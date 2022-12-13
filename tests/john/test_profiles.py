from brownie import accounts, reverts
from scripts.john.deploy import deploy  

def test_create_profile():
    bbDeployer = accounts[0]
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    cid = "test_cid"
    
    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, cid, {"from": creator})

def test_edit_profile():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    cid = "test_cid"
    
    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, cid, {"from": creator})

    editedOwner = accounts[4]
    editedReceiver = accounts[5]
    unauthorized = accounts[6]
    editedCid = "edited_cid"

    with reverts():
        bbProfiles.editProfile(0, editedOwner, editedReceiver, editedCid, {"from": unauthorized})
        bbProfiles.editProfile(0, editedOwner, editedReceiver, editedCid, {"from": creator})
        bbProfiles.editProfile(0, editedOwner, editedReceiver, editedCid, {"from": receiver})

    bbProfiles.editProfile(0, editedOwner, editedReceiver, editedCid, {"from": owner}) 

def test_total_profiles():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    cid = "test_cid"
    
    bbProfiles = deploy.bbProfiles(bbDeployer)

    assert bbProfiles.totalProfiles() == 0

    bbProfiles.createProfile(owner, receiver, cid, {"from": creator})

    assert bbProfiles.totalProfiles() == 1

def test_get_profile():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    cid = "test_cid"
    
    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, cid, {"from": creator})

    (returnedOwner, returnedReceiver, returnedCid) = bbProfiles.getProfile(0) 

    assert returnedOwner == owner
    assert returnedReceiver == receiver
    assert returnedCid == cid

def test_get_edited_profile():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    cid = "test_cid"
    
    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, cid, {"from": creator})

    (returnedOwner, returnedReceiver, returnedCid) = bbProfiles.getProfile(0) 

    assert returnedOwner == owner
    assert returnedReceiver == receiver
    assert returnedCid == cid

    editedOwner = accounts[4]
    editedReceiver = accounts[5]
    unauthorized = accounts[6]
    editedCid = "edited_cid"

    with reverts():
        bbProfiles.editProfile(0, editedOwner, editedReceiver, editedCid, {"from": unauthorized})
        bbProfiles.editProfile(0, editedOwner, editedReceiver, editedCid, {"from": creator})
        bbProfiles.editProfile(0, editedOwner, editedReceiver, editedCid, {"from": receiver})

    bbProfiles.editProfile(0, editedOwner, editedReceiver, editedCid, {"from": owner})

    (returnedOwner, returnedReceiver, returnedCid) = bbProfiles.getProfile(0)

    assert returnedOwner == editedOwner
    assert returnedReceiver == editedReceiver
    assert returnedCid == editedCid

def test_get_owners_profiles():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    cid = "test_cid"
    
    bbProfiles = deploy.bbProfiles(bbDeployer)

    assert bbProfiles.getOwnersProfiles(owner) == []
    assert bbProfiles.getOwnersProfiles(receiver) == []
    assert bbProfiles.getOwnersProfiles(creator) == []

    bbProfiles.createProfile(owner, receiver, cid, {"from": creator})

    assert bbProfiles.getOwnersProfiles(owner) == [0]
    assert bbProfiles.getOwnersProfiles(receiver) == []
    assert bbProfiles.getOwnersProfiles(creator) == []

def test_owners_total_profiles():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    cid = "test_cid"
    
    bbProfiles = deploy.bbProfiles(bbDeployer)

    assert bbProfiles.ownersTotalProfiles(owner) == 0
    assert bbProfiles.ownersTotalProfiles(receiver) == 0
    assert bbProfiles.ownersTotalProfiles(creator) == 0

    bbProfiles.createProfile(owner, receiver, cid, {"from": creator})

    assert bbProfiles.ownersTotalProfiles(owner) == 1
    assert bbProfiles.ownersTotalProfiles(receiver) == 0
    assert bbProfiles.ownersTotalProfiles(creator) == 0