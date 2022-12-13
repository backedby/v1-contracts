from brownie import accounts, reverts
from scripts.john.deploy import deploy
import random

def test_create_post():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    unauthorized = accounts[4]
    profileCid = "test_profile_cid"
    postCid = "test_post_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbPosts = deploy.bbPosts(bbDeployer, bbProfiles)

    with reverts():
        bbPosts.createPost(0, postCid, {"from": bbDeployer})
        bbPosts.createPost(0, postCid, {"from": receiver})
        bbPosts.createPost(0, postCid, {"from": creator})
        bbPosts.createPost(0, postCid, {"from": unauthorized})

    bbPosts.createPost(0, postCid, {"from": owner})

def test_edit_post():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    unauthorized = accounts[4]
    profileCid = "test_profile_cid"
    postCid = "test_post_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbPosts = deploy.bbPosts(bbDeployer, bbProfiles)

    bbPosts.createPost(0, postCid, {"from": owner})

    editedPostCid = "edited_post_cid"

    with reverts():
        bbPosts.editPost(0, 0, editedPostCid, {"from": bbDeployer})
        bbPosts.editPost(0, 0, editedPostCid, {"from": receiver})
        bbPosts.editPost(0, 0, editedPostCid, {"from": creator})
        bbPosts.editPost(0, 0, editedPostCid, {"from": unauthorized})

    bbPosts.editPost(0, 0, editedPostCid, {"from": owner})

def test_get_post():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"
    postCid = "test_post_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbPosts = deploy.bbPosts(bbDeployer, bbProfiles)

    bbPosts.createPost(0, postCid, {"from": owner})

    assert bbPosts.getPost(0, 0) == postCid

def test_profiles_total_posts():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"
    postCid = "test_post_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbPosts = deploy.bbPosts(bbDeployer, bbProfiles)

    expectedTotal = random.randint(1, 10)

    for i in range(expectedTotal):
        bbPosts.createPost(0, postCid + "_" + str(i), {"from": owner})

    assert bbPosts.profilesTotalPosts(0) == expectedTotal

def test_get_edited_post():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"
    postCid = "test_post_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbPosts = deploy.bbPosts(bbDeployer, bbProfiles)

    editedPostCid = "edited_post_cid"

    postsTotal = random.randint(1, 10)

    for i in range(postsTotal):
        bbPosts.createPost(0, postCid, {"from": owner})
        bbPosts.editPost(0, i, editedPostCid + "_" + str(i), {"from": owner})
        assert bbPosts.getPost(0, i) == editedPostCid + "_" + str(i)

def test_edit_nonexistent_post():
    bbDeployer = accounts[0]    
    owner = accounts[1]
    receiver = accounts[2]
    creator = accounts[3]
    profileCid = "test_profile_cid"
    postCid = "test_post_cid"

    bbProfiles = deploy.bbProfiles(bbDeployer)

    bbProfiles.createProfile(owner, receiver, profileCid, {"from": creator})

    bbPosts = deploy.bbPosts(bbDeployer, bbProfiles)

    editedPostCid = "edited_post_cid"

    with reverts():
        bbPosts.editPost(0, 0, editedPostCid, {"from": owner})

    bbPosts.createPost(0, postCid, {"from": owner})

    with reverts():
        bbPosts.editPost(0, 1, editedPostCid, {"from": owner})

    bbPosts.editPost(0, 0, editedPostCid, {"from": owner})