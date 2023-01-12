from brownie import reverts
from brownie import BBSubscriptions
from scripts.josh.bbenv import bbenv
from scripts.josh.helpers import helpers, objdict
from scripts.josh.snapshotbalances import SnapshotBalances

def test_subscribe(je_org):
    profile = je_org.setup_subscriptionProfile()
    profileId = profile.out_.profileId
    tierIndex = 1 if len(profile._in._tierSet._in.prices) > 2 else 0
    tierPrice = profile._in._tierSet._in.prices[tierIndex]
    price = je_org.tiers.getTier(profileId, profile._in.tierSet, tierIndex, je_org.TUSD.address)[1]

    subber = je_org.anons[0]

    je_org.TUSD.mint(int(tierPrice * 120 * 10 ** je_org.TUSD.decimals()), helpers.by(subber))
    je_org.TUSD.approve(je_org.subscriptions[je_org.TUSD.address], helpers.MAXUINT256, helpers.by(subber))

    sub = je_org.setup_subscription(profileId=profileId, tierId=tierIndex, currency=je_org.TUSD.address, expectedPrice=price, account=subber)
    
    subscription = je_org.subscriptions[je_org.TUSD.address].getSubscriptionFromProfile(sub._in.profileId, sub._in.tierId, sub._in.account.address)
    assert subscription[1] == price

    return objdict({
        'sub': sub,
        'profile': profile,
        'profileId': profileId,
        'tierId': tierIndex,
        'subAccount': subber,
        'expectedPrice': price
    })

def test_multiTierSubscribe(je_org):
    x = test_subscribe(je_org)
    profileId = x.profile._in.profileId

    prepaidGas = je_org.subscriptionsFactory.getSubscriptionFee(je_org.TUSD.address)
    price = je_org.tiers.getTier(profileId, x.profile._in.tierSet, x.tierId+1, je_org.TUSD.address)[1]
    je_org.subscriptions[je_org.TUSD.address].subscribe(x.profileId, x.tierId+1, price, helpers.by(x.subAccount, {'value': prepaidGas}))
    tierSetId = je_org.subscriptionsFactory.getSubscriptionProfile(profileId)[0]
    tier1Price = je_org.tiers.getTier(profileId, tierSetId, x.tierId, je_org.TUSD)[1]
    tier2Price = je_org.tiers.getTier(profileId, tierSetId, x.tierId+1, je_org.TUSD)[1]

    with SnapshotBalances([x.subAccount], [je_org.TUSD]) as snap:
        helpers.advance_time(33)
        je_org.performUpkeep()
    assert snap.diff(x.subAccount, je_org.TUSD) == (tier1Price + tier2Price)
    
    with SnapshotBalances([x.subAccount], [je_org.TUSD]) as snap:
        helpers.advance_time(33)
        je_org.performUpkeep()
    assert snap.diff(x.subAccount, je_org.TUSD) == (tier1Price + tier2Price)


def test_changeCurrency(je_org):
    x = test_subscribe(je_org)
    je_org.DAI.mint(5000e18, helpers.by(x.subAccount))
    je_org.DAI.approve(je_org.subscriptions[je_org.DAI.address], helpers.MAXUINT256, helpers.by(x.subAccount))
    price = je_org.tiers.getTier(x.profileId, x.profile._in.tierSet, x.tierId, je_org.DAI.address)[1]
    prepaidGas = je_org.subscriptionsFactory.getSubscriptionFee(je_org.DAI.address)
    with reverts():
        je_org.subscriptions[je_org.DAI.address].subscribe(x.profileId, x.tierId, price, helpers.by(x.subAccount, {'value': prepaidGas}))


def test_changeCurrency_cancelled_first(je_org):
    x = test_subscribe(je_org)
    je_org.DAI.mint(5000e18, helpers.by(x.subAccount))
    je_org.DAI.approve(je_org.subscriptions[je_org.DAI.address], helpers.MAXUINT256, helpers.by(x.subAccount))
    prepaidGas = je_org.subscriptionsFactory.getSubscriptionFee(je_org.DAI.address)
    je_org.subscriptions[je_org.TUSD.address].unsubscribe(x.profileId, x.tierId, helpers.by(x.subAccount))
    price = je_org.tiers.getTier(x.profileId, x.profile._in.tierSet, x.tierId, je_org.DAI.address)[1]
    je_org.subscriptions[je_org.DAI.address].subscribe(x.profileId, x.tierId, price, helpers.by(x.subAccount, {'value': prepaidGas}))


def test_subscribe_outOfRange(je_org):
    profile = je_org.setup_subscriptionProfile()
    profileId = profile.out_.profileId
    tierIndex = 1 if len(profile._in._tierSet._in.prices) > 2 else 0
    tierPrice = profile._in._tierSet._in.prices[tierIndex]
    price = je_org.tiers.getTier(profileId, profile._in.tierSet, tierIndex, je_org.TUSD.address)[1]

    subber = je_org.anons[0]

    je_org.TUSD.mint(int(tierPrice * 120 * 10 ** je_org.TUSD.decimals()), helpers.by(subber))
    je_org.TUSD.approve(je_org.subscriptions[je_org.TUSD.address], helpers.MAXUINT256, helpers.by(subber))
    with reverts():
        je_org.setup_subscription(profileId=1e9, tierId=tierIndex, currency=je_org.TUSD.address, account=subber)
        
    with reverts():
        je_org.setup_subscription(profileId=profileId, tierId=1e9, currency=je_org.TUSD.address, account=subber)


def test_subscribe_notEnoughMoney(je_org, DebugERC20):
    profile = je_org.setup_subscriptionProfile()
    profileId = profile.out_.profileId
    tierIndex = 1 if len(profile._in._tierSet._in.prices) > 2 else 0
    tierPrice = profile._in._tierSet._in.prices[tierIndex]
    price = je_org.tiers.getTier(profileId, profile._in.tierSet, tierIndex, je_org.TUSD.address)[1]
    subContract = BBSubscriptions.at(je_org.subscriptions[je_org.TUSD.address])

    subber = je_org.anons[0]
    
    with reverts():
        tx = subContract.subscribe(profileId, tierIndex, price, helpers.by(subber))

    with reverts():
        je_org.setup_subscription(profileId=profileId, tierId=1e9, currency=je_org.TUSD.address, account=subber)

    je_org.TUSD.mint(int(tierPrice * 120 * 10 ** je_org.TUSD.decimals()), helpers.by(subber))
    with reverts():
        je_org.setup_subscription(profileId=profileId, tierId=1e9, currency=je_org.TUSD.address, account=subber)

    je_org.TUSD.approve(je_org.subscriptions[je_org.TUSD.address], helpers.MAXUINT256, helpers.by(subber))
    with reverts():
        tx = subContract.subscribe(profileId, tierIndex, price, helpers.by(subber))

def test_subscribe_depreciated(je_org):
    profile = je_org.setup_subscriptionProfile()
    profileId = profile.out_.profileId
    tierIndex = 1 if len(profile._in._tierSet._in.prices) > 2 else 0
    tierPrice = profile._in._tierSet._in.prices[tierIndex]
    tierDetails = je_org.tiers.getTier(profileId, profile._in.tierSet, tierIndex, je_org.TUSD.address)
    price = tierDetails[1]

    #depreciate tier 0
    newDepreciated = profile._in._tierSet._in.depreciated
    newDepreciated[0] = True
    je_org.tiers.editTiers(profileId, profile.out_.tierSet, profile._in._tierSet._in.prices, profile._in._tierSet._in.cids, newDepreciated, helpers.by(profile._in.account))

    subContract = BBSubscriptions.at(je_org.subscriptions[je_org.TUSD.address])

    subber = je_org.anons[0]
    je_org.TUSD.mint(int(tierPrice * 120 * 10 ** je_org.TUSD.decimals()), helpers.by(subber))
    je_org.TUSD.approve(je_org.subscriptions[je_org.TUSD.address], helpers.MAXUINT256, helpers.by(subber))
    gas = je_org.subscriptionsFactory.getSubscriptionFee(je_org.TUSD.address)

    with reverts():
        tx = subContract.subscribe(profileId, 0, price, helpers.by(subber, {'value': gas}))

def test_subscribe_sunset(je_org):
    profile = je_org.setup_subscriptionProfile()
    profileId = profile.out_.profileId
    tierSetId = profile.out_.tierSet
    tierIndex = 1 if len(profile._in._tierSet._in.prices) > 2 else 0
    tierPrice = profile._in._tierSet._in.prices[tierIndex]
    tierDetails = je_org.tiers.getTier(profileId, profile._in.tierSet, tierIndex, je_org.TUSD.address)
    price = tierDetails[1]

    subContract = BBSubscriptions.at(je_org.subscriptions[je_org.TUSD.address])

    subber = je_org.anons[0]
    je_org.TUSD.mint(int(tierPrice * 120 * 10 ** je_org.TUSD.decimals()), helpers.by(subber))
    je_org.TUSD.approve(je_org.subscriptions[je_org.TUSD.address], helpers.MAXUINT256, helpers.by(subber))
    gas = je_org.subscriptionsFactory.getSubscriptionFee(je_org.TUSD.address)
    tx = subContract.subscribe(profileId, tierIndex, price, helpers.by(subber, {'value': gas}))
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, tierIndex, subber.address) is True
    assert je_org.tiers.isCurrencySupported(profileId, tierSetId, je_org.TUSD.address) is True
    je_org.tiers.setSupportedCurrencies(profileId, tierSetId, [je_org.TUSD.address], [0], helpers.by(profile._in.account))
    assert je_org.tiers.isCurrencySupported(profileId, tierSetId, je_org.TUSD.address) is False
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, tierIndex, subber.address) is True
    helpers.advance_time(33)
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, tierIndex, subber.address) is False
    je_org.performUpkeep()
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, tierIndex, subber.address) is False

def test_unsubscribe(je_org):
    x = test_subscribe(je_org)
    
    subProfile = BBSubscriptions.at(je_org.subscriptions[je_org.TUSD.address])
    unsubTx = subProfile.unsubscribe(x.profile.out_.profileId, x.sub._in.tierId, helpers.by(x.sub._in.account))

    assert unsubTx.events['Unsubscribed']['subscriptionId'] == 0
    subInfo = subProfile.getSubscriptionFromId(unsubTx.events['Unsubscribed']['subscriptionId'])
    assert subInfo[0] == x.profile.out_.profileId
    assert subInfo[1] == x.sub._in.tierId
    assert subInfo[2] == x.sub._in.account
    

def test_unsubscribe_not_subscriber(je_org):
    x = test_subscribe(je_org)
    
    subProfile = BBSubscriptions.at(je_org.subscriptions[je_org.TUSD.address])
    with reverts():
        subProfile.unsubscribe(x.profile.out_.profileId, x.sub._in.tierId, helpers.by(je_org.anons[1]))
def test_unsubscribe_outOfRange(je_org):
    x = test_subscribe(je_org)
    
    subProfile = BBSubscriptions.at(je_org.subscriptions[je_org.TUSD.address])
    with reverts():
        subProfile.unsubscribe(1e9, x.sub._in.tierId, helpers.by(je_org.anons[1]))
    with reverts():
        subProfile.unsubscribe(x.profile.out_.profileId, 1e9, helpers.by(je_org.anons[1]))

def test_subscription_expire(je_org):
    x = test_subscribe(je_org)
    assert je_org.subscriptionsFactory.isSubscriptionActive(x.profileId, x.tierId, x.subAccount) is True
    helpers.advance_time(35)
    assert je_org.subscriptionsFactory.isSubscriptionActive(x.profileId, x.tierId, x.subAccount) is False

def test_isSubscriptionActive_IBBPermissions(je_org, DebugProfileOwner):
    subProfile = je_org.setup_subscriptionProfile()
    profileId = subProfile._in.profileId
    tierId = 1
    firstOwner = subProfile._in.account

    subber = je_org.setup_subscription(profileId=profileId, tierId=tierId)
    
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, 1, firstOwner)
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, 1, je_org.coCreator) is False
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, 1, subber._in.account)

    profileOwner = DebugProfileOwner.deploy( helpers.by(firstOwner))
    profileOwner.setOwner(je_org.coCreator, True, helpers.by(firstOwner))

    je_org.profiles.editProfile(profileId, profileOwner, firstOwner, "somecid", helpers.by(firstOwner))
    
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, 1, firstOwner)
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, 1, je_org.coCreator)
    assert je_org.subscriptionsFactory.isSubscriptionActive(profileId, 1, subber._in.account)

def test_getSubscription_outOfRange(je_org):
    subber = je_org.setup_subscription()
    with reverts():
        #address doesn't exist
        je_org.subscriptions[je_org.TUSD.address].getSubscriptionFromProfile(0, 0, "0x68f517efc82c1c60997f6aa7d7322d719bb6bdbe")
    with reverts():
        #profile doesn't exist
        je_org.subscriptions[je_org.TUSD.address].getSubscriptionFromProfile(1e9, 0, subber._in.account)
    with reverts():
        #tier doesn't exist
        je_org.subscriptions[je_org.TUSD.address].getSubscriptionFromProfile(0, 1e9, subber._in.account)


def test_outOfFunds(je_org):
    #simulate nothing left.
    je_org.gasOracle.setGasPrice(1, helpers.by(je_org.deployer))
    je_org.subscriptionsFactory.setSubscriptionFee(je_org.TUSD.address, 1*60, helpers.by(je_org.deployer))
    sub = je_org.setup_subscription()
    assert je_org.subscriptions[je_org.TUSD.address].balance() == 60
    je_org.gasOracle.setGasPrice(30, helpers.by(je_org.deployer))
    je_org.subscriptionsFactory.setSubscriptionFee(je_org.TUSD.address, 225000*60, helpers.by(je_org.deployer))
    helpers.advance_time(31)
    je_org.performUpkeep()
    assert je_org.subscriptions[je_org.TUSD.address].balance() == 0
    helpers.advance_time(31)
    je_org.performUpkeep()
    assert je_org.subscriptions[je_org.TUSD.address].balance() == 0

def test_withdrawToTreasury(je_org):
    bbsubs = je_org.subscriptions[je_org.TUSD.address]
    je_org.TUSD.mintFor(bbsubs, 1e24, helpers.by(je_org.deployer))

    assert je_org.TUSD.balanceOf(bbsubs) == 1e24
    bbsubs.withdrawToTreasury(helpers.by(je_org.anons[1]))
    assert je_org.TUSD.balanceOf(bbsubs) == 0
    assert je_org.TUSD.balanceOf(je_org.treasury) == 1e24

def test_expectedValue(je_org):
    profile = je_org.setup_subscriptionProfile()
    profileId = profile.out_.profileId
    tierIndex = 1 if len(profile._in._tierSet._in.prices) > 2 else 0
    tierPrice = profile._in._tierSet._in.prices[tierIndex]
    price = je_org.tiers.getTier(profileId, profile._in.tierSet, tierIndex, je_org.TUSD.address)[1]

    subber = je_org.anons[0]

    je_org.TUSD.mint(int(tierPrice * 120 * 10 ** je_org.TUSD.decimals()), helpers.by(subber))
    je_org.TUSD.approve(je_org.subscriptions[je_org.TUSD.address], helpers.MAXUINT256, helpers.by(subber))

    with reverts():
        je_org.setup_subscription(profileId=profileId, tierId=tierIndex, currency=je_org.TUSD.address, expectedPrice=price+1, account=subber)