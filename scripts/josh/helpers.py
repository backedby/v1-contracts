import string
from brownie.network import state
from random import choices as randomChoices
chain = state.Chain()

class helpers:
    MAXUINT256 = int("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16)
    def advance_time(days):
        chain.sleep(days*86400)
        chain.mine()
    def by(account, values={}):
        try:
            return values | {'from':account}
        except:
            return {**values, 'from': account}

    def randomCid():
        return ''.join(randomChoices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k= 16))

    def balanceSnapshot(accounts, currency):
        d = []
        for i, account in accounts:
            d[i] = currency.balanceOf(account.address)
        return d

class objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)