import brownie, pytest
from scripts.josh.bbenv import bbenv

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

@pytest.fixture(scope='function')
def org():
    return bbenv()
