import pytest
from brownie import network,reverts
from scripts.josh.bbenv import bbenv, helpers
from eth_abi import encode

def test_subfactory_change_treasury(je_org):
    je_org.subscriptionsFactory.setTreasury(je_org.anons[0].address, helpers.by(je_org.deployer))
    
def test_subfactory_change_treasury_non_owner(je_org):
    with reverts():
        je_org.subscriptionsFactory.setTreasury(je_org.anons[0].address, helpers.by(je_org.anons[0]))


def test_subfactory_change_gas(je_org):
    je_org.subscriptionsFactory.setSubscriptionGasRequirement(je_org.TUSD.address, 133700, helpers.by(je_org.deployer))

def test_subfactory_change_gas_non_owner(je_org):
    with reverts():
        je_org.subscriptionsFactory.setSubscriptionGasRequirement(je_org.TUSD.address, 133700, helpers.by(je_org.anons[0]))

def test_subfactory_change_gas_outside_limit(je_org):
    with reverts():
        je_org.subscriptionsFactory.setSubscriptionGasRequirement(je_org.TUSD.address, 1e16, helpers.by(je_org.deployer))


def test_subscriptionContracts(je_org, DebugERC20):
    assert je_org.subscriptionsFactory.getDeployedSubscriptions(je_org.TUSD) == je_org.subscriptions[je_org.TUSD.address]

    badMoney = DebugERC20.deploy("bad", "money", helpers.by(je_org.deployer))
    assert je_org.subscriptionsFactory.isSubscriptionsDeployed(badMoney) == False
    with reverts():
        je_org.subscriptionsFactory.getDeployedSubscriptions(badMoney)

def testSubFactoryVariables(je_org):
    assert je_org.subscriptionsFactory.getGracePeriod() == 172800
    assert je_org.subscriptionsFactory.getContributionBounds()[0] == 1
    assert je_org.subscriptionsFactory.getContributionBounds()[1] == 100
    #assert je_org.subscriptionsFactory.getSubscriptionGasRequirement() == 225000
    #assert je_org.subscriptionsFactory.getSubscriptionGasEstimate(network.gas_price()) == 225000 * network.gas_price() * 60

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
