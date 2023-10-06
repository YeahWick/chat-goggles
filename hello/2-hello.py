from modal import Stub, Mount, Image, Function
import sys
sys.path.append('../run_model')

from run_model.vol import InvokeArgs

stub = Stub('2-hello-sandbox')
image = Image.debian_slim()

@stub.function(image=image)
def hello():
    f = Function.lookup("model-volume","invoke")

    instruction="write some python code that prints hello"
    prompt=f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n### Instruction:\n{instruction}\n\n### Response:"
    
    # Passing hello_callback directly doesn't appear to work, need to use Function lookup.
    f.spawn(InvokeArgs(repo_name="TheBloke/WizardCoder-Python-13B-V1.0-GGUF", file_name="wizardcoder-python-13b-v1.0.Q5_K_M.gguf", prompt=f"{prompt}", model_type="llama"), callback=Function.lookup("2-hello-sandbox","hello_callback"))

#This needs to be deployed to modal to be callable. It should be moved to its own app
@stub.function(image=image)
def hello_callback(code: str):
    #TODO lvl2
    with open("hello_lvl2.py", 'w') as f:
        f.write(code)

    sb = stub.spawn_sandbox(
        "python", "/repo/hello_lvl2.py",
        image=image,
        mounts=[Mount.from_local_file(local_path="./hello_lvl2.py", remote_path="/repo/hello_lvl2.py")],
        timeout=60,
    )
    sb.wait()

    if sb.returncode != 0:
        print(f"Tests failed with code {sb.returncode}")
        print(sb.stderr.read())
    else:
        print(sb.stdout.read())