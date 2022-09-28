import pytest
from brownie import network,reverts
from scripts.josh.bbenv import bbenv, helpers
from eth_abi import encode

def test_subfactory_init(je_org):
    sf = je_org.subscriptionsFactory
    assert sf.getTreasuryOwner() == je_org.deployer.address
    assert sf.getGasPriceOwner() == je_org.deployer.address
    assert sf.getUpkeepGasRequirementOwner() == je_org.deployer.address

def test_subfactory_change_owners(je_org):
    sf = je_org.subscriptionsFactory
    oldOwner = je_org.deployer.address
    newOwner = je_org.anons[0].address
    
    sf.setTreasuryOwner(newOwner, helpers.by(oldOwner))
    assert sf.getTreasuryOwner() == newOwner

    sf.setGasPriceOwner(newOwner, helpers.by(oldOwner))
    assert sf.getGasPriceOwner() == newOwner

    sf.setUpkeepGasRequirementOwner(newOwner, helpers.by(oldOwner))
    assert sf.getUpkeepGasRequirementOwner() == newOwner

def test_subfactory_change_owners_non_owner(je_org):
    sf = je_org.subscriptionsFactory
    oldOwner = je_org.anons[0].address
    newOwner = je_org.anons[1].address
    
    with reverts():
        sf.setTreasuryOwner(newOwner, helpers.by(oldOwner))
        assert sf.getTreasuryOwner() == newOwner

    with reverts():
        sf.setGasPriceOwner(newOwner, helpers.by(oldOwner))
        assert sf.getGasPriceOwner() == newOwner

    with reverts():
        sf.setUpkeepGasRequirementOwner(newOwner, helpers.by(oldOwner))
        assert sf.getUpkeepGasRequirementOwner() == newOwner

def test_subfactory_change_treasury(je_org):
    je_org.subscriptionsFactory.setTreasury(je_org.anons[0].address, helpers.by(je_org.deployer))
    
def test_subfactory_change_treasury_non_owner(je_org):
    with reverts():
        je_org.subscriptionsFactory.setTreasury(je_org.anons[0].address, helpers.by(je_org.anons[0]))

def test_subfactory_change_gas(je_org):
    je_org.subscriptionsFactory.setUpkeepGasRequirement(je_org.TUSD.address, 133700, helpers.by(je_org.deployer))

def test_subfactory_change_gas_non_owner(je_org):
    with reverts():
        je_org.subscriptionsFactory.setUpkeepGasRequirement(je_org.TUSD.address, 133700, helpers.by(je_org.anons[0]))

def test_subfactory_change_gas_outside_limit(je_org):
    with reverts():
        je_org.subscriptionsFactory.setUpkeepGasRequirement(je_org.TUSD.address, 1e16, helpers.by(je_org.deployer))


def test_subscriptionContracts(je_org, DebugERC20):
    assert je_org.subscriptionsFactory.getDeployedSubscriptions(je_org.TUSD) == je_org.subscriptions[je_org.TUSD.address]

    badMoney = DebugERC20.deploy("bad", "money", helpers.by(je_org.deployer))
    assert je_org.subscriptionsFactory.isSubscriptionsDeployed(badMoney) == False
    with reverts():
        je_org.subscriptionsFactory.getDeployedSubscriptions(badMoney)

def test_subFactoryVariables(je_org):
    assert je_org.subscriptionsFactory.getGracePeriod() == 172800
    assert je_org.subscriptionsFactory.getContributionBounds()[0] == 1
    assert je_org.subscriptionsFactory.getContributionBounds()[1] == 100

def test_deployedSubscriptionGasRequirements(je_org):
    gasprice = je_org.subscriptionsFactory.getGasPrice()
    assert je_org.subscriptions[je_org.TUSD.address].getUpkeepGasRequirement() == 225000
    assert je_org.subscriptions[je_org.TUSD.address].getSubscriptionGasRequirement() == 225000 * gasprice * 60

    je_org.subscriptionsFactory.setUpkeepGasRequirement(je_org.TUSD.address, 1, helpers.by(je_org.deployer))
    assert je_org.subscriptions[je_org.TUSD.address].getUpkeepGasRequirement() == 1
    assert je_org.subscriptions[je_org.TUSD.address].getSubscriptionGasRequirement() == 1 * gasprice * 60

    with reverts():
        je_org.subscriptionsFactory.setUpkeepGasRequirement(je_org.TUSD.address, 7331, helpers.by(je_org.anons[0]))

    with reverts():
        je_org.subscriptions[je_org.TUSD.address].setUpkeepGasRequirement(1337, helpers.by(je_org.anons[0]))

    with reverts():
        je_org.subscriptions[je_org.TUSD.address].setUpkeepGasRequirement(1337, helpers.by(je_org.deployer))

    assert je_org.subscriptions[je_org.TUSD.address].getUpkeepGasRequirement() == 1

def test_getSetSubscriptionCurrency(je_org):
    subber = je_org.setup_subscription()
    account = subber._in.account
    profileId = subber._in.profileId
    tierId = subber._in.tierId
    ogCurrency = subber._in.currency

    assert je_org.subscriptionsFactory.getSubscriptionCurrency(profileId, tierId, account) == ogCurrency

def test_isSubscriptionActive(je_org):
    subber = je_org.setup_subscription()

    assert je_org.subscriptionsFactory.isSubscriptionActive(subber._in.profileId, subber._in.tierId, subber._in.account)
    assert je_org.subscriptionsFactory.isSubscriptionActive(subber._in.profileId, subber._in.tierId + 1, subber._in.account) is False
    with reverts():
        assert je_org.subscriptionsFactory.isSubscriptionActive(1e9, subber._in.tierId, subber._in.account) is False

    helpers.advance_time(33)
    assert je_org.subscriptionsFactory.isSubscriptionActive(subber._in.profileId, subber._in.tierId, subber._in.account) is False
    je_org.performUpkeep()
    assert je_org.subscriptionsFactory.isSubscriptionActive(subber._in.profileId, subber._in.tierId, subber._in.account)
