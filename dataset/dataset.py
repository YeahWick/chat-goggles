from modal import Stub, Image, Volume, Function, Queue, method

stub = Stub('datasets')
stub.volume = Volume.persisted("datasets")

vol_mnt = "/datasets"

image = Image.debian_slim().pip_install(["datasets"])

@stub.function(image=image, volumes={vol_mnt: stub.volume})
def fetch_data(dataset):
    from datasets import load_dataset
    #TODO mkdir
    huggingface_dataset = load_dataset(dataset_repo, dataset_name, cache_dir = f"{vol_mnt}/{dataset_repo}")
    def data_generator():
        for example in huggingface_dataset['train']:
            yield example
    return data_generator

@stub.local_entrypoint()
def main():
    gen = fetch_data("tasksource/bigbench", "abstract_narrative_understanding")
    for item in gen():
        print(item)
        break