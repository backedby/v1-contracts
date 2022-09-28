from brownie import accounts, reverts, interface
from scripts.john.deploy import deploy
from brownie.network.state import Chain
chain = Chain()

def test_deploy_subscriptions():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[4]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    tokeDeployer = accounts[5]
    token = deploy.erc20Token(tokeDeployer)

    subscriptionsDeployer = accounts[6]

    bbSubscriptionsFactory.deploySubscriptions(token.address, {"from": subscriptionsDeployer})

    #deploying same token again should revert
    with reverts():
        bbSubscriptionsFactory.deploySubscriptions(token.address, {"from": subscriptionsDeployer})     

def test_is_subscriptions_deployed():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[4]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    tokeDeployer = accounts[5]
    token = deploy.erc20Token(tokeDeployer)

    subscriptionsDeployer = accounts[6]

    bbSubscriptionsFactory.deploySubscriptions(token.address, {"from": subscriptionsDeployer})

    assert bbSubscriptionsFactory.isSubscriptionsDeployed(token.address) == True

def test_get_deployed_subscriptions():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[4]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    tokeDeployer = accounts[5]
    token = deploy.erc20Token(tokeDeployer)

    subscriptionsDeployer = accounts[6]

    deployedSubscriptions = bbSubscriptionsFactory.deploySubscriptions.call(token.address, {"from": subscriptionsDeployer})
    bbSubscriptionsFactory.deploySubscriptions(token.address, {"from": subscriptionsDeployer})

    assert bbSubscriptionsFactory.getDeployedSubscriptions(token.address) == deployedSubscriptions

def test_set_treasury():
    bbDeployer = accounts[0]    
    profileOwner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    unauthorized = accounts[4]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(profileOwner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    newTreasury = accounts[6]

    with reverts():
        bbSubscriptionsFactory.setTreasury(newTreasury, {"from": profileOwner})
    with reverts():
        bbSubscriptionsFactory.setTreasury(newTreasury, {"from": receiver})
    with reverts():
        bbSubscriptionsFactory.setTreasury(newTreasury, {"from": creator})
    with reverts():
        bbSubscriptionsFactory.setTreasury(newTreasury, {"from": unauthorized})
    with reverts():
        bbSubscriptionsFactory.setTreasury(newTreasury, {"from": bbTreasury})

    bbSubscriptionsFactory.setTreasury(newTreasury, {"from": bbDeployer})
    assert bbSubscriptionsFactory.getTreasury() == newTreasury
    bbSubscriptionsFactory.setTreasury(bbDeployer, {"from": bbDeployer})
    assert bbSubscriptionsFactory.getTreasury() == bbDeployer

def test_change_owner():
    bbDeployer = accounts[0]    
    profileOwner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    unauthorized = accounts[4]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(profileOwner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    newTreasury = accounts[6]

    bbSubscriptionsFactory.setTreasury(newTreasury, {"from": bbDeployer})
    assert bbSubscriptionsFactory.getTreasury() == newTreasury
    newNewTreasury = accounts[7]
    bbSubscriptionsFactory.transferOwnership(newTreasury, {"from": bbDeployer})
    bbSubscriptionsFactory.setTreasury(newNewTreasury, {"from": newTreasury})
    assert bbSubscriptionsFactory.getTreasury() == newNewTreasury
    with reverts():
        bbSubscriptionsFactory.setTreasury(newTreasury, {"from": bbDeployer})


def test_set_subscription_gas_requirement():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    unauthorized = accounts[4]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    erc20 = deploy.erc20Token(bbDeployer)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)\

    bbSubscriptionsFactory.deploySubscriptions(erc20.address, {'from': bbDeployer})
    
    bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 5, {"from": bbDeployer})
    with reverts():
        bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 5, {"from": owner})
    with reverts():
        bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 14, {"from": bbDeployer})
    with reverts():
        bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 14, {"from": owner})
    with reverts():
        bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 14, {"from": receiver})
    with reverts():
        bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 14, {"from": creator})
    with reverts():
        bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 14, {"from": unauthorized})
    with reverts():
        bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 14, {"from": bbTreasury})
    with reverts():
        bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 18, {"from": bbDeployer})
    with reverts():
        bbSubscriptionsFactory.setUpkeepGasRequirement(erc20.address, 10 ** 14, {"from": bbDeployer})

def test_get_treasury():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    assert bbSubscriptionsFactory.getTreasury() == bbTreasury

def test_get_grace_period():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    # 2 days
    expectedGracePeriod  = (60 * 60 * 24) * 2

    assert bbSubscriptionsFactory.getGracePeriod() == expectedGracePeriod

def test_get_contribution_bounds():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    expectedLower = 1
    expectedUpper = 100

    (returnedLower, returnedUpper) = bbSubscriptionsFactory.getContributionBounds()

    assert returnedLower == expectedLower
    assert returnedUpper == expectedUpper

def test_get_subscription_gas_requirement():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    erc20 = deploy.erc20Token(bbDeployer)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)
    bbSubscriptionsFactory.deploySubscriptions(erc20.address, {'from': bbDeployer})
    
    bbSubscription = interface.IBBSubscriptions(bbSubscriptionsFactory.getDeployedSubscriptions(erc20.address))

    expectedGasRequirement = 225000

    assert bbSubscription.getUpkeepGasRequirement() == expectedGasRequirement

def test_set_subscription_currency():
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

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    tokeDeployer = accounts[7]
    token = deploy.erc20Token(tokeDeployer)

    subscriptionsDeployer = accounts[8]

    bbSubscriptionsFactory.deploySubscriptions(token.address, {"from": subscriptionsDeployer})

    with reverts():
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": bbDeployer})
    with reverts():
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": owner})
    with reverts():
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": receiver})
    with reverts():
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": creator})
    with reverts():
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": bbTreasury})
    with reverts():
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": subscriber})
    with reverts():
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": tokeDeployer})
    with reverts():
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": subscriptionsDeployer})

def test_get_subscription_currency():
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

    token.approve(deployedSubscriptions.address, 10 ** 25, {"from": subscriber})

    deployedSubscriptions.subscribe(0, 0, {"from": subscriber, "value": 10 ** 18})

def test_create_subscription_profile():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[6], accounts[7]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})
    

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})
    with reverts():
        bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})
    with reverts():
        bbSubscriptionsFactory.createSubscriptionProfile(0, 1, 1, {"from": creator})
    with reverts():
        bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 0, {"from": owner})

def test_set_contribution():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[6], accounts[7]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    bbSubscriptionsFactory.setContribution(0, 10, {"from": owner})
    with reverts():
        bbSubscriptionsFactory.setContribution(0, 0, {"from": owner})
    with reverts():
        bbSubscriptionsFactory.setContribution(0, 11, {"from": bbTreasury})
    with reverts():
        bbSubscriptionsFactory.setContribution(0, 101, {"from": owner})

def test_get_subscription_profile():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[6], accounts[7]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    tierSet = 0
    contribution = 10

    bbSubscriptionsFactory.createSubscriptionProfile(0, tierSet, contribution, {"from": owner})

    (returnedTierSet, returnedContribution) = bbSubscriptionsFactory.getSubscriptionProfile(0)

    assert returnedTierSet == tierSet
    assert returnedContribution == contribution

def test_is_subscription_profile_created():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    bbTreasury = accounts[5]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[6], accounts[7]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    assert bbSubscriptionsFactory.isSubscriptionProfileCreated(0) == True

def test_is_subscription_active():
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

    token.approve(deployedSubscriptions.address, 10 ** 25, {"from": subscriber})
    assert bbSubscriptionsFactory.isSubscriptionActive(0, 0, subscriber) == False
    deployedSubscriptions.subscribe(0, 0, {"from": subscriber, "value": 10 ** 18})
    assert bbSubscriptionsFactory.isSubscriptionActive(0, 0, owner) == True
    assert bbSubscriptionsFactory.isSubscriptionActive(0, 0, subscriber) == True
    chain.sleep(60 * 60 * 24 * 31)
    chain.mine()
    assert bbSubscriptionsFactory.isSubscriptionActive(0, 0, subscriber) == True
    chain.sleep(60 * 60 * 24 * 31 * 60)
    chain.mine()
    assert bbSubscriptionsFactory.isSubscriptionActive(0, 0, subscriber) == False
    assert bbSubscriptionsFactory.isSubscriptionActive(0, 0, owner) == True