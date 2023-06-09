// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IBBStoreRouter {
    function totalStores() external view returns (uint256 total);
    function getStore(uint256 storeId) external view returns (uint256 profileId, uint256 contribution, address nft, address cashier, string memory cid);
    
    function createStore(uint256 profileId, uint256 contribution, address nft, address cashier, string memory cid) external returns (uint256 storeId);
    function editStore(uint256 storeId, uint256 profileId, uint256 contribution, address nft, address cashier, string memory cid) external;
    function setProfileId(uint256 storeId, uint256 profileId) external;

    function buy(uint256 storeId, uint256 expectedPrice, address currency, bytes memory buyData) external returns (bytes memory);
}