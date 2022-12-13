// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

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

    // Profile ID => Index => Post
    mapping(uint256 => mapping(uint256 => string)) internal _posts;
    // Profile ID => Total posts
    mapping(uint256 => uint256) internal _profilesTotalPosts;

    IBBProfiles internal immutable _bbProfiles;

    constructor(address bbProfiles) {
        _bbProfiles = IBBProfiles(bbProfiles);
    }

    /*
        @dev Reverts if msg.sender is not profile IDs owner

        @param Profile ID
    */
    modifier onlyProfileOwner(uint256 profileId) {
        (address profileOwner,,) = _bbProfiles.getProfile(profileId);
        require(profileOwner == msg.sender, BBErrorCodesV01.NOT_OWNER);
        _;
    }

    /*
        @dev Reverts if post ID does not exist

        @param Profile ID
        @param Post ID
    */
    modifier postExists(uint256 profileId, uint256 postId) {
        require(postId < _profilesTotalPosts[profileId], BBErrorCodesV01.POST_NOT_EXIST);
        _;
    }

    /*
        @notice Creates a new post

        @param Profile ID
        @param Post CID

        @return Instantiated posts ID
    */
    function createPost(uint256 profileId, string calldata cid) external override onlyProfileOwner(profileId) returns(uint256 postId){
        postId = _profilesTotalPosts[profileId];

        _posts[profileId][postId] = cid;

        // Increment profiles total posts
        _profilesTotalPosts[profileId]++;

        emit NewPost(profileId, postId, cid);
    }

    /*
        @notice Set an existing posts variables

        @param Profile ID
        @param Post ID
        @param Post CID
    */
    function editPost(uint256 profileId, uint postId, string calldata cid) external override onlyProfileOwner(profileId) postExists(profileId, postId) {
        _posts[profileId][postId] = cid;

        emit EditPost(profileId, postId, cid);
    }

    /*
        @notice Get a posts CID

        @param Profile ID
        @param Post ID

        @return Post CID
    */
    function getPost(uint256 profileId, uint256 postId) external view override postExists(profileId, postId) returns (string memory) {
        return (_posts[profileId][postId]);
    }

    /*
        @notice Gets the total number of posts in a profile

        @param Profile ID

        @return Total number of posts in a profile
    */
    function profilesTotalPosts(uint256 profileId) external view override returns (uint256) {
        return _profilesTotalPosts[profileId];
    }
}