from modal import Stub, Image, Function

def download_model():
    from ctransformers import AutoModelForCausalLM

    # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
    llm = AutoModelForCausalLM.from_pretrained("TheBloke/Xwin-LM-13B-V0.1-GGUF", model_file="xwin-lm-13b-v0.1.Q4_K_M.gguf", model_type="llama")# , gpu_layers=50)

stub = Stub('xwin_lm')
image = Image.debian_slim().pip_install("ctransformers").run_function(download_model)

@stub.function(image=image)
def entry_function():
    from ctransformers import AutoModelForCausalLM
    llm = AutoModelForCausalLM.from_pretrained("TheBloke/Xwin-LM-13B-V0.1-GGUF", model_file="xwin-lm-13b-v0.1.Q4_K_M.gguf", model_type="llama", local_files_only=True)# , gpu_layers=50)
    print(llm("Here is a bash function that will change a aws ec2 tag", max_new_tokens=400))