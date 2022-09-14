from brownie import accounts, reverts
from scripts.boris.bbenv import bbenv
from scripts.boris.helpers import helpers

def test_createProfiles(org):
    #initial conditions
    assert org.profiles.totalProfiles() == 0
    assert org.profiles.ownersTotalProfiles(bbenv.creator) == 0
    #first profile testing iteration of mappings
    tx = org.setup_profile(bbenv.creator, bbenv.creator, "first cid")
    assert org.profiles.totalProfiles() == 1
    assert org.profiles.ownersTotalProfiles(bbenv.creator) == 1
    assert org.profiles.getOwnersProfiles(bbenv.creator) == [0]
    assert org.profiles.getProfile(0) == (bbenv.creator, bbenv.creator, "first cid")
    assert tx.events['NewProfile']['profileId'] == 0
    assert tx.events['NewProfile']['owner'] == bbenv.creator
    assert tx.events['NewProfile']['receiver'] == bbenv.creator
    assert tx.events['NewProfile']['cid'] == "first cid"
    #second profile testing iteration of mappings
    tx2 = org.setup_profile(bbenv.creator, bbenv.creator, "second cid")
    assert org.profiles.totalProfiles() == 2
    assert org.profiles.ownersTotalProfiles(bbenv.creator) == 2
    assert org.profiles.getOwnersProfiles(bbenv.creator) == [0,1]
    assert org.profiles.getProfile(0) == (bbenv.creator, bbenv.creator, "first cid")
    assert org.profiles.getProfile(1) == (bbenv.creator, bbenv.creator, "second cid")
    assert tx2.events['NewProfile']['profileId'] == 1
    assert tx2.events['NewProfile']['owner'] == bbenv.creator
    assert tx2.events['NewProfile']['receiver'] == bbenv.creator
    assert tx2.events['NewProfile']['cid'] == "second cid"
    #profile does not exist
    with reverts():
        org.profiles.getProfile(2)

def test_editProfile(org):
    #initial conditions
    assert org.profiles.totalProfiles() == 0 
    assert org.profiles.ownersTotalProfiles(bbenv.creator) == 0
    assert org.profiles.ownersTotalProfiles(bbenv.coCreator) == 0
    #first profile
    tx = org.setup_profile(bbenv.creator, bbenv.creator, "first cid")
    #testing transfer of profile to new creator, edits of all parameters
    tx2 = org.profiles.editProfile(tx.out_.profileId, bbenv.coCreator, bbenv.coCreator, "new cid", {'from': bbenv.creator})
    assert tx2.events['EditProfile']['profileId'] == tx.out_.profileId
    assert tx2.events['EditProfile']['owner'] == bbenv.coCreator
    assert tx2.events['EditProfile']['receiver'] == bbenv.coCreator
    assert tx2.events['EditProfile']['cid'] == "new cid"
    assert org.profiles.totalProfiles() == 1
    #correct mapping changes for transfer of ownership
    assert org.profiles.ownersTotalProfiles(bbenv.creator) == 0
    assert org.profiles.ownersTotalProfiles(bbenv.coCreator) == 1
    assert org.profiles.getProfile(0) == (bbenv.coCreator, bbenv.coCreator, "new cid")
    
    #original owner no longer has access to edit
    with reverts():
        tx3 = org.profiles.editProfile(tx.out_.profileId, bbenv.creator, bbenv.creator, "new cid 2", {'from': bbenv.creator})

