// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

interface IBBTiers {
    function createTiers(uint256 profileId, uint256[] memory prices, string[] memory cids, address[] memory supportedCurrencies, uint256[] memory priceMultipliers) external returns(uint256 TierSetId);
    function editTiers(uint256 profileId, uint256 tierSet, uint256[] memory prices, string[] memory cids) external;
    function setSupportedCurrencies(uint256 profileId, uint256 tierSet, address[] memory supportedCurrencies, uint256[] memory priceMultipliers) external;

    function getTierCid(uint256 profileId, uint256 tierSet, uint256 tierId) external view returns (string memory cid);
    function getTierPrice(uint256 profileId, uint256 tierSet, uint256 tierId, address currency) external view returns (uint256 price);
    function getTierSet(uint256 profileId, uint256 tierSet) external view returns (uint256[] memory, string[] memory);

    function totalTiers(uint256 profileId, uint256 tierSet) external view returns (uint256);
    function totalTierSets(uint256 profileId) external view returns (uint256);

    function getCurrencyMultiplier(uint256 profileId, uint256 tierSet, address currency) external view returns (uint256);
    function isCurrencySupported(uint256 profileId, uint256 tierSet, address currency) external view returns (bool);
}