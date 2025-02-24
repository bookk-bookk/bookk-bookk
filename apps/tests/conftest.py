"""
https://docs.pytest.org/en/stable/how-to/writing_plugins.html
Requiring plugins using pytest_plugins variable in non-root conftest.py files is deprecated.
-> import 하는 것으로 대체
"""
from tests.fixtures import *  # noqa: F401,F403
