from brownie import reverts
from scripts.josh.bbenv import bbenv
from scripts.josh.helpers import helpers

def test_createProfile(je_org):
    tx = je_org.setup_profile()
    assert je_org.profiles.totalProfiles() == 1
    assert tx.events['NewProfile']['profileId'] == 0

def test_editProfile_owner(je_org):
    tx = je_org.setup_profile()
    newOwner = je_org.coCreator
    je_org.profiles.editProfile(tx.out_.profileId, newOwner, tx._in.account, tx._in.cid, helpers.by(tx._in.account))
    assert je_org.profiles.getProfile(tx.out_.profileId)[0] == newOwner


def test_editProfile_receiver(je_org):
    tx = je_org.setup_profile()
    newReceiver = je_org.coCreator
    je_org.profiles.editProfile(tx.out_.profileId, tx._in.account, newReceiver, tx._in.cid, helpers.by(tx._in.account))
    assert je_org.profiles.getProfile(tx.out_.profileId)[1] == newReceiver


def test_editProfile_cid(je_org):
    tx = je_org.setup_profile()
    newCid = "some new cid"
    je_org.profiles.editProfile(tx.out_.profileId, tx._in.account, tx._in.account, newCid, helpers.by(tx._in.account))
    assert je_org.profiles.getProfile(tx.out_.profileId)[2] == newCid

def test_editProfile_non_owner(je_org):
    tx1 = je_org.setup_profile(account = je_org.creator)
    attacker = je_org.anons[0]
    with reverts():
        je_org.profiles.editProfile(tx1.out_.profileId, je_org.creator.address, attacker.address, tx1._in.cid, helpers.by(attacker))

def test_editProfile_outOfRange(je_org):
    tx1 = je_org.setup_profile(account = je_org.creator)
    attacker = je_org.anons[0]
    with reverts():
        je_org.profiles.editProfile(1e9, je_org.creator.address, je_org.creator.address, tx1._in.cid, helpers.by(tx1._in.account))
    with reverts():
        je_org.profiles.editProfile(1e9, je_org.creator.address, attacker.address, tx1._in.cid, helpers.by(attacker))

def test_ownersTotalProfiles(je_org):
    assert je_org.profiles.ownersTotalProfiles(je_org.creator) == 0
    
    tx1 = je_org.setup_profile(account = je_org.creator)
    assert je_org.profiles.ownersTotalProfiles(je_org.creator) == 1
    tx2 = je_org.setup_profile(account = je_org.creator)
    assert je_org.profiles.ownersTotalProfiles(je_org.creator) == 2
    tx3 = je_org.setup_profile(account = je_org.creator)
    assert je_org.profiles.ownersTotalProfiles(je_org.creator) == 3
    return [tx1.out_.profileId,tx2.out_.profileId,tx3.out_.profileId]

def test_getOwnersProfiles(je_org):
    createdIds = test_ownersTotalProfiles(je_org)
    ids = je_org.profiles.getOwnersProfiles(je_org.creator)
    assert len(createdIds) == len(ids)

    seen = []
    for id in createdIds:
        assert id in ids
        assert id not in seen
        if id in ids: seen.append(id)

    assert len(seen) == len(ids)
        
def test_address_no_profiles(je_org):
    assert len(je_org.profiles.getOwnersProfiles(je_org.anons[0])) == 0
    assert je_org.profiles.ownersTotalProfiles(je_org.anons[0]) == 0