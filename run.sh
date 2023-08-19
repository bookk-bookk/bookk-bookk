# !/bin/bash
cd apps & gunicorn -c gunicorn.init.py app:app
