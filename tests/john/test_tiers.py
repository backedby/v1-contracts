from brownie import accounts, reverts
from scripts.john.deploy import deploy
import random

def test_create_tier():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    unauthorized = accounts[4]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    with reverts():
        bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": bbDeployer})
        bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": receiver})
        bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": creator})
        bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": unauthorized})

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})


def test_edit_tier():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    unauthorized = accounts[4]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    editedTierPrices = [2, 4, 8]
    editedTierCids = ["edited_tier_0", "edited_tier_1", "edited_tier_2"]

    with reverts():
        bbTiers.editTiers(0, 0, editedTierPrices, editedTierCids, {"from": bbDeployer})
        bbTiers.editTiers(0, 0, editedTierPrices, editedTierCids, {"from": receiver})
        bbTiers.editTiers(0, 0, editedTierPrices, editedTierCids, {"from": creator})
        bbTiers.editTiers(0, 0, editedTierPrices, editedTierCids, {"from": unauthorized})

    bbTiers.editTiers(0, 0, editedTierPrices, editedTierCids, {"from": owner})

def test_set_supported_currencies():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    unauthorized = accounts[4]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    editedSupportedCurrencies = [accounts[7], accounts[8]]
    editedPriceMultipliers = [2000, 4500]

    with reverts():
        bbTiers.setSupportedCurrencies(0, 0, editedSupportedCurrencies, editedPriceMultipliers, {"from": bbDeployer})
        bbTiers.setSupportedCurrencies(0, 0, editedSupportedCurrencies, editedPriceMultipliers, {"from": receiver})
        bbTiers.setSupportedCurrencies(0, 0, editedSupportedCurrencies, editedPriceMultipliers, {"from": creator})
        bbTiers.setSupportedCurrencies(0, 0, editedSupportedCurrencies, editedPriceMultipliers, {"from": unauthorized})

    bbTiers.setSupportedCurrencies(0, 0, editedSupportedCurrencies, editedPriceMultipliers, {"from": owner})

def test_get_tier_cid():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    for i in range(len(tierCids)):
        assert bbTiers.getTierCid(0, 0, i) == tierCids[i]

def test_get_tier_price():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    for i in range(len(supportedCurrencies)):
        for t in range(len(tierPrices)):
            assert bbTiers.getTierPrice(0, 0, t, supportedCurrencies[i]) == tierPrices[t] * priceMultipliers[i]

def test_get_tier_set():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    (returnedPrices, returnedCids) = bbTiers.getTierSet(0, 0)

    assert returnedPrices == tierPrices
    assert returnedCids == tierCids

def test_total_tiers():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    with reverts():
        bbTiers.totalTiers(0, 0)

    tierPrices = []
    tierCids = []
    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    tierCount = random.randint(1, 10)

    for i in range(tierCount):
        tierPrices.append(10 + i)
        tierCids.append("tier_" + str(i))

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    assert bbTiers.totalTiers(0, 0) == tierCount

def test_total_tier_sets():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    supportedCurrencies = [accounts[5], accounts[6]]    
    priceMultipliers = [100, 150]

    tierSetCount = random.randint(1, 10)

    for i in range(tierSetCount):
        tierPrices = [10 + i, 25 + i, 50 + i]
        tierCids = ["tier_" + str(i) + "_0", "tier_" + str(i) + "_1", "tier_" + str(i) + "_2"]
        bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    assert bbTiers.totalTierSets(0) == tierSetCount

def test_get_currency_multiplier():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = []
    priceMultipliers = []

    supportedCurrenciesCount = random.randint(1, 5)

    for i in range(supportedCurrenciesCount):
        supportedCurrencies.append(accounts[4 + i])
        priceMultipliers.append(100 + i)

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    for i in range(supportedCurrenciesCount):
        with reverts():
            bbTiers.getCurrencyMultiplier(0, 0, accounts[4 + supportedCurrenciesCount + i])

    for i in range(supportedCurrenciesCount):
        assert bbTiers.getCurrencyMultiplier(0, 0, supportedCurrencies[i]) == priceMultipliers[i]

def test_is_currency_supported():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbTiers = deploy.bbTiers(bbDeployer, bbProfiles)

    tierPrices = [10, 25, 50]
    tierCids = ["tier_0", "tier_1", "tier_2"]
    supportedCurrencies = []
    priceMultipliers = []

    supportedCurrenciesCount = random.randint(1, 5)

    for i in range(supportedCurrenciesCount):
        supportedCurrencies.append(accounts[4 + i])
        priceMultipliers.append(100 + i)

    bbTiers.createTiers(0, tierPrices, tierCids, supportedCurrencies, priceMultipliers, {"from": owner})

    for i in range(supportedCurrenciesCount):
        assert bbTiers.isCurrencySupported(0, 0, accounts[4 + supportedCurrenciesCount + i]) == False

    for i in range(supportedCurrenciesCount):
        assert bbTiers.isCurrencySupported(0, 0, supportedCurrencies[i]) == True