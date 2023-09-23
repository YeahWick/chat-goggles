from modal import Stub, Image, Function

def download_model():
    from ctransformers import AutoModelForCausalLM

    # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
    llm = AutoModelForCausalLM.from_pretrained("TheBloke/robin-7B-v2-GGML", model_file="robin-7b.ggmlv3.q4_1.bin", model_type="llama")# , gpu_layers=50)

stub = Stub('robin')
image = Image.debian_slim().pip_install("ctransformers").run_function(download_model)

@stub.function(image=image)
def entry_function():
    from ctransformers import AutoModelForCausalLM
    llm = AutoModelForCausalLM.from_pretrained("TheBloke/robin-7B-v2-GGML", model_file="robin-7b.ggmlv3.q4_1.bin", model_type="llama", local_files_only=True)# , gpu_layers=50)
    print(llm("A bash function to change a aws ec2 tag:"))