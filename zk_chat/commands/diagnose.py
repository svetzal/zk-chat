"""
Diagnose subcommand for zk-chat.

Provides diagnostic information about the index and search system.
"""
import logging
import os

# Set log levels early to prevent chatty output
logging.basicConfig(level=logging.WARN)

# Disable ChromaDB telemetry to avoid PostHog compatibility issues
os.environ['CHROMA_TELEMETRY'] = 'false'

import typer
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from mojentic.llm.gateways import OllamaGateway, OpenAIGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config, ModelGateway
from zk_chat.global_config import GlobalConfig
from zk_chat.vector_database import VectorDatabase
from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.zettelkasten import Zettelkasten

diagnose_app = typer.Typer(
    name="diagnose",
    help="🔬 Diagnose index and search issues",
    rich_markup_mode="rich"
)

console = Console()


@diagnose_app.command()
def index(
    vault: Annotated[Optional[Path], typer.Option("--vault", "-v", help="Path to your Zettelkasten vault")] = None,
    query: Annotated[Optional[str], typer.Option("--query", "-q", help="Test query to run")] = None,
):
    """
    Diagnose the search index to identify why queries aren't returning results.

    [bold]Checks performed:[/]

    • Collection existence and counts
    • Sample documents in each collection
    • Test query results (if --query provided)
    • Embedding generation test

    [bold]Examples:[/]

    • [cyan]zk-chat diagnose index[/] - Basic diagnostics
    • [cyan]zk-chat diagnose index --query "test"[/] - Run test query
    • [cyan]zk-chat diagnose index --vault ~/notes[/] - Diagnose specific vault
    """
    # Determine vault path
    if vault:
        vault_path = str(vault.resolve())
    else:
        global_config = GlobalConfig.load()
        vault_path = global_config.get_last_opened_bookmark_path()
        if not vault_path:
            console.print("[red]❌ Error:[/] No vault specified and no bookmarks found.")
            console.print("[yellow]Use:[/] [cyan]zk-chat diagnose index --vault /path/to/vault[/]")
            raise typer.Exit(1)

    if not os.path.exists(vault_path):
        console.print(f"[red]❌ Error:[/] Vault path '{vault_path}' does not exist.")
        raise typer.Exit(1)

    # Load config
    config = Config.load(vault_path)
    if not config:
        console.print("[yellow]⚠️  Warning:[/] No zk-chat configuration found in vault.")
        console.print(f"[dim]Run [cyan]zk-chat interactive --vault {vault_path}[/dim] to initialize.")
        raise typer.Exit(1)

    console.print(Panel(f"[bold cyan]Index Diagnostics[/] - {vault_path}", expand=False))

    # Set up gateway and databases
    db_dir = os.path.join(config.vault, ".zk_chat_db")

    if not os.path.exists(db_dir):
        console.print("\n[red]❌ Database directory does not exist![/]")
        console.print(f"[dim]Expected: {db_dir}[/]")
        console.print("\n[yellow]Run:[/] [cyan]zk-chat index update[/] to create the index")
        raise typer.Exit(1)

    chroma = ChromaGateway(config.gateway, db_dir=db_dir)

    # Create the appropriate gateway based on configuration
    if config.gateway == ModelGateway.OLLAMA:
        gateway = OllamaGateway()
    elif config.gateway == ModelGateway.OPENAI:
        gateway = OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
    else:
        gateway = OllamaGateway()

    # Check collections
    console.print("\n[bold]1. Collection Status[/]")
    collections_table = Table(title="ChromaDB Collections")
    collections_table.add_column("Collection", style="cyan")
    collections_table.add_column("Documents", justify="right", style="green")
    collections_table.add_column("Status", style="yellow")

    for collection_name in [ZkCollectionName.DOCUMENTS, ZkCollectionName.EXCERPTS]:
        try:
            collection = chroma.get_collection(collection_name)
            count = collection.count()
            status = "✓ OK" if count > 0 else "⚠ Empty"
            collections_table.add_row(collection_name.value, str(count), status)
        except Exception as e:
            collections_table.add_row(collection_name.value, "N/A", f"✗ Error: {e}")

    console.print(collections_table)

    # Sample documents from each collection
    console.print("\n[bold]2. Sample Documents[/]")
    for collection_name in [ZkCollectionName.DOCUMENTS, ZkCollectionName.EXCERPTS]:
        try:
            collection = chroma.get_collection(collection_name)
            count = collection.count()

            if count > 0:
                # Get a few sample documents
                results = collection.get(limit=3, include=['metadatas', 'documents'])

                console.print(f"\n[cyan]{collection_name.value}[/] (showing {min(3, count)} of {count}):")
                for i, (doc_id, metadata, document) in enumerate(
                    zip(results['ids'], results['metadatas'], results['documents'])
                ):
                    console.print(f"  [{i+1}] ID: {doc_id[:50]}...")
                    console.print(f"      Title: {metadata.get('title', 'N/A')}")
                    console.print(f"      Content: {document[:100]}...")
            else:
                console.print(f"\n[yellow]{collection_name.value}:[/] No documents")
        except Exception as e:
            console.print(f"\n[red]{collection_name.value}:[/] Error: {e}")

    # Test embedding generation
    console.print("\n[bold]3. Embedding Generation Test[/]")
    test_text = "This is a test document"
    try:
        embedding = gateway.calculate_embeddings(test_text)
        console.print(f"  ✓ Generated embedding with {len(embedding)} dimensions")
        console.print(f"  Sample values: [{embedding[0]:.4f}, {embedding[1]:.4f}, {embedding[2]:.4f}, ...]")
    except Exception as e:
        console.print(f"  [red]✗ Failed to generate embedding:[/] {e}")

    # Test query if provided
    doc_results = []
    excerpt_results = []
    if query:
        console.print(f"\n[bold]4. Test Query:[/] '{query}'")

        try:
            # Set up full Zettelkasten
            zk = Zettelkasten(
                tokenizer_gateway=TokenizerGateway(),
                excerpts_db=VectorDatabase(
                    chroma_gateway=chroma,
                    gateway=gateway,
                    collection_name=ZkCollectionName.EXCERPTS
                ),
                documents_db=VectorDatabase(
                    chroma_gateway=chroma,
                    gateway=gateway,
                    collection_name=ZkCollectionName.DOCUMENTS
                ),
                filesystem_gateway=MarkdownFilesystemGateway(config.vault)
            )

            # Query documents
            console.print("\n  [cyan]Documents query:[/]")
            doc_results = zk.query_documents(query, n_results=3)
            if doc_results:
                for i, result in enumerate(doc_results):
                    console.print(f"    [{i+1}] {result.document.title} (distance: {result.distance:.4f})")
                    console.print(f"        {result.document.content[:100]}...")
            else:
                console.print("    [yellow]No results[/]")

            # Query excerpts
            console.print("\n  [cyan]Excerpts query:[/]")
            excerpt_results = zk.query_excerpts(query, n_results=5, max_distance=1.0)
            if excerpt_results:
                for i, result in enumerate(excerpt_results):
                    console.print(f"    [{i+1}] {result.excerpt.document_title} (distance: {result.distance:.4f})")
                    console.print(f"        {result.excerpt.text[:100]}...")
            else:
                console.print("    [yellow]No results[/]")

        except Exception as e:
            console.print(f"  [red]✗ Query failed:[/] {e}")
            import traceback
            console.print(f"  [dim]{traceback.format_exc()}[/]")

    # Summary and recommendations
    console.print("\n[bold]Recommendations:[/]")

    # Check if both collections have data
    try:
        doc_collection = chroma.get_collection(ZkCollectionName.DOCUMENTS)
        excerpt_collection = chroma.get_collection(ZkCollectionName.EXCERPTS)
        doc_count = doc_collection.count()
        excerpt_count = excerpt_collection.count()

        if doc_count == 0 and excerpt_count == 0:
            console.print("  [red]•[/] Both collections are empty - run [cyan]zk-chat index update --full[/]")
        elif doc_count == 0:
            console.print("  [yellow]•[/] Documents collection is empty - run [cyan]zk-chat index update --full[/]")
        elif excerpt_count == 0:
            console.print("  [yellow]•[/] Excerpts collection is empty - run [cyan]zk-chat index update --full[/]")
        else:
            console.print("  [green]•[/] Collections have data")

            if query and not doc_results and not excerpt_results:
                console.print("  [yellow]•[/] Query returned no results - this may be a distance threshold issue")
                console.print("    Try a different query or check if your model is working correctly")
    except Exception as e:
        console.print(f"  [red]•[/] Error checking collections: {e}")
