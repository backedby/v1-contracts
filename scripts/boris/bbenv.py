import brownie
import string
from brownie import *
from brownie import accounts, BBProfiles
from scripts.boris.helpers import helpers, objdict

class bbenv:
    inited = 0
    def __init__(self):
        bbenv.inited += 1
        bbenv.deployer = accounts[0]
        bbenv.treasury = accounts[1]
        bbenv.backedByStaff = accounts[2:5]
        bbenv.creator = accounts[6]
        bbenv.coCreator = accounts[7]
        bbenv.subs = accounts[8:13]
        bbenv.anons = accounts[14:]

        self.profiles = BBProfiles.deploy({'from': bbenv.deployer})
        self.tiers = BBTiers.deploy(self.profiles, {'from': bbenv.deployer})
        self.subscriptionsFactory = BBSubscriptionsFactory.deploy(self.profiles, self.tiers, bbenv.treasury, {'from': bbenv.deployer})
        self.posts = BBPosts.deploy(self.profiles, {'from': bbenv.deployer})
        
        self.TUSD = DebugERC20.deploy("Test USD", "TUSD", {'from': bbenv.deployer})
        self.TUSD.setDecimal(6)
        # self.posts = BackedByPosts.deploy(self.profiles, {'from': bbenv.deployer})
        # self.subscriptions = BackedBySubscriptions.deploy(self.core, self.profiles, {'from': bbenv.deployer})
        # #self.dao = 
        
        # self.TUSD = DebugERC20.deploy("Test USD", "TUSD", {'from': bbenv.deployer})
        # self.DAI = DebugERC20.deploy("Dai", "DAI", {'from': bbenv.deployer})
        # self.WMATIC = DebugERC20.deploy("Wrapped MATIC", "WMATIC", {'from': bbenv.deployer})

        # #set base currency
        # self.core.addSupportedCurrency(self.TUSD.address)
    
    def setup_profile(self, owner, receiver, cid):
        tx = self.profiles.createProfile(owner, receiver, cid)
        tx._in = objdict({
            'owner': owner,
            'receiver' : receiver,
            'cid': cid
        })
        tx.out_ = objdict({
            'profileId': tx.events['NewProfile']['profileId'],
            'owner': tx.events['NewProfile']['owner'],
            'receiver': tx.events['NewProfile']['receiver'],
            'cid': tx.events['NewProfile']['cid']
        })
        try:
            _tmp = self.profiles.getProfile(tx.out_.profileId)
            tx.out_.owner = _tmp[0]
            tx.out_.receiver = _tmp[1]
            tx.out_.cid = _tmp[2]
        except:
            pass
        return tx

    
    def setup_tiers(self, prices, cids, supportedCurrencies, priceMultipliers, profileId=None, account=None):
        if len(prices) != len(cids):
            raise Exception("prices and cids is required to be the same length")

        if account is None:
            account = bbenv.creator

        if profileId is None:
            profileId = self.setup_profile(account=account).out_.profileId
        
        tx = self.tiers.createTiers(profileId, prices, cids, supportedCurrencies, priceMultipliers, helpers.by(account))

        tx._in = objdict({
            'account': account,
            'profileId': profileId,
            'prices': prices,
            'cids': cids,
            'supportedCurrencies': supportedCurrencies,
            'priceMultipliers': priceMultipliers
        })

        tx.out_ = objdict({
            'tierSetId': tierSetId
        })

        return tx