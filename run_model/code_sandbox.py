from modal import Stub, Mount, Image, Function

stub = Stub("code-sandbox")
image = Image.debian_slim()

@stub.function(image=image)
def code_callback(code: str):
    with open("code.py", 'w') as f:
        f.write(code)

    sb = stub.spawn_sandbox(
        "python", "/repo/code.py",
        image=image,
        mounts=[Mount.from_local_file(local_path="./code.py", remote_path="/repo/code.py")],
        timeout=60,
    )
    sb.wait()

    if sb.returncode != 0:
        print(f"Tests failed with code {sb.returncode}")
        print(sb.stderr.read())
    else:
        print(sb.stdout.read())