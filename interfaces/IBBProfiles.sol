// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

interface IBBProfiles {
    function createProfile(address owner, address receiver, string memory cid) external returns(uint256 profileId);
    function editProfile(uint256 profileId, address owner, address receiver, string memory cid) external; 

    function totalProfiles() external view returns (uint256 total);
    function getProfile(uint256 profileId) external view returns (address owner, address receiver, string memory cid);

    function getOwnersProfiles(address account) external view returns (uint256[] memory profileIds);
    function ownersTotalProfiles(address owner) external view returns (uint256);

    function isProfileOwner(uint256 profileId, address account) external view returns (bool);
}