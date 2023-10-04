from modal import Stub, Mount, Image, Function
import sys
sys.path.append('../run_model')

from run_model.vol import InvokeArgs

stub = Stub('hello-sandbox')
image = Image.debian_slim()

@stub.function(image=image)
def hello():
    f = Function.lookup("model-volume","invoke")
    
    f.spawn(InvokeArgs(repo_name="TheBloke/WizardLM-Uncensored-Falcon-7B-GGML", file_name="wizardlm-7b-uncensored.ggccv1.q4_1.bin", prompt="Write some python code to print hello", model_type="falcon"))
    #TODO use callback


@stub.function(image=image)
def hello_callback(code: str):
    #TODO lvl2
    with open("hello_lvl1.py", 'w') as f:
        f.write(code)

    sb = stub.spawn_sandbox(
        "python", "/repo/hello_lvl1.py",
        image=image,
        mounts=[Mount.from_local_file(local_path="./hello_lvl1.py", remote_path="/repo/hello_lvl1.py")],
        timeout=60,
    )
    # Would be better to exit and find results from a volume later
    sb.wait()

    if sb.returncode != 0:
        print(f"Tests failed with code {sb.returncode}")
        print(sb.stderr.read())