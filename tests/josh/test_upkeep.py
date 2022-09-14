from brownie import reverts
from scripts.josh.bbenv import bbenv
from scripts.josh.helpers import helpers
from eth_abi import encode, decode

def test_checkUpkeep(je_org):
    runner = bbenv.anons[4]
    sub1 = je_org.setup_subscription()
    sub2 = je_org.setup_subscription()

    currency = sub1._in.currency

    helpers.advance_time(31)
    checkUpkeepPayload = "0x" + encode( ['uint256','uint256', 'uint256','address'], [0, 100, 25, runner.address] ).hex()
    checkUpkeepDataRaw = je_org.subscriptions[currency].checkUpkeep(checkUpkeepPayload)
    checkUpkeepData = decode(['uint[]', 'address'], checkUpkeepDataRaw[1])
    assert len(checkUpkeepData[0]) == 2
    assert checkUpkeepData[1].lower() == runner.address.lower()


def test_performUpkeep(je_org):
    runner = bbenv.anons[4]
    sub1 = je_org.setup_subscription()
    sub2 = je_org.setup_subscription(account=bbenv.anons[1])

    currency = sub1._in.currency

    helpers.advance_time(31)
    checkUpkeepPayload = "0x" + encode( ['uint256','uint256', 'uint256','address'], [0, 100, 25, runner.address] ).hex()
    checkUpkeepDataRaw = je_org.subscriptions[currency].checkUpkeep(checkUpkeepPayload)
    checkUpkeepData = decode(['uint[]', 'address'], checkUpkeepDataRaw[1])
    putx = je_org.subscriptions[currency].performUpkeep(checkUpkeepDataRaw[1], helpers.by(runner))

    assert je_org.subscriptionsFactory.isSubscriptionActive(sub2._in.profileId, sub2._in.tierId, sub2._in.account.address)
    assert je_org.subscriptionsFactory.isSubscriptionActive(sub2._in.profileId, sub2._in.tierId, sub2._in.account.address)