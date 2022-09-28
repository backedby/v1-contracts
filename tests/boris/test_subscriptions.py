from base64 import decode
from brownie import accounts
from eth_abi import encode, decode
from brownie.network.state import Chain
from brownie.network import gas_price
from scripts.john.deploy import deploy
from calendar import monthrange
from datetime import datetime
chain = Chain()

def test_check_upkeep():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    subscriber = accounts[6]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tokeDeployer = accounts[7]
    token = deploy.erc20Token(tokeDeployer)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [token.address, accounts[8]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    subscriptions = deploy.bbSubscriptions(bbSubscriptionsFactory, token.address)

    token.mint(10000, {"from": subscriber})

    token.approve(subscriptions.address, 1000 * 60, {"from": subscriber})
    
    subscriptions.subscribe(0, 0, {"from": subscriber, "value": 10 ** 18})

    keeper = accounts[8]

    checkData = "0x" + encode(['uint256','uint256','uint256','uint256','address'], [0, 100, 1, 25, keeper.address]).hex()
    
    returnedCheckBytes = subscriptions.checkUpkeep(checkData)

    assert returnedCheckBytes[0] == False

    chain.sleep(60 * 60 * 24 * 31)
    chain.mine()
    
    returnedCheckBytes = subscriptions.checkUpkeep(checkData)

    assert returnedCheckBytes[0] == True

    returnedCheckData = decode(['uint256[]', 'address'], returnedCheckBytes[1])

    assert len(returnedCheckData[0]) == 1
    assert returnedCheckData[0][0] == 0
    assert returnedCheckData[1] == keeper

def test_perform_upkeep():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    subscriber = accounts[6]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tokeDeployer = accounts[7]
    token = deploy.erc20Token(tokeDeployer)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [token.address, accounts[8]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    bbSubscriptions = deploy.bbSubscriptions(bbSubscriptionsFactory, token.address)

    token.mint(10000, {"from": subscriber})

    token.approve(bbSubscriptions.address, 1000 * 60, {"from": subscriber})
    
    bbSubscriptions.subscribe(0, 0, {"from": subscriber, "value": 10 ** 18})
    

    keeper = accounts[8]
    pre_upkeep_balance = keeper.balance()

    checkData = "0x" + encode(['uint256','uint256','uint256','uint256','address'], [0, 100, 1, 50, keeper.address]).hex()

    chain.sleep(60 * 60 * 24 * 34)
    chain.mine()
    
    returnedCheckBytes = bbSubscriptions.checkUpkeep(checkData)
    gas_price("2 gwei")
    bbSubscriptions.performUpkeep(returnedCheckBytes[1], {"from": keeper})
    assert keeper.balance()/pre_upkeep_balance > 0.99999

    chain.sleep(60 * 60 * 24 * 34)
    chain.mine()
    for i in range(10, 35):
        token.mint(10000, {"from": accounts[i]})
        token.approve(bbSubscriptions.address, 1000 * 60, {"from": accounts[i]})
        bbSubscriptions.subscribe(0, 0, {"from": accounts[i], "value": 10 ** 18})
    gas_price("20 gwei")
    returnedCheckBytes = bbSubscriptions.checkUpkeep(checkData)
    bbSubscriptions.performUpkeep(returnedCheckBytes[1], {"from": keeper})
    assert keeper.balance()/pre_upkeep_balance > 0.9999

def test_subscribe():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    subscriber = accounts[6]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tokeDeployer = accounts[7]
    token = deploy.erc20Token(tokeDeployer)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [token.address, accounts[8]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    deployedSubscriptions = deploy.bbSubscriptions(bbSubscriptionsFactory, token.address)

    token.mint(1000, {"from": subscriber})

    token.approve(deployedSubscriptions.address, 1000 * 60, {"from": subscriber})

    deployedSubscriptions.subscribe(0, 0, {"from": subscriber, "value": 10 ** 18})

def test_unsubscribe():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    subscriber = accounts[6]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tokeDeployer = accounts[7]
    token = deploy.erc20Token(tokeDeployer)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [token.address, accounts[8]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    subscriptions = deploy.bbSubscriptions(bbSubscriptionsFactory, token.address)

    token.mint(1000, {"from": subscriber})

    token.approve(subscriptions.address, 1000 * 60, {"from": subscriber})

    subscriptions.subscribe(0, 0, {"from": subscriber, "value": 10 ** 18})

    subscriptions.unsubscribe(0, 0, {"from": subscriber})

def test_withdraw_to_treasury():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    subscriber = accounts[6]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tokeDeployer = accounts[7]
    token = deploy.erc20Token(tokeDeployer)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [token.address, accounts[8]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    subscriptions = deploy.bbSubscriptions(bbSubscriptionsFactory, token.address)

    token.mint(1000, {"from": subscriber})

    token.approve(subscriptions.address, 1000 * 60, {"from": subscriber})
    
    subscriptions.subscribe(0, 0, {"from": subscriber, "value": 10 ** 18})

    subscriptions.withdrawToTreasury({"from": bbTreasury})

def test_get_subscription():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    subscriber = accounts[6]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tokeDeployer = accounts[7]
    token = deploy.erc20Token(tokeDeployer)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [token.address, accounts[8]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    subscriptions = deploy.bbSubscriptions(bbSubscriptionsFactory, token.address)

    token.mint(1000, {"from": subscriber})

    token.approve(subscriptions.address, 1000 * 60, {"from": subscriber})
    
    subscriptions.subscribe(0, 0, {"from": subscriber, "value": 10 ** 18})

    (returnedPrice, returnedExpiration, returnedCancelled) = subscriptions.getSubscription(0, 0, subscriber)

    assert returnedPrice == tierPrices[0] * priceMultipliers[0]
    a,daysinmonth = monthrange(datetime.now().year, datetime.now().month)
    assert returnedExpiration == chain.time() + (60 * 60 * 24 * daysinmonth)
    assert returnedCancelled == False