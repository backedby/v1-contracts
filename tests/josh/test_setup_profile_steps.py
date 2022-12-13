import pytest
from brownie import accounts,reverts
from scripts.josh.bbenv import bbenv, helpers

def test_ProfileSetupHelper(je_org, ProfileSetupHelper):
    defaultPrices = [1,5,10,20]
    defaultCids = ["aa", "bb", "cc", "dd"]
    defaultDepreciated = [False,False,False,False]
    defaultCur = [je_org.TUSD, je_org.DAI]
    defaultMul = [10 ** je_org.TUSD.decimals(), 10 ** je_org.DAI.decimals()]
    
    pf = ProfileSetupHelper.deploy(je_org.profiles, je_org.tiers, je_org.subscriptionsFactory, defaultPrices, defaultCids, defaultDepreciated, defaultCur, defaultMul, helpers.by(je_org.deployer))

    spTx1 = pf.SimpleProfileSetup("profile0", 3, helpers.by(je_org.anons[0]))
    assert spTx1.return_value[0] == 0
    assert je_org.subscriptionsFactory.getSubscriptionProfile(spTx1.return_value[0])[0] == spTx1.return_value[1]
    assert je_org.subscriptionsFactory.getSubscriptionProfile(spTx1.return_value[0])[1] == 3
    assert je_org.tiers.getTier(spTx1.return_value[0], spTx1.return_value[1], 3, defaultCur[1])[1] == 20e18
    assert je_org.profiles.getProfile(spTx1.return_value[0])[0] == je_org.anons[0].address

    spTx2 = pf.AdvancedProfileSetup("profile1", [1,5], ['z', 'x'], [False, False], 2, helpers.by(je_org.anons[1]))
    assert spTx2.return_value[0] == 1
    assert je_org.subscriptionsFactory.getSubscriptionProfile(spTx2.return_value[0])[0] == spTx2.return_value[1]
    assert je_org.subscriptionsFactory.getSubscriptionProfile(spTx2.return_value[0])[1] == 2
    assert je_org.tiers.getTier(spTx2.return_value[0], spTx2.return_value[1], 1, defaultCur[1])[1] == 5e18
    assert je_org.profiles.getProfile(spTx2.return_value[0])[0] == je_org.anons[1].address