from modal import Stub, Image, Function, gpu

model_name="TheBloke/falcon-40b-sft-top1-560-GGML"
model_file="falcon-40b-top1-560.ggccv1.q4_1.bin"

def download_model():
    from ctransformers import AutoModelForCausalLM

    # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
    llm = AutoModelForCausalLM.from_pretrained(model_name, model_file=model_file, model_type="falcon")# , gpu_layers=50)

stub = Stub('falcon_40b')
image = Image.debian_slim().pip_install("ctransformers").run_function(download_model).pip_install("ctransformers[cuda]") #TODO move to 1 pip install for ctransforms, just saving time on a rebuild for now

@stub.function(image=image,gpu="t4")
def entry_function():
    from ctransformers import AutoModelForCausalLM
    llm = AutoModelForCausalLM.from_pretrained(model_name, model_file=model_file, model_type="falcon", gpu_layers=40, local_files_only=True)# , gpu_layers=50)
    print(llm("What is the carry capacity of a full laden swallow?", max_new_tokens=400))