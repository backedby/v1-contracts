#from brownie import reverts
#from scripts.bbenv import bbenv
from scripts.josh.helpers import helpers, objdict

class SnapshotBalances:
    def __init__(self, accounts, currencies):
        self._accounts = accounts
        self._currencies = currencies
        self.starting = objdict({})
        self.ending = objdict({})
        self.starting = self._snap(self._accounts, self._currencies)

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.ending = self._snap(self._accounts, self._currencies)

    def _snap(self, accounts, currencies):
        rtn = objdict({})
        for account in accounts:
            rtn[account.address] = objdict()
            for currency in currencies:
                rtn[account.address][currency.address] = currency.balanceOf(account.address)
        return rtn

    def diff(self, account, currency):
        return self.starting[account.address][currency.address] - self.ending[account.address][currency.address]