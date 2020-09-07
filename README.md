# bookk-bookk [![bookk-bookk](https://circleci.com/gh/bookk-bookk/bookk-bookk.svg?style=svg)](https://app.circleci.com/pipelines/github/bookk-bookk)


### Repository setup guide
1. [`pyenv`](https://github.com/pyenv/pyenv)와 [`pyenv-virtualenv`](https://github.com/pyenv/pyenv-virtualenv)를 설치하세요.
2. 파이썬 가상환경을 만드세요.
```
$ pyenv install 3.8.0
$ pyenv virtualenv 3.8.0 bookk-bookk
$ pyenv activate bookk-bookk
```
3. pip 패키지를 설치하세요.
```
$ pip install -r requirements/local.txt
```

4. git hook을 설정하세요.
```
$ pre-commit install
$ pre-commit install -t prepare-commit-msg
```

5. gunicorn을 실행하세요.
```
$ gunicorn -c gunicorn.ini app:app
```
