from ftypes import InvokeArgs
from modal import Function
import click

invoke_f = Function.lookup("invoke","invoke")

@click.group()
def cli():
    pass

@click.command()
@click.option("--repo-name", "repo_name", prompt="Enter repo name", help="Name of the repository")
@click.option("--file-name", "file_name", prompt="Enter file name", help="Name of the file")
@click.option("--prompt", prompt="Enter prompt", help="Prompt for the model")
@click.option("--model-type", "model_type", prompt="Enter model type", help="Type of the model")
@click.option("--context-length", "context_length", default=512, type=int, help="Length of the context")
def invoke(repo_name: str, file_name: str, prompt: str, model_type: str, context_length: int = 512):
    invoke_f.remote(InvokeArgs(repo_name, file_name, prompt, model_type, context_length), None)

@click.command()
def select():
    # Your logic for the "select" subcommand goes here
    pass

cli.add_command(invoke)
cli.add_command(select)

if __name__ == "__main__":
    cli()