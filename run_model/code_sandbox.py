from modal import Stub, Mount, Image, Function
import hashlib

stub = Stub("code-sandbox")
image = Image.debian_slim()

@stub.function(image=image)
def code_callback(code: str):
    code_sha = hashlib.sha1(code.encode()).hexdigest()
    filename = f"{code_sha}.py"

    print("\n\nhere\n")
    print(code)
    print("\n\nhere3\n")
    print(code)
    print("\nhere4\n")

    with open(filename, 'w') as f:
        f.write(code)

    sb = stub.spawn_sandbox(
        "python", f"/repo/{filename}",
        image=image,
        mounts=[Mount.from_local_file(local_path=f"./{filename}", remote_path=f"/repo/{filename}")],
        timeout=60,
    )
    sb.wait()

    if sb.returncode != 0:
        print(f"Tests failed with code {sb.returncode}")
        print(sb.stderr.read())
    else:
        print(sb.stdout.read())