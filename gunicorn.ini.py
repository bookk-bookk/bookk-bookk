import os

workers = 4
worker_class = "uvicorn.workers.UvicornH11Worker"
bind = "0.0.0.0:{}".format(os.getenv("PORT"))
