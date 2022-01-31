export NOTION_TOKEN_V2=$(cat /notion_token.txt)
gunicorn -c gunicorn.ini.py apps.app:app
