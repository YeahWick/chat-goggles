from modal import Stub, Volume

stub = Stub('volume-test')
stub.volume = Volume.persisted("models-test1")

@stub.function(volumes={"/models": stub.volume})
def f():
    with open("/models/bar.txt", "w") as f:
        f.write("hello")
    stub.volume.commit()  # Persist changes

@stub.function(volumes={"/models": stub.volume})
def g():
    stub.volume.reload()  # Fetch latest changes
    with open("/models/bar.txt", "r") as f:
        print(f.read())