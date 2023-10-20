from modal import Stub, Image, Volume, Function, Mount
from dataclasses import dataclass

# Define NamedTuple classes for download and invoke arguments
@dataclass
class DownloadArgs():
    repo_name: str
    file_name: str

    def __post_init__(self):
        self.repo_name_dir = self.repo_name.replace("/", "-")

@dataclass
class InvokeArgs():
    repo_name: str
    file_name: str
    prompt: str
    model_type: str
    context_length: int = 512

    def __post_init__(self):
        self.repo_name_dir = self.repo_name.replace("/", "-")

stub = Stub('invoke')
stub.volume = Volume.persisted("models")

vol_mnt = "/models"
max_tokens = 350

image = Image.debian_slim().env(dict(CMAKE_ARGS="-DLLAMA_CUBLAS=on")).pip_install(["huggingface_hub", "llama-cpp-python"])

@stub.function(image=image, volumes={vol_mnt: stub.volume})
def download(args: DownloadArgs):
    from huggingface_hub import hf_hub_download
    import os, shutil

    target_dir = f"{vol_mnt}/{args.repo_name_dir}"
    os.makedirs(target_dir, exist_ok=True)

    downloads_dir = "/model_downloads"
    os.mkdir(downloads_dir)
    model_file = hf_hub_download(repo_id=args.repo_name, filename=args.file_name, cache_dir=downloads_dir)

    shutil.copy(model_file, target_dir)
    stub.volume.commit()

@stub.function(image=image, volumes={vol_mnt: stub.volume}, timeout=1800)
def invoke(args: InvokeArgs, callback: Function):
    from llama_cpp import Llama
    import os

    stub.volume.reload()
    file_path = f"{vol_mnt}/{args.repo_name_dir}/{args.file_name}"
    if not os.path.isfile(file_path):
        download.remote(DownloadArgs(repo_name=args.repo_name, file_name=args.file_name))
        stub.volume.reload()

    llm = Llama(f"{vol_mnt}/{args.repo_name_dir}/{args.file_name}")
    output = llm(args.prompt, max_tokens=max_tokens)
    if callback is None:
        print(output)
    else:
        callback.spawn(output["choices"][0]["text"])


@stub.function(image=image, volumes={vol_mnt: stub.volume})
def list_files():
    import os
    stub.volume.reload()
    print(f"{vol_mnt}")
    def traverse_directory(directory):
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                print(f"{directory}/{item} {size}")
            elif os.path.isdir(path):
                traverse_directory(path)

    traverse_directory(vol_mnt)

@stub.local_entrypoint()
def main(repo_name: str, file_name: str, prompt: str, model_type: str, context_length: int = 512):
    invoke.remote(InvokeArgs(repo_name, file_name, prompt, model_type, context_length), None)