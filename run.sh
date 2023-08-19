# !/bin/bash
cd apps
gunicorn -c gunicorn.ini.py app:app
