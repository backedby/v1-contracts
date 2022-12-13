from brownie import accounts, reverts, DebugGasOracle
from scripts.john.deploy import deploy

def test_deploy_subscriptions():
    bbDeployer = accounts[0]    
    bbTreasury = accounts[4]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    tokeDeployer = accounts[5]
    token = deploy.erc20Token(tokeDeployer)

    subscriptionsDeployer = accounts[6]

    bbSubscriptionsFactory.deploySubscriptions(token.address, {"from": subscriptionsDeployer})        

def test_is_subscriptions_deployed():
    bbDeployer = accounts[0]    
    bbTreasury = accounts[4]

    bbProfiles = deploy.bbProfiles(bbDeployer)

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

def test_set_treasury_owner():
    bbDeployer = accounts[0]    
    unauthorized = accounts[4]
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    newTreasuryOwner = accounts[6]

    with reverts():
        bbSubscriptionsFactory.setTreasuryOwner(newTreasuryOwner, {"from": unauthorized})
        bbSubscriptionsFactory.setTreasuryOwner(newTreasuryOwner, {"from": bbTreasury})

    bbSubscriptionsFactory.setTreasuryOwner(newTreasuryOwner, {"from": bbDeployer})

def test_set_gas_oracle_owner():
    bbDeployer = accounts[0]    
    unauthorized = accounts[4]
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    newGasPriceOwner = accounts[6]

    with reverts():
        bbSubscriptionsFactory.setGasOracleOwner(newGasPriceOwner, {"from": unauthorized})
        bbSubscriptionsFactory.setGasOracleOwner(newGasPriceOwner, {"from": bbTreasury})

    bbSubscriptionsFactory.setGasOracleOwner(newGasPriceOwner, {"from": bbDeployer})

def test_set_subscription_fee_owner():
    bbDeployer = accounts[0]    
    unauthorized = accounts[4]
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    newUpkeepGasRequirementOwner = accounts[6]

    with reverts():
        bbSubscriptionsFactory.setSubscriptionFeeOwner(newUpkeepGasRequirementOwner, {"from": unauthorized})
        bbSubscriptionsFactory.setSubscriptionFeeOwner(newUpkeepGasRequirementOwner, {"from": bbTreasury})

    bbSubscriptionsFactory.setSubscriptionFeeOwner(newUpkeepGasRequirementOwner, {"from": bbDeployer})

def test_get_treasury_owner():
    bbDeployer = accounts[0]    
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    assert bbSubscriptionsFactory.getTreasuryOwner() == bbDeployer

def test_get_gas_oracle_owner():
    bbDeployer = accounts[0]    
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    assert bbSubscriptionsFactory.getGasOracleOwner() == bbDeployer

def test_get_subscription_fee_owner():
    bbDeployer = accounts[0]    
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    assert bbSubscriptionsFactory.getSubscriptionFeeOwner() == bbDeployer

def test_set_treasury():
    bbDeployer = accounts[0]    
    unauthorized = accounts[4]
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    newTreasury = accounts[6]

    with reverts():
        bbSubscriptionsFactory.setTreasury(newTreasury, {"from": unauthorized})
        bbSubscriptionsFactory.setTreasury(newTreasury, {"from": bbTreasury})

    bbSubscriptionsFactory.setTreasury(newTreasury, {"from": bbDeployer})

def test_set_gas_oracle():
    bbDeployer = accounts[0]    
    unauthorized = accounts[4]
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    newGasOracle = DebugGasOracle.deploy({'from': bbDeployer})

    with reverts():
        bbSubscriptionsFactory.setGasOracle(newGasOracle, {"from": unauthorized})
    with reverts():
        bbSubscriptionsFactory.setGasOracle(newGasOracle, {"from": bbTreasury})

    bbSubscriptionsFactory.setGasOracle(newGasOracle, {"from": bbDeployer})

def test_set_subscription_fee():
    bbDeployer = accounts[0]    
    unauthorized = accounts[4]
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    erc20 = deploy.erc20Token(bbDeployer)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)
    bbSubscriptionsFactory.deploySubscriptions(erc20.address, {'from': bbDeployer})

    newSubscriptionFee = 1000

    with reverts():
        bbSubscriptionsFactory.setSubscriptionFee(erc20.address, newSubscriptionFee, {"from": unauthorized})
        bbSubscriptionsFactory.setSubscriptionFee(erc20.address, newSubscriptionFee, {"from": bbTreasury})
        bbSubscriptionsFactory.setSubscriptionFee(erc20.address, newSubscriptionFee, {"from": bbDeployer})

    bbSubscriptionsFactory.setSubscriptionFee(erc20.address, newSubscriptionFee, {"from": bbDeployer})

def test_get_treasury():
    bbDeployer = accounts[0]    
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    assert bbSubscriptionsFactory.getTreasury() == bbTreasury

def test_get_gas_oracle():
    bbDeployer = accounts[0]    
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    gasOracle = DebugGasOracle.deploy({'from': bbDeployer})

    bbSubscriptionsFactory.setGasOracle(gasOracle, {"from": bbDeployer})

    assert bbSubscriptionsFactory.getGasOracle() == gasOracle

def test_get_subscription_fee():
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
    deprecated = [False, False, False]
    supportedCurrencies = [token.address, accounts[8]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, deprecated, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    gasOracle = DebugGasOracle.deploy({'from': bbDeployer})

    bbSubscriptionsFactory.setGasOracle(gasOracle, {"from": bbDeployer})

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    bbSubscriptions = deploy.bbSubscriptions(bbSubscriptionsFactory, token.address)

    assert bbSubscriptionsFactory.getSubscriptionFee(token) == 13500000 * 30000000000

def test_get_grace_period():
    bbDeployer = accounts[0]    
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    # 2 days
    expectedGracePeriod  = (60 * 60 * 24) * 2

    assert bbSubscriptionsFactory.getGracePeriod() == expectedGracePeriod

def test_get_contribution_bounds():
    bbDeployer = accounts[0]    
    bbTreasury = accounts[5]

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    expectedLower = 1
    expectedUpper = 100

    (returnedLower, returnedUpper) = bbSubscriptionsFactory.getContributionBounds()

    assert returnedLower == expectedLower
    assert returnedUpper == expectedUpper

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
    deprecated = [False, False, False]
    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, deprecated, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    tokeDeployer = accounts[7]
    token = deploy.erc20Token(tokeDeployer)

    subscriptionsDeployer = accounts[8]

    bbSubscriptionsFactory.deploySubscriptions(token.address, {"from": subscriptionsDeployer})

    with reverts():
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": bbDeployer})
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": owner})
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": receiver})
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": creator})
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": bbTreasury})
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": subscriber})
        bbSubscriptionsFactory.setSubscriptionCurrency(0, 0, subscriber, token.address, {"from": tokeDeployer})
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
    deprecated = [False, False, False]
    supportedCurrencies = [token.address, accounts[8]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, deprecated, supportedCurrencies, priceMultipliers, {"from": owner})

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
    deprecated = [False, False, False]
    supportedCurrencies = [accounts[6], accounts[7]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, deprecated, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

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
    deprecated = [False, False, False]
    supportedCurrencies = [accounts[6], accounts[7]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, deprecated, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    bbSubscriptionsFactory.setContribution(0, 10, {"from": owner})

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
    deprecated = [False, False, False]
    supportedCurrencies = [accounts[6], accounts[7]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, deprecated, supportedCurrencies, priceMultipliers, {"from": owner})

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
    deprecated = [False, False, False]
    supportedCurrencies = [accounts[6], accounts[7]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, deprecated, supportedCurrencies, priceMultipliers, {"from": owner})

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
    deprecated = [False, False, False]
    supportedCurrencies = [token.address, accounts[8]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, deprecated, supportedCurrencies, priceMultipliers, {"from": owner})

    bbSubscriptionsFactory = deploy.bbSubscriptionsFactory(bbDeployer, bbProfiles, bbTiers, bbTreasury)

    bbSubscriptionsFactory.createSubscriptionProfile(0, 0, 1, {"from": owner})

    deployedSubscriptions = deploy.bbSubscriptions(bbSubscriptionsFactory, token.address)

    token.mint(1000, {"from": subscriber})

    token.approve(deployedSubscriptions.address, 10 ** 25, {"from": subscriber})

    deployedSubscriptions.subscribe(0, 0, {"from": subscriber, "value": 10 ** 18})

    assert bbSubscriptionsFactory.isSubscriptionActive(0, 0, subscriber) == True