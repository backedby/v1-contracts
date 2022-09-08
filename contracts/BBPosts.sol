// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "./BBErrorsV01.sol";
import "./interfaces/IBBProfiles.sol";
import "./interfaces/IBBPosts.sol";

contract BBPosts is IBBPosts {
    event NewPost(
        uint256 profileId,
        uint256 postId,
        string cid
    );

    event EditPost(
        uint256 profileId,
        uint256 postId,
        string cid
    );

    mapping(uint256 => mapping(uint256 => string)) internal _posts;
    mapping(uint256 => uint256) internal _profilesTotalPosts;

    IBBProfiles internal immutable _bbProfiles;

    constructor(address bbProfiles) {
        _bbProfiles = IBBProfiles(bbProfiles);
    }

    /*
        @notice Function for a profile owner to make a post

        @param Profile ID
        @param Post CID
    */
    function createPost(uint256 profileId, string calldata cid) external override returns(uint256 postId){
        (address profileOwner,,) = _bbProfiles.getProfile(profileId);
        require(profileOwner == msg.sender, BBErrorCodesV01.NOT_OWNER);

        postId = _profilesTotalPosts[profileId];

        _posts[profileId][_profilesTotalPosts[profileId]] = cid;
        _profilesTotalPosts[profileId]++;

        emit NewPost(profileId, _profilesTotalPosts[profileId] - 1, cid);
    }

    /*
        @notice Function for profile owner to edit an existing post

        @param Profile ID
        @param Post ID
        @param New post CID
    */
    function editPost(uint256 profileId, uint postId, string calldata cid) external override {
        (address profileOwner,,) = _bbProfiles.getProfile(profileId);
        require(profileOwner == msg.sender, BBErrorCodesV01.NOT_OWNER);
        require(postId < _profilesTotalPosts[profileId], BBErrorCodesV01.POST_NOT_EXIST);

        _posts[profileId][postId] = cid;

        emit EditPost(profileId, postId, cid);
    }

    /*
        @notice Returns all posts from a profile

        @param Profile ID
        @param Post ID

        @return Array of posts
    */
    function getPost(uint256 profileId, uint256 postId) external view override returns (string memory) {
        require(profileId < _bbProfiles.totalProfiles(), BBErrorCodesV01.NOT_OWNER);
        require(postId < _profilesTotalPosts[profileId], BBErrorCodesV01.POST_NOT_EXIST);

        return (_posts[profileId][postId]);
    }

    /*
        @notice Returns the total number of posts by a profile

        @param Profile ID

        @return Total number of posts made by the profile
    */
    function profilesTotalPosts(uint256 profileId) external view override returns (uint256) {
        return _profilesTotalPosts[profileId];
    }
}