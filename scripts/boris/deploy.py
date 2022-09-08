from brownie import accounts, BBProfiles, BBTiers, BBSubscriptionsFactory, BBPosts

def main():
    deployment_account = accounts.load('deployment_account')
    profiles = BBProfiles.deploy({'from': deployment_account})
    tiers = BBTiers.deploy(profiles, {'from': deployment_account})
    subscriptionsFactory = BBSubscriptionsFactory.deploy(profiles, tiers, deployment_account, {'from': deployment_account})
    posts = BBPosts.deploy(profiles, {'from': deployment_account})
    currency = "0x3c75bD0E659B8bD426B3B9a1D93B75BB9C97dE10"
    subscriptionsFactory.deploySubscriptions(currency, {'from': deployment_account})