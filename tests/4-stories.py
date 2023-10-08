from modal import Stub, Mount, Image, Function
import sys
sys.path.append('../run_model')

from run_model.invoke import InvokeArgs

stub = Stub('3-compare')
image = Image.debian_slim()

@stub.function(image=image)
def hello():
    f = Function.lookup("invoke","invoke")

    instruction="# Python3 code that will make a request to http://slashdot.org and find headlines from html"
    prompt=f"{instruction}"
    
    # Passing hello_callback directly doesn't appear to work, need to use Function lookup.
    f.spawn(InvokeArgs(
        repo_name="TheBloke/CodeLlama-7B-GGUF",
        file_name="codellama-7b.Q4_K_M.gguf",
        prompt=f"{prompt}",
        model_type="llama",
        context_length=1024),
        callback=Function.lookup("code-sandbox","code_callback"))