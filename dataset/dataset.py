from datasets import load_dataset

# https://huggingface.co/datasets/tasksource/bigbench
# abstract_narrative_understanding
def fetch_huggingface_data(dataset):
    huggingface_dataset = load_dataset(dataset)
    def data_generator():
        for example in huggingface_dataset['train']:
            yield example
    return data_generator

# Running the function for "squad" dataset
gen = fetch_huggingface_data('squad')
for item in gen():
    print(item)
    break