from modal import Stub, Mount, Image

stub = Stub('hello-sandbox')
image = Image.debian_slim()

@stub.function(image=image)
def hello():
    with open("hello_lvl1.py", 'w') as f:
        f.write("print(\"hello\")")

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