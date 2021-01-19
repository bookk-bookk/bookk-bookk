def generate():
    print("start coroutine")
    x = yield
    print("resume coroutine: ", x)
    return


co = generate()
print("co: ", co, end="\n\n")
next(co)
print("suspend coroutine", end="\n\n")
co.send(42)
