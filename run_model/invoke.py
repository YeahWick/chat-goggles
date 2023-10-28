from modal import Stub, Image, Volume, Function, Queue, method
from ftypes import DownloadArgs, InvokeArgs

stub = Stub('invoke')
stub.volume = Volume.persisted("models")
stub.queue = Queue.persisted("invoke-queue")

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

@stub.cls(image=image, volumes={vol_mnt: stub.volume}, timeout=1800)
class RunQueue():
    def __enter__(self):
        from llama_cpp import Llama
        import os
        # TODO fix how this gets which model, right now
        # it just assumes all models within the queue are the same.
        if (stub.queue.len() > 0):
            args = stub.queue.get()
            stub.volume.reload()
            file_path = f"{vol_mnt}/{args.repo_name_dir}/{args.file_name}"
            if not os.path.isfile(file_path):
                download.remote(DownloadArgs(repo_name=args.repo_name, file_name=args.file_name))
                stub.volume.reload()
            self.llm = Llama(f"{vol_mnt}/{args.repo_name_dir}/{args.file_name}")
            output = self.llm(args.prompt, max_tokens=max_tokens)
            print(output) #TODO move this. Needs an invoke fn

    @method()
    def run_queue(self):
        while (stub.queue.len() > 0):
            args = stub.queue.get()

            output = self.llm(args.prompt, max_tokens=max_tokens)

            #TODO consider callback
            callback = None
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

