from brownie import BBProfiles, BBPosts, BBTiers, BBSubscriptionsFactory, BBSubscriptions, DebugERC20

class deploy:
    def bbProfiles(deployer):
        contract = BBProfiles.deploy({"from": deployer})
        print("BBProfiles address: ", contract.address)
        return contract

    def bbPosts(deployer, bbProfiles):
        contract = BBPosts.deploy(bbProfiles, {"from": deployer})
        print("BBPosts address: ", contract.address)
        return contract

    def bbTiers(deployer, bbProfiles):
        contract = BBTiers.deploy(bbProfiles, {"from": deployer})
        print("BBTiers address: ", contract.address)
        return contract

    def bbSubscriptionsFactory(deployer, bbProfiles, bbTiers, bbTreasury):
        contract = BBSubscriptionsFactory.deploy(bbProfiles, bbTiers, bbTreasury, {"from": deployer})
        print("BBSubscriptionsFactory address: ", contract.address)
        return contract

    def bbSubscriptions(bbSubscriptionsFactory, currency):
        contractAddress = bbSubscriptionsFactory.deploySubscriptions.call(currency)
        bbSubscriptionsFactory.deploySubscriptions(currency)
        contract = BBSubscriptions.at(contractAddress)
        print("BBSubscriptions address: ", contract.address)
        return contract

    def erc20Token(deployer):
        contract = DebugERC20.deploy("ERC20 Token", "ERC20", {"from": deployer})
        print("ERC20 Token address: ", contract.address)
        return contract