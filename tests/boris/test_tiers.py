from brownie import accounts, reverts
from scripts.boris.bbenv import bbenv
from scripts.boris.helpers import helpers

def test_createTierSet(org):
    #initial conditions
    tx = org.setup_profile(bbenv.creator, bbenv.creator, "first cid")
    assert org.tiers.totalTierSets(tx.out_.profileId) == 0
    #creating first tier set
    supportedCurrencies = [org.TUSD.address]
    priceMultipliers = [org.TUSD.decimals()]
    for i in range(5):
        prices = [1+i,5+i,10+i,20+i]
        cids = ['a%s'%i, 'b%s'%i, 'c%s'%i, 'd%s'%i]
        depreciatedTiers = [False]*len(prices)
        tier_tx = org.tiers.createTiers(tx.out_.profileId, prices, cids, depreciatedTiers, supportedCurrencies, priceMultipliers, {'from': bbenv.creator})
        assert tier_tx.events["NewTierSet"]["profileId"] == tx.out_.profileId
        assert tier_tx.events["NewTierSet"]["tierSetId"] == i
        assert tier_tx.events["SupportedCurrencyAdded"]["profileId"] == tx.out_.profileId
        assert tier_tx.events["SupportedCurrencyAdded"]["tierSetId"] == i
        assert tier_tx.events["SupportedCurrencyAdded"]["currency"] == org.TUSD.address
        assert tier_tx.events["SupportedCurrencyAdded"]["priceMultiplier"] == org.TUSD.decimals()
        assert org.tiers.totalTierSets(tx.out_.profileId) == i+1
        assert org.tiers.getTierSet(tx.out_.profileId, i) == (prices, cids, depreciatedTiers)
        assert org.tiers.isCurrencySupported(tx.out_.profileId, i, org.TUSD.address)
        for j in range(len(prices)):
            assert org.tiers.getTier(tx.out_.profileId, i, j, org.TUSD.address)[0] == cids[j]
            assert org.tiers.getTier(tx.out_.profileId, i, j, org.TUSD.address)[1] == prices[j] * org.TUSD.decimals()
    
    # profile id doesn't exist     
    with reverts():  
        failed_tx = org.tiers.createTiers(5, prices, cids, depreciatedTiers, supportedCurrencies, priceMultipliers, {'from': bbenv.creator})
    # tx initiated by someone without ownership of the profile     
    with reverts():  
        failed_tx = org.tiers.createTiers(tx.out_.profileId, prices, cids, depreciatedTiers, supportedCurrencies, priceMultipliers, {'from': bbenv.coCreator})
    # mismatch of price and cid length     
    with reverts():
        failed_tx = org.tiers.createTiers(tx.out_.profileId, prices[:2], cids, depreciatedTiers, supportedCurrencies, priceMultipliers, {'from': bbenv.creator})
    # mismatch of supported currency and pricemultiplier length   
    with reverts(): 
        failed_tx = org.tiers.createTiers(tx.out_.profileId, prices, cids, depreciatedTiers, supportedCurrencies, [], {'from': bbenv.creator})

def test_editTierSet(org):
    test_createTierSet(org)
    newPrices = [5, 10, 15, 25]
    newCids = ['w', 'x', 'y', 'z']
    depreciatedTiers = [False,False,False,False]
    edit_tx = org.tiers.editTiers(0, 0, newPrices, newCids, depreciatedTiers, {'from': bbenv.creator})
    assert edit_tx.events["EditTierSet"]["profileId"] == 0
    assert edit_tx.events["EditTierSet"]["tierSetId"] == 0
    for j in range(len(newPrices)):
        assert org.tiers.getTier(0, 0, j, org.TUSD.address)[0] == newCids[j]
        assert org.tiers.getTier(0, 0, j, org.TUSD.address)[1] == newPrices[j] * org.TUSD.decimals()

    # profile id doesn't exist   
    with reverts(): 
        failed_tx = org.tiers.editTiers(5, 1, newPrices, newCids, depreciatedTiers, {'from': bbenv.creator})
    # tx initiated by someone without ownership of the profile 
    with reverts():
        failed_tx = org.tiers.editTiers(0, 1, newPrices, newCids, depreciatedTiers, {'from': bbenv.coCreator})
    # mismatch of price and cid length 
    with reverts():
        failed_tx = org.tiers.editTiers(0, 1, newPrices[0:2], newCids, depreciatedTiers, {'from': bbenv.creator})
