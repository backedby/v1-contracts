from brownie import reverts
from scripts.josh.bbenv import bbenv
from scripts.josh.helpers import helpers, objdict

def test_createTierSet(je_org):
    #profile = je_org.setup_profile()
    #tierAmount = 5 * 10 ** je_org.TUSD.decimals()
    #tierCid = "sogboan04nznrjbga8gasnfdg"
    #tx1 = je_org.setup_tier(account=profile._in.account, profileId=profile.out_.profileId, price=tierAmount, cid=tierCid)
    #assert tx1.events['CreatedTier']['price'] == tierAmount
    #assert tx1.out_.cid == tierCid


    prices = [1,5,10,20]
    cids = ['a', 'b', 'c', 'd']
    supportedCurrencies = [je_org.TUSD.address]
    priceMultipliers = [int(10 ** je_org.TUSD.decimals())]
    tierSet = je_org.setup_tiers(prices, cids, supportedCurrencies, priceMultipliers, account=je_org.creator)
    profileId = tierSet._in.profileId
    tierSetId = tierSet.out_.tierSetId

    #this returns false since profile setup hasn't been completed.
    assert je_org.subscriptionsFactory.isSubscriptionProfileCreated(profileId) == False

    tierId = 2
    tierId_Cid = je_org.tiers.getTier(profileId, tierSetId, tierId, je_org.TUSD)[0]
    tierId_Price = je_org.tiers.getTier(profileId, tierSetId, tierId, je_org.TUSD)[1]

    assert tierId_Cid == cids[tierId]
    assert (prices[tierId] * priceMultipliers[0]) == tierId_Price

    return objdict({
        'tierSet': tierSet,
        'account': tierSet._in.account,
        'tierSetId': tierSet.out_.tierSetId,
        'profileId': profileId,
        'prices': prices,
        'cids': cids,
        'supportedCurrencies': supportedCurrencies,
        'priceMultipliers': priceMultipliers
    })

def test_getTier_Cid(je_org):
    x = test_createTierSet(je_org)
    tc = je_org.tiers.getTier(x.profileId, x.tierSetId, 1, je_org.TUSD)[0]
    assert tc == x.cids[1]


def test_getTier_Cid_outOfRange(je_org):
    x = test_createTierSet(je_org)
    with reverts():
        je_org.tiers.getTier(1e9, x.tierSetId, 1, je_org.TUSD)[0]
    with reverts():
        je_org.tiers.getTier(x.profileId, 1e9, 1, je_org.TUSD)[0]
    with reverts():
        je_org.tiers.getTier(1e9, 1e9, 1, je_org.TUSD)[0]


def test_getTier_Price(je_org):
    x = test_createTierSet(je_org)
    tc = je_org.tiers.getTier(x.profileId, x.tierSetId, 1, je_org.TUSD)[1]
    print("prices", x.prices)
    print("supported", x.supportedCurrencies)
    print("multipliers", x.priceMultipliers)
    assert tc == x.prices[1] * x.priceMultipliers[0]

def test_getTier_Price_outOfRange(je_org):
    x = test_createTierSet(je_org)
    with reverts():
        je_org.tiers.getTier(1e9, x.tierSetId, 1, je_org.TUSD)[1]
    with reverts():
        je_org.tiers.getTier(x.profileId, 1e9, 1, je_org.TUSD)[1]
    with reverts():
        je_org.tiers.getTier(1e9, 1e9, 1, je_org.TUSD)[1]

def test_getTier_Price_unknown_currency(je_org, DebugERC20):
    x = test_createTierSet(je_org)
    badmoney = DebugERC20.deploy("bad", "money", helpers.by(je_org.deployer))
    with reverts():
        je_org.tiers.getTier(x.profileId, x.tierSetId, 1, badmoney)[1]

def test_getTierSet(je_org):
    x = test_createTierSet(je_org)
    ts = je_org.tiers.getTierSet(x.profileId, x.tierSetId)

    assert len(x.prices) == len(ts[0])
    assert len(x.cids) == len(ts[1])
    assert x.prices[0] == ts[0][0]
    assert x.cids[0] == ts[1][0]


def test_getTierSet_outOfRange(je_org):
    x = test_createTierSet(je_org)
    with reverts():
        je_org.tiers.getTierSet(x.profileId, 1e9)
    with reverts():
        je_org.tiers.getTierSet(1e9, x.tierSetId)
    with reverts():
        je_org.tiers.getTierSet(1e9, 1e9)

def test_totals(je_org):
    x = test_createTierSet(je_org)
    assert je_org.tiers.totalTiers(x.profileId, x.tierSetId) == 4
    assert je_org.tiers.totalTierSets(x.profileId) == 1

def test_createTier_non_owner(je_org):
    profile = je_org.setup_profile()
    prices = [1,5,10,20]
    cids = ['a', 'b', 'c', 'd']
    supportedCurrencies = [je_org.TUSD.address]
    priceMultipliers = [je_org.TUSD.decimals()]
    with reverts():
        tierSet = je_org.setup_tiers(prices, cids, supportedCurrencies, priceMultipliers, profileId=profile.out_.profileId, account=je_org.anons[1])

def test_editTierSet(je_org):
    x = test_createTierSet(je_org)

    newPrices = [5, 10, 15, 25]
    newCids = ['w', 'x', 'y', 'z']
    newDepreciated = [False]*len(newCids)
    je_org.tiers.editTiers(x.profileId, x.tierSetId, newPrices, newCids, newDepreciated, helpers.by(x.account))

    tierId = 2
    tierId_Cid = je_org.tiers.getTier(x.profileId, x.tierSetId, tierId, je_org.TUSD)[0]
    tierId_Price = je_org.tiers.getTier(x.profileId, x.tierSetId, tierId, je_org.TUSD)[1]

    assert tierId_Cid == newCids[tierId]
    assert (newPrices[tierId] * x.priceMultipliers[0]) == tierId_Price


def test_editTierSet_outOfRange(je_org):
    x = test_createTierSet(je_org)

    newPrices = [5, 10, 15, 25]
    newCids = ['w', 'x', 'y', 'z']
    newDepreciated = [False]*len(newCids)
    je_org.tiers.editTiers(x.profileId, x.tierSetId, newPrices, newCids, newDepreciated, helpers.by(x.account))

    tierId = 6
    tierId_Cid = je_org.tiers.getTier(x.profileId, x.tierSetId, tierId, je_org.TUSD)[0]
    tierId_Price = je_org.tiers.getTier(x.profileId, x.tierSetId, tierId, je_org.TUSD)[1]

    assert tierId_Cid == newCids[tierId]
    assert (newPrices[tierId] * x.priceMultipliers[0]) == tierId_Price

def test_editTierSet_outOfRange(je_org):
    x = test_createTierSet(je_org)

    newPrices = [5, 10, 15, 25]
    newCids = ['w', 'x', 'y', 'z']
    newDepreciated = [False]*len(newCids)
    with reverts():
        je_org.tiers.editTiers(x.profileId, 1e9, newPrices, newCids, newDepreciated, helpers.by(x.account))


def test_editTierSet_outOfRange_non_owner(je_org):
    x = test_createTierSet(je_org)

    newPrices = [5, 10, 15, 25]
    newCids = ['w', 'x', 'y', 'z']
    newDepreciated = [False]*len(newCids)
    with reverts():
        je_org.tiers.editTiers(x.profileId, 1e9, newPrices, newCids, newDepreciated, helpers.by(je_org.anons[0]))


def test_editTierSet_non_owner(je_org):
    x = test_createTierSet(je_org)

    newPrices = [5, 10, 15, 25]
    newCids = ['w', 'x', 'y', 'z']
    newDepreciated = [False]*len(newCids)
    with reverts():
        je_org.tiers.editTiers(x.profileId, x.tierSetId, newPrices, newCids, newDepreciated, helpers.by(je_org.anons[1]))
    
    tierId = 2
    tierId_Cid = je_org.tiers.getTier(x.profileId, x.tierSetId, tierId, je_org.TUSD)[0]
    tierId_Price = je_org.tiers.getTier(x.profileId, x.tierSetId, tierId, je_org.TUSD)[1]

    assert tierId_Cid == x.cids[tierId]
    assert (x.prices[tierId] * x.priceMultipliers[0]) == tierId_Price

def test_setSupportedCurrencies(je_org):
    x = test_createTierSet(je_org)

    je_org.tiers.setSupportedCurrencies(x.profileId, x.tierSetId, [je_org.DAI], [10 ** je_org.DAI.decimals()], helpers.by(x.account))
    assert je_org.tiers.isCurrencySupported(x.profileId, x.tierSetId, je_org.DAI) is True

def test_setSupportedCurrencies_non_owner(je_org):
    x = test_createTierSet(je_org)
    with reverts():
        je_org.tiers.setSupportedCurrencies(x.profileId, x.tierSetId, [je_org.DAI], [10 ** je_org.DAI.decimals()], helpers.by(je_org.anons[1]))

    assert je_org.tiers.isCurrencySupported(x.profileId, x.tierSetId, je_org.DAI) is False
    
def test_setSupportedCurrencies_unknownCurrency(je_org, DebugERC20):
    x = test_createTierSet(je_org)
    badmoney = DebugERC20.deploy("bad", "money", helpers.by(je_org.deployer))
    je_org.tiers.setSupportedCurrencies(x.profileId, x.tierSetId, [badmoney], [10 ** badmoney.decimals()], helpers.by(x.account))
    assert je_org.tiers.isCurrencySupported(x.profileId, x.tierSetId, badmoney) is True

def test_getCurrencyMultiplier(je_org):
    x = test_createTierSet(je_org)
    assert je_org.tiers.getCurrencyMultiplier(x.profileId, x.tierSetId, je_org.TUSD) == int(10 ** je_org.TUSD.decimals())

def test_getCurrencyMultiplier_outOfRange(je_org):
    x = test_createTierSet(je_org)
    
    with reverts():
        je_org.tiers.getCurrencyMultiplier(1e9, x.tierSetId, je_org.TUSD)
    with reverts():
        je_org.tiers.getCurrencyMultiplier(x.profileId, 1e9, je_org.TUSD)
    with reverts():
        je_org.tiers.getCurrencyMultiplier(1e9, 1e9, je_org.TUSD)

def test_getCurrencyMultiplier_unknownCurrency(je_org, DebugERC20):
    x = test_createTierSet(je_org)
    badmoney = DebugERC20.deploy("bad", "money", helpers.by(je_org.deployer))

    with reverts():
        je_org.tiers.getCurrencyMultiplier(x.profileId, x.tierSetId, badmoney)
