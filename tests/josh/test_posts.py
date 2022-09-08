from brownie import reverts
from scripts.josh.bbenv import bbenv
from scripts.josh.helpers import helpers, objdict

def test_createPost(je_org):
    profile = je_org.setup_profile()
    cid = helpers.randomCid()
    assert je_org.posts.profilesTotalPosts(profile.out_.profileId)  == 0
    createPostTx = je_org.posts.createPost(profile.out_.profileId, cid, helpers.by(profile._in.account))
    assert je_org.posts.profilesTotalPosts(profile.out_.profileId)  == 1
    return objdict({
        'profile': profile,
        'profileId': createPostTx.events['NewPost']['profileId'],
        'postId': createPostTx.events['NewPost']['postId'],
        'cid': createPostTx.events['NewPost']['cid']
    })

def test_createPost_profile_outOfRange(je_org):
    profile = je_org.setup_profile()
    cid = helpers.randomCid()
    with reverts():
        createPostTx = je_org.posts.createPost(1e9, cid, helpers.by(profile._in.account))


def test_createPost_non_owner(je_org):
    profile = je_org.setup_profile()
    cid = helpers.randomCid()
    with reverts():
        createPostTx = je_org.posts.createPost(profile.out_.profileId, cid, helpers.by(je_org.anons[1]))


def test_editPost(je_org):
    x = test_createPost(je_org)
    newCid = "different cid"
    tx = je_org.posts.editPost(x.profileId, x.postId, newCid, helpers.by(x.profile._in.account))
    assert tx.events['EditPost']['postId'] == x.postId
    assert tx.events['EditPost']['profileId'] == x.profileId
    assert tx.events['EditPost']['cid'] == newCid


def test_editPost_non_owner(je_org):
    x = test_createPost(je_org)
    with reverts():
        je_org.posts.editPost(x.profileId, x.postId, "gggg", helpers.by(je_org.anons[1]))

def test_editPost_outOfRange(je_org):
    x = test_createPost(je_org)
    newCid = "different cid"
    with reverts():
        je_org.posts.editPost(x.profileId, 1e9, newCid, helpers.by(x.profile._in.account))
        
    with reverts():
        je_org.posts.editPost(1e9, x.postId, newCid, helpers.by(x.profile._in.account))

def test_getPost(je_org):
    x = test_createPost(je_org)
    postCid = je_org.posts.getPost(x.profileId, x.postId)

    assert x.cid == postCid

def test_getPost_outOfRange(je_org):
    x = test_createPost(je_org)
    with reverts():
        je_org.posts.getPost(x.profileId, 1e9)
    
    with reverts():
        je_org.posts.getPost(1e9, 0)

def test_profilesTotalPosts(je_org):
    x = test_createPost(je_org)
    for i in range(1, 20):
        je_org.posts.createPost(x.profileId, helpers.randomCid(), helpers.by(x.profile._in.account))

    assert je_org.posts.profilesTotalPosts(x.profileId) == 20