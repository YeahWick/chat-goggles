from modal import Stub, Image, Volume, Function, Queue, method
import ftypes

stub = Stub('datasets')
stub.volume = Volume.persisted("datasets")
stub.queue = Queue.from_name("invoke-queue")

vol_mnt = "/datasets"

image = Image.debian_slim().pip_install(["datasets"])

@stub.function(image=image, volumes={vol_mnt: stub.volume})
def fetch_data(dataset_repo, dataset_name):
    from datasets import load_dataset
    huggingface_dataset = load_dataset(dataset_repo, dataset_name, cache_dir = f"{vol_mnt}/")
    def data_generator():
        for example in huggingface_dataset['train']:
            yield example
    return data_generator

@stub.function(image=image, volumes={vol_mnt: stub.volume})
def put_queue(data_gen): #TODO add type
    #TODO fix error
    # No module named 'datasets'
    # This can happen if your local environment does not have a module that was used to construct the result. 
    for item in data_gen():
        print(item)
        break

@stub.local_entrypoint()
def main():
    gen = fetch_data.remote("tasksource/bigbench", "abstract_narrative_understanding")
    put_queue.remote(gen)