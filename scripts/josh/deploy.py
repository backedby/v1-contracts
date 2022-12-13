from brownie import *
import os

def deploy_backedby(deployer):
    from0 = {'from': deployer}
    profiles = BBProfiles.deploy(from0)
    posts = BBPosts.deploy(profiles, from0)
    tiers = BBTiers.deploy(profiles, from0)
    subfactory = BBSubscriptionsFactory.deploy(profiles, tiers, deployer, from0)

    gasOracle = DebugGasOracle.deploy(from0)
    subfactory.setGasOracle(gasOracle, from0).wait(2)
        
    tokens = [
        {'name': "USDC", 'address': "0x8f7116CA03AEB48547d0E2EdD3Faa73bfB232538"},
        {'name': "USDT", 'address': "0x0afF29eeCf746EC239C8DA3E8e630F46FCaBC48e"},
        {'name': "DAI", 'address': "0xd393b1E02dA9831Ff419e22eA105aAe4c47E1253"},
        {'name': "TUSD", 'address': "0x3c75bd0e659b8bd426b3b9a1d93b75bb9c97de10"}
    ]

    for i, token in enumerate(tokens):
        tx = subfactory.deploySubscriptions(token['address'], from0)
        tx.wait(2)
        token['subaddress'] = subfactory.getDeployedSubscriptions(token['address'])
        #remove gas change for live
        #subfactory.setSubscriptionFee(token['address'], 1, from0)

    print("profiles", profiles)
    print("posts", posts)
    print("tiers", tiers)
    print("subfactory", subfactory)
    print("gas oracle", gasOracle)

    
    for i, token in enumerate(tokens):
        print(token['name'], token['address'], "=>", token['subaddress'])


def main():
    
    if(os.environ.get("DEPLOYER_PRIVATEKEY") != None):
        deployer = accounts.add(os.environ.get("DEPLOYER_PRIVATEKEY"))
    elif(len(accounts) > 0):
        deployer = accounts[0]

    if(deployer.balance() >= 1e17):
        deploy_backedby(deployer)