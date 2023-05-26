import modal
stub = modal.Stub("hello-numpy")

@stub.function()
def square(x):
    import numpy
    print("this is numpy code")
    print(numpy.ones([5,5]))
    return x**2

@stub.local_entrypoint()
def main():
    print("square is", square.call(7))