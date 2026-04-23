"""
Diagnose subcommand for zk-chat.

Provides diagnostic information about the index and search system.
"""

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports
from zk_chat.config_gateway import ConfigGateway
from zk_chat.gateway_defaults import (
    create_default_chroma_gateway,
    create_default_config_gateway,
    create_default_console_gateway,
    create_default_filesystem_gateway,
    create_default_git_gateway,
    create_default_global_config_gateway,
    create_default_model_gateway,
    create_default_tokenizer_gateway,
)
from zk_chat.service_factory import build_service_registry
from zk_chat.services.diagnostic_service import (
    CollectionSamples,
    CollectionStatus,
    DiagnosticService,
    EmbeddingTestResult,
)
from zk_chat.services.service_provider import ServiceProvider
from zk_chat.vault_resolution import VaultResolutionError, resolve_vault_path

diagnose_app = typer.Typer(name="diagnose", help="🔬 Diagnose index and search issues", rich_markup_mode="rich")

console = Console()


def _load_config(vault_path: str, config_gateway: ConfigGateway):
    config = config_gateway.load(vault_path)
    if not config:
        console.print("[yellow]⚠️  Warning:[/] No zk-chat configuration found in vault.")
        console.print(f"[dim]Run [cyan]zk-chat interactive --vault {vault_path}[/dim] to initialize.")
        raise typer.Exit(1)
    return config


def _print_collection_status(statuses: list[CollectionStatus]) -> None:
    console.print("\n[bold]1. Collection Status[/]")
    table = Table(title="ChromaDB Collections")
    table.add_column("Collection", style="cyan")
    table.add_column("Documents", justify="right", style="green")
    table.add_column("Status", style="yellow")
    for status in statuses:
        count_str = str(status.count) if status.count is not None else "N/A"
        table.add_row(status.name, count_str, status.status)
    console.print(table)


def _print_samples(samples: list[CollectionSamples]) -> None:
    console.print("\n[bold]2. Sample Documents[/]")
    for sample in samples:
        if sample.total_count > 0:
            console.print(
                f"\n[cyan]{sample.collection_name}[/] (showing {len(sample.entries)} of {sample.total_count}):"
            )
            for i, entry in enumerate(sample.entries):
                console.print(f"  [{i + 1}] ID: {entry.id[:50]}...")
                console.print(f"      Title: {entry.title}")
                console.print(f"      Content: {entry.content_preview}...")
        else:
            console.print(f"\n[yellow]{sample.collection_name}:[/] No documents")


def _print_embedding_result(result: EmbeddingTestResult) -> None:
    console.print("\n[bold]3. Embedding Generation Test[/]")
    if result.success:
        console.print(f"  ✓ Generated embedding with {result.dimensions} dimensions")
        if result.sample_values:
            vals = ", ".join(f"{v:.4f}" for v in result.sample_values)
            console.print(f"  Sample values: [{vals}, ...]")
    else:
        console.print(f"  [red]✗ Failed to generate embedding:[/] {result.error}")


def _run_test_query(query: str, provider: ServiceProvider) -> tuple[list, list]:
    console.print(f"\n[bold]4. Test Query:[/] '{query}'")
    doc_results: list = []
    excerpt_results: list = []
    try:
        index_service = provider.get_index_service()
        console.print("\n  [cyan]Documents query:[/]")
        doc_results = index_service.query_documents(query, n_results=3)
        if doc_results:
            for i, result in enumerate(doc_results):
                console.print(f"    [{i + 1}] {result.document.title} (distance: {result.distance:.4f})")
                console.print(f"        {result.document.content[:100]}...")
        else:
            console.print("    [yellow]No results[/]")
        console.print("\n  [cyan]Excerpts query:[/]")
        excerpt_results = index_service.query_excerpts(query, n_results=5, max_distance=1.0)
        if excerpt_results:
            for i, result in enumerate(excerpt_results):
                console.print(f"    [{i + 1}] {result.excerpt.document_title} (distance: {result.distance:.4f})")
                console.print(f"        {result.excerpt.text[:100]}...")
        else:
            console.print("    [yellow]No results[/]")
    except (ConnectionError, OSError, ValueError) as e:
        console.print(f"  [red]✗ Query failed:[/] {e}")
        import traceback

        console.print(f"  [dim]{traceback.format_exc()}[/]")
    return doc_results, excerpt_results


def _print_recommendations(
    diagnostic_service: DiagnosticService, query: str | None, doc_results: list, excerpt_results: list
) -> None:
    from zk_chat.diagnostics import generate_recommendations

    _SEVERITY_COLOR = {"error": "red", "warning": "yellow", "ok": "green"}

    console.print("\n[bold]Recommendations:[/]")
    try:
        statuses = diagnostic_service.get_collection_statuses()
        counts = {s.name: s.count for s in statuses}
        doc_count = counts.get("documents", 0) or 0
        excerpt_count = counts.get("excerpts", 0) or 0
        for rec in generate_recommendations(doc_count, excerpt_count, query, doc_results, excerpt_results):
            color = _SEVERITY_COLOR.get(rec.severity, "white")
            console.print(f"  [{color}]•[/] {rec.message}")
            if rec.detail:
                console.print(f"    {rec.detail}")
    except (ValueError, OSError) as e:
        console.print(f"  [red]•[/] Error checking collections: {e}")


@diagnose_app.command()
def index(
    vault: Annotated[Path | None, typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
    query: Annotated[str | None, typer.Option("--query", "-q", help="Test query to run")] = None,
) -> None:
    """Diagnose the search index to identify why queries aren't returning results."""
    global_config_gateway = create_default_global_config_gateway()
    config_gateway = create_default_config_gateway()

    try:
        vault_path = resolve_vault_path(vault, global_config_gateway)
    except VaultResolutionError as e:
        console.print(f"[red]❌ Error:[/] {e}")
        console.print("[yellow]Use:[/] [cyan]zk-chat diagnose index --vault /path/to/vault[/]")
        raise typer.Exit(1) from e

    config = _load_config(vault_path, config_gateway)
    console.print(Panel(f"[bold cyan]Index Diagnostics[/] - {vault_path}", expand=False))
    db_dir = os.path.join(config.vault, ".zk_chat_db")
    if not os.path.exists(db_dir):
        console.print("\n[red]❌ Database directory does not exist![/]")
        console.print(f"[dim]Expected: {db_dir}[/]")
        console.print("\n[yellow]Run:[/] [cyan]zk-chat index update[/] to create the index")
        raise typer.Exit(1)

    registry = build_service_registry(
        config=config,
        config_gateway=config_gateway,
        global_config_gateway=global_config_gateway,
        model_gateway=create_default_model_gateway(config.gateway),
        chroma_gateway=create_default_chroma_gateway(config),
        filesystem_gateway=create_default_filesystem_gateway(config.vault),
        tokenizer_gateway=create_default_tokenizer_gateway(),
        git_gateway=create_default_git_gateway(config.vault),
        console_service=create_default_console_gateway(),
    )
    provider = ServiceProvider(registry)
    diagnostic_service = provider.get_diagnostic_service()
    model_gateway = provider.get_model_gateway()

    _print_collection_status(diagnostic_service.get_collection_statuses())
    _print_samples(diagnostic_service.get_sample_documents())
    _print_embedding_result(diagnostic_service.test_embedding(model_gateway))

    doc_results: list = []
    excerpt_results: list = []
    if query:
        doc_results, excerpt_results = _run_test_query(query, provider)
    _print_recommendations(diagnostic_service, query, doc_results, excerpt_results)
