import brownie, pytest
from scripts.josh.bbenv import bbenv as je_bbenv
from scripts.boris.bbenv import bbenv as b_bbenv

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    print("isolated")
    #pass

@pytest.fixture(scope='function')
def je_org():
    return je_bbenv()

@pytest.fixture(scope='function')
def b_org():
    return b_bbenv()
