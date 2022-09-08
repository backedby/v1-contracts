import brownie
from brownie import accounts, BackedByCore, TokenFaucet

def deploy_backedby(deployer):
    backedby = BackedByCore.deploy({"from": deployer})
    print("Deployer: ", deployer)
    print("BackedBy contract: ", backedby.address)
    return backedby

def deploy_backedby_env(deploy):
    backedby = backedby

def deploy_token_faucet(deployer):
    usdFaucet = TokenFaucet.deploy({"from": deployer})
    usdToken = brownie.interface.IERC20(usdFaucet.tokenAddress())
    return (usdFaucet, usdToken)

def main():
    deploy_backedby(accounts[0])