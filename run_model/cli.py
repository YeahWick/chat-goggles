from ftypes import InvokeArgs
from modal import Function, Queue, Cls
import click

@click.group()
def cli():
    pass

@cli.command()
@click.option("--repo-name", "repo_name", prompt="Enter repo name", help="Name of the repository")
@click.option("--file-name", "file_name", prompt="Enter file name", help="Name of the file")
@click.option("--prompt", prompt="Enter prompt", help="Prompt for the model")
@click.option("--model-type", "model_type", prompt="Enter model type", help="Type of the model")
@click.option("--context-length", "context_length", default=512, type=int, help="Length of the context")
def invoke(repo_name: str, file_name: str, prompt: str, model_type: str, context_length: int = 512):
    invoke_f = Function.lookup("invoke","invoke")
    invoke_f.remote(InvokeArgs(repo_name, file_name, prompt, model_type, context_length), None)

@cli.command()
def list_files():
    invoke_ls = Function.lookup("invoke","list_files")
    print(invoke_ls.remote())

@cli.command()
@click.option("--repo-name", "repo_name", prompt="Enter repo name", help="Name of the repository")
@click.option("--file-name", "file_name", prompt="Enter file name", help="Name of the file")
@click.option("--prompt", prompt="Enter prompt", help="Prompt for the model")
@click.option("--model-type", "model_type", prompt="Enter model type", help="Type of the model")
@click.option("--context-length", "context_length", default=512, type=int, help="Length of the context")
def queue(repo_name: str, file_name: str, prompt: str, model_type: str, context_length: int = 512):
    queue_q = Queue.lookup("invoke-queue")
    queue_q.put(InvokeArgs(repo_name, file_name, prompt, model_type, context_length))

@cli.command()
def run_queue():
    queue_r = Cls.lookup("invoke","RunQueue")
    qr = queue_r()
    qr.run_queue.remote()

if __name__ == "__main__":
    cli()