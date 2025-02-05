import os

homedir = os.environ['HOME']
vault_path = f"Documents/ToyVault"
vault_root = f"{homedir}/{vault_path}"
# vault_root = f"{homedir}/Documents/HostedVault"
# ollama_model = 'llama3.1-instruct-8b-32k'
# ollama_model = 'llama3.3-instruct-70b-32k'
ollama_model = 'deepseek-r1:70b'
