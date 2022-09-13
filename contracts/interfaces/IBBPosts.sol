// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IBBPosts {
    function createPost(uint256 profileId, string calldata cid) external returns(uint256 postId);
    function editPost(uint256 profileId, uint256 postId, string calldata cid) external;
    
    function getPost(uint256 profileId, uint256 postId) external view returns (string memory cid);
    function profilesTotalPosts(uint256 profileId) external view returns (uint256 total);
}