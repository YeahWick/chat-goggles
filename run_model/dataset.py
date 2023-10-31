from modal import Stub, Image, Volume, Function, Queue, method
import ftypes

stub = Stub('datasets')
stub.volume = Volume.persisted("datasets")
stub.queue = Queue.from_name("invoke-queue")

vol_mnt = "/datasets"

image = Image.debian_slim().pip_install(["datasets"])

class DataIterator(object):
    from datasets import Dataset

    def __init__(self, rdataset: Dataset):
        self.rdataset = rdataset
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.rdataset):
            raise StopIteration
        else:
            data = self.rdataset[self.index]
            self.index += 1
            return data

def fetch_data(dataset_repo, dataset_name, split):
    from datasets import load_dataset, DownloadConfig
    stub.volume.reload()
    load_dataset(dataset_repo, dataset_name, cache_dir = f"{vol_mnt}/", download_config=DownloadConfig(cache_dir=f"{vol_mnt}/downloads/"))
    stub.volume.commit()
    huggingface_dataset = load_dataset(dataset_repo, dataset_name, cache_dir = f"{vol_mnt}/", download_config=DownloadConfig(cache_dir=f"{vol_mnt}/downloads/"))
    return DataIterator(huggingface_dataset[split])

@stub.function(image=image, volumes={vol_mnt: stub.volume})
def put_queue(dataset_repo, dataset_name):
    data_it = fetch_data(dataset_repo, dataset_name,"train")
    for item in data_it:
        print(item)
        break

@stub.local_entrypoint()
def main():
    put_queue.remote("tasksource/bigbench", "abstract_narrative_understanding")