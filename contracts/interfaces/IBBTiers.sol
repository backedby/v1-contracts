// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IBBTiers {
    function createTiers(uint256 profileId, uint256[] calldata prices, string[] calldata cids, bool[] memory deprecated, address[] calldata supportedCurrencies, uint256[] calldata priceMultipliers) external returns(uint256 tierSetId);
    function editTiers(uint256 profileId, uint256 tierSetId, uint256[] calldata prices, string[] calldata cids, bool[] memory deprecated) external;
    function setSupportedCurrencies(uint256 profileId, uint256 tierSetId, address[] calldata supportedCurrencies, uint256[] calldata priceMultipliers) external;

    function getTier(uint256 profileId, uint256 tierSetId, uint256 tierId, address currency) external view returns (string memory, uint256, bool);
    function getTierSet(uint256 profileId, uint256 tierSetId) external view returns (uint256[] memory prices, string[] memory cids, bool[] memory deprecated);

    function totalTiers(uint256 profileId, uint256 tierSetId) external view returns (uint256 total);
    function totalTierSets(uint256 profileId) external view returns (uint256 total);

    function getCurrencyMultiplier(uint256 profileId, uint256 tierSetId, address currency) external view returns (uint256 multiplier);
    function isCurrencySupported(uint256 profileId, uint256 tierSetId, address currency) external view returns (bool supported);
}