// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "./BBErrorsV01.sol";
import "./interfaces/IBBProfiles.sol";
import "./interfaces/IBBTiers.sol";

contract BBTiers is IBBTiers {   
    event NewTierSet (
        uint256 profileId,
        uint256 tierSetId
    );

    event EditTierSet (
        uint256 profileId,
        uint256 tierSetId
    );

    event SupportedCurrencyChange (
        uint256 profileId,
        uint256 tierSetId,
        address currency,
        uint256 priceMultiplier
    );
    
    struct TierSet {
        uint256[] prices;
        string[] cids;
        mapping(address => uint256) supportedCurrencies;
    }

    // Profile Id -> tier set ID -> individual tier ID
    mapping(uint256 => mapping(uint256 => TierSet)) internal _tierSets; 
    // Profile Id -> total number of tier sets owned by that profile ID
    mapping(uint256 => uint256) internal _totalTierSets;

    IBBProfiles internal immutable _bbProfiles;

    constructor(address bbProfiles) {
        _bbProfiles = IBBProfiles(bbProfiles);
    }

    modifier onlyProfileOwner(uint256 profileId) {
        (address profileOwner,,) = _bbProfiles.getProfile(profileId);
        require(profileOwner == msg.sender, BBErrorCodesV01.NOT_OWNER);
        _;
    }

    modifier profileExists(uint256 profileId) {
        require(profileId < _bbProfiles.totalProfiles(), BBErrorCodesV01.PROFILE_NOT_EXIST);
        _;
    }

    modifier tierSetExists(uint256 profileId, uint256 tierSet) {
        require(profileId < _bbProfiles.totalProfiles(), BBErrorCodesV01.PROFILE_NOT_EXIST);
        require(tierSet < _totalTierSets[profileId], BBErrorCodesV01.TIER_SET_NOT_EXIST);
        _;
    }

    modifier tierExists(uint256 profileId, uint256 tierSet, uint256 tierId) {
        require(profileId < _bbProfiles.totalProfiles(), BBErrorCodesV01.PROFILE_NOT_EXIST);
        require(tierSet < _totalTierSets[profileId], BBErrorCodesV01.TIER_SET_NOT_EXIST);
        require(tierId < _tierSets[profileId][tierSet].prices.length, BBErrorCodesV01.TIER_NOT_EXIST);
        _;
    }

    function createTiers(uint256 profileId, uint256[] memory prices, string[] memory cids, address[] memory supportedCurrencies, uint256[] memory priceMultipliers) external profileExists(profileId) onlyProfileOwner(profileId) returns(uint tierSetId) {
        tierSetId = _totalTierSets[profileId];
        _totalTierSets[profileId]++;
        
        _setTiers(profileId, tierSetId, prices, cids);
        _setSupportedCurrencies(profileId, tierSetId, supportedCurrencies, priceMultipliers);
    
        emit NewTierSet(profileId, tierSetId);
    }

    function editTiers(uint256 profileId, uint256 tierSet, uint256[] memory prices, string[] memory cids) external override tierSetExists(profileId, tierSet) onlyProfileOwner(profileId) {
        _setTiers(profileId, tierSet, prices, cids);
        
        emit EditTierSet(profileId, tierSet);
    }

    function _setTiers(uint256 profileId, uint256 tierSet, uint256[] memory prices, string[] memory cids) internal {
        require(prices.length == cids.length, BBErrorCodesV01.INVALID_LENGTH);

        for(uint256 i; i < prices.length; i++) {
            require(prices[i] > 0, BBErrorCodesV01.OUT_OF_BOUNDS);
        }

        _tierSets[profileId][tierSet].prices = prices;
        _tierSets[profileId][tierSet].cids = cids;
    }

    function setSupportedCurrencies(uint256 profileId, uint256 tierSet, address[] memory supportedCurrencies, uint256[] memory priceMultipliers) external override tierSetExists(profileId, tierSet) onlyProfileOwner(profileId) {
        _setSupportedCurrencies(profileId, tierSet, supportedCurrencies, priceMultipliers);
    }

    function _setSupportedCurrencies(uint256 profileId, uint256 tierSet, address[] memory supportedCurrencies, uint256[] memory priceMultipliers) internal {
        require(supportedCurrencies.length == priceMultipliers.length, BBErrorCodesV01.INVALID_LENGTH);

        for(uint256 i; i < priceMultipliers.length; i++) {
            _tierSets[profileId][tierSet].supportedCurrencies[supportedCurrencies[i]] = priceMultipliers[i];
            emit SupportedCurrencyChange(profileId, tierSet, supportedCurrencies[i], priceMultipliers[i]);
        }
    }

    function getTierCid(uint256 profileId, uint256 tierSet, uint256 tierId) external view override tierExists(profileId, tierSet, tierId) returns (string memory) {
        return _tierSets[profileId][tierSet].cids[tierId];
    }

    function getTierPrice(uint256 profileId, uint256 tierSet, uint256 tierId, address currency) external view override tierExists(profileId, tierSet, tierId) returns (uint256) {
        require(_tierSets[profileId][tierSet].supportedCurrencies[currency] > 0, BBErrorCodesV01.UNSUPPORTED_CURRENCY);
        return _tierPrice(_tierSets[profileId][tierSet].prices[tierId], _tierSets[profileId][tierSet].supportedCurrencies[currency]);
    }

    function _tierPrice(uint256 price, uint256 multiplier) internal pure returns (uint256) {
        return price * multiplier;
    }

    function getTierSet(uint256 profileId, uint256 tierSet) external view tierSetExists(profileId, tierSet) returns (uint256[] memory, string[] memory) {
        return(_tierSets[profileId][tierSet].prices, _tierSets[profileId][tierSet].cids);
    }
    
    function totalTiers(uint256 profileId, uint256 tierSet) external view override tierSetExists(profileId, tierSet) returns (uint256) {
        return _tierSets[profileId][tierSet].prices.length;
    }

    function totalTierSets(uint256 profileId) external view override profileExists(profileId) returns (uint256) {
        return _totalTierSets[profileId];
    }
    
    function getCurrencyMultiplier(uint256 profileId, uint256 tierSet, address currency) external view override tierSetExists(profileId, tierSet) returns (uint256) {
        require(_tierSets[profileId][tierSet].supportedCurrencies[currency] > 0, BBErrorCodesV01.UNSUPPORTED_CURRENCY);
        return _tierSets[profileId][tierSet].supportedCurrencies[currency];
    }

    function isCurrencySupported(uint256 profileId, uint256 tierSet, address currency) external view override tierSetExists(profileId, tierSet) returns (bool) {
        return _tierSets[profileId][tierSet].supportedCurrencies[currency] > 0;
    }
}
