from codecs import EncodedFile
import profile
import brownie
import string
from brownie import *
from brownie import accounts
from scripts.josh.helpers import helpers, objdict
from eth_abi import encode, decode

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
        self.DAI = DebugERC20.deploy("Dai", "DAI", {'from': bbenv.deployer})
        self.WMATIC = DebugERC20.deploy("Wrapped MATIC", "WMATIC", {'from': bbenv.deployer})
        self.WETH = DebugERC20.deploy("Wrapped ETH", "WETH", {'from': bbenv.deployer})
        self.WBTC = DebugERC20.deploy("Wrapped BTC", "WBTC", {'from': bbenv.deployer})
        self.currencies = [self.TUSD, self.DAI]
        self.allCurrencies = [self.TUSD, self.DAI, self.WMATIC, self.WETH, self.WBTC]
        self.subscriptions = objdict({})

        #set inital currencies
        for currency in self.allCurrencies:
            self.subscriptionsFactory.deploySubscriptions(currency, helpers.by(self.deployer))
            subaddr = self.subscriptionsFactory.getDeployedSubscriptions(currency)
            self.subscriptions[currency.address] = BBSubscriptions.at(subaddr)


    def performUpkeep(self, currencies=None):
        runner = bbenv.deployer
        checkUpkeepPayload = "0x" + encode( ['uint256','uint256','uint256','uint256','address'], [0, int(1e6), 1, 25, runner.address] ).hex()
        if currencies is None:
            currencies = self.currencies
        
        for currency in currencies:
            
            try:
                checkUpkeepDataRaw = self.subscriptions[currency.address].checkUpkeep(checkUpkeepPayload)
                checkUpkeepData = decode(['uint256[]', 'address'], checkUpkeepDataRaw[1])
                if checkUpkeepDataRaw[0]:
                    tx = self.subscriptions[currency.address].performUpkeep(checkUpkeepDataRaw[1], helpers.by(runner))
            except:
                pass

    def setup_profile(self, account=None, receiver=None, cid="first user cid"):
        if account is None:
            account = bbenv.creator
        if receiver is None:
            receiver = account

        tx = self.profiles.createProfile(account, receiver, cid, helpers.by(account))
        tx._in = objdict({
            'account': account,
            'receiver': receiver,
            'cid' : cid,
        })
        tx.out_ = objdict({
            'profileId': tx.events['NewProfile']['profileId'],
            'owner': tx.events['NewProfile']['owner'],
            'receiver': tx.events['NewProfile']['receiver'],
            'cid': tx.events['NewProfile']['cid']
        })
        return tx

    def get_profile(self, profileId):
        t = self.profiles.getProfile(profileId)
        return objdict({
            'profileId': profileId,
            'owner': t[0],
            'receiver': t[1],
            'cid': t[2]
        })
    
    #trash since tiers are their own thing now and are mass defined.
    #def _trash_setup_tier(self, account=None, profileId=-1, price=-1, cid="first added tier cid"):
    #    if(account == None):
    #        account = bbenv.creator
    #    if(profileId == -1):
    #        profileId = self.setup_profile(account=account, cid=helpers.randomCid(), url=helpers.randomCid()).out_.profileId
    #    if(price == -1):
    #        price = 5 * 10 ** self.TUSD.decimals()
    #    tx = self.subscriptions.createTier(profileId, price, cid, helpers.by(account))
    #    tx._in = objdict({
    #        'account': account,
    #        'profileId': profileId,
    #        'price': price,
    #        'cid' : cid
    #    })
    #    tx.out_ = objdict({
    #        'profileId': tx.events['NewTier']['profileId'],
    #        'tierId': tx.events['NewTier']['tierId'],
    #        'price': tx.events['NewTier']['price']
    #        #tx.cid = cid
    #    })
    #    try:
    #        tx.out_.cid = self.subscriptions.getTier(profileId, tx.out_.tierId)[1]
    #    except:
    #        pass
    #    return tx
    
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
        
        #"this is only temporary"
        tierSetId = self.tiers.totalTierSets(profileId) - 1

        tx.out_ = objdict({
            'tierSetId': tierSetId
        })

        return tx

    def setup_subscriptionProfile(self, profileId=None, tierSet=None, contribution=1, account=None):
        
        if(account is None):
            account = bbenv.creator
            
        
        if profileId is None:
            profileId = self.setup_profile(account=account).out_.profileId
        if tierSet is None:
            tierPrices = [1,5,10,20]
            tierCids = [helpers.randomCid(), helpers.randomCid(), helpers.randomCid(), helpers.randomCid()]
            tierCurrencies = [self.TUSD, self.DAI]
            tierPriceMultipliers = [int(10 ** self.TUSD.decimals()), int(10 ** self.DAI.decimals())]
            _tierSet = self.setup_tiers(tierPrices, tierCids, tierCurrencies, tierPriceMultipliers, profileId=profileId, account=account)
            tierSet = _tierSet.out_.tierSetId

        tx = self.subscriptionsFactory.createSubscriptionProfile(profileId, tierSet, contribution, helpers.by(account))

        tx._in = objdict({
            'account': account,
            'profileId': profileId,
            'tierSet': tierSet,
            'contribution': contribution,
            '_tierSet': _tierSet
        })

        tx.out_ = objdict({
            'profileId': tx.events['NewSubscriptionProfile']['profileId'],
            'tierSet': tx.events['NewSubscriptionProfile']['tierSetId'],
            'contribution': tx.events['NewSubscriptionProfile']['contribution'],
        })

        return tx
    def setup_subscription(self, account=None, creator=None, profileId=None, tierId=None, currency=None):
        isAuto = False
        if(account is None):
            account = bbenv.anons[0]
            isAuto = True
        if(creator is None):
            creator = bbenv.creator
        if(currency is None):
            currency = self.TUSD.address
            isAuto = True

        if(profileId is None):
            _subProfile = self.setup_subscriptionProfile(account=creator)
            profileId = _subProfile._in.profileId

        if(tierId is None):
            tierId = 0

        if isAuto:
            c = DebugERC20.at(currency)
            c.mint(int(1e6 * 10 ** c.decimals()), helpers.by(account))
            c.approve(self.subscriptions[currency], helpers.MAXUINT256, helpers.by(account))

        gas = self.subscriptions[currency].getSubscriptionGasRequirement()
        subContract = BBSubscriptions.at(self.subscriptions[currency])
        tx = subContract.subscribe(profileId, tierId, helpers.by(account, {'value': gas}))

        tx._in = objdict({
            'account': account,
            'creator': creator,
            'profileId': profileId,
            'tierId': tierId,
            'currency': currency
        })
        
        tx.out_ = objdict({
            'profileId': tx.events['Subscribed']['profileId'],
            'tierId': tx.events['Subscribed']['tierId'],
            'subscriber': tx.events['Subscribed']['subscriber']
        })

        return tx;

    def _trash_setup_subscription(self, account=None, creator=None, profileId=-1, tierId=-1, currency=None):
        if(account is None):
            account = bbenv.anons[0]
        if(creator is None):
            creator = bbenv.creator
        if(currency is None):
            currency = self.TUSD.address

        if(profileId == -1):
            profileId = self.setup_profile(account=creator, url=helpers.randomCid()).out_.profileId

        if(tierId == -1):
            tier = self.setup_tier(account=creator, profileId=profileId)
            tierId = tier.out_.tierId
        else:
            _tmp = self.subscriptions.getTier(profileId, tierId)
            tier = objdict({})
            tier.out_ = objdict({
                'profileId': profileId,
                'tierId': tierId,
                'price': _tmp[0]
            })

            tier._in = objdict({
                'profileId': profileId,
                'tierId': tierId,
                'price': _tmp[0]
            })
            tierID = tier.out_.tierId

        token = DebugERC20.at(currency)
        token.mint(tier._in.price * 120, helpers.by(account))
        token.approve(self.subscriptions.address, tier._in.price * 60, helpers.by(account))
        sub = self.subscriptions.subscribe(tier._in.profileId, tier.out_.tierId, currency, helpers.by(account, {'value': self.subscriptions[currency].getSubscriptionGasRequirement()}))
        sub._in = objdict({
            'account': account,
            'creator': creator,
            'profileId': profileId,
            'tierId': tierId,
            'currency': currency
        })
        if(helpers.keyExists(sub.events, ['NewSubscription', 'profileId']) is not None):
            sub.out_ = objdict({
                'profileId': sub.events['NewSubscription']['profileId'],
                'tierId': sub.events['NewSubscription']['tierId'],
                'subscriptionIndex': sub.events['NewSubscription']['subscriptionId'],
                'subscriptionId': sub.events['NewSubscription']['subscriptionId'],
                #'currency': currency
            })
        try:
            sub.out_.currency = self.subscriptions.getSubscription(tier.profileId, tier.tierId, account.address)[3]
        except:
            pass
        #sub.account = account
        #sub.profileId = sub.events['NewSubscription']['profileId']
        #sub.tierId = sub.events['NewSubscription']['tierId']
        #sub.subscriptionIndex = sub.events['NewSubscription']['subscriptionIndex']
        #sub.currency = currency
        return sub
