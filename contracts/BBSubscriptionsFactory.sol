// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/access/Ownable.sol";

import "./BBErrorsV01.sol";
import "./interfaces/IBBProfiles.sol";
import "./interfaces/IBBTiers.sol";
import "./interfaces/IBBSubscriptionsFactory.sol";
import "./interfaces/IBBSubscriptions.sol";
import "./interfaces/IBBPermissionsV01.sol";
import "./BBSubscriptions.sol";

contract BBSubscriptionsFactory is Ownable, IBBSubscriptionsFactory {
    event DeployedSubscription(
        address currency,
        address deployedAddress
    );

    event NewSubscriptionProfile(
        uint256 profileId,
        uint256 tierSet,
        uint256 contribution
    );

    event EditContribution(
        uint256 profileId,
        uint256 contribution
    );

    struct SubscriptionProfile {
        uint256 tierSet;
        uint256 contribution;
    }

    uint256 internal constant _contributionLower = 1;
    uint256 internal constant _contributionUpper = 100;

    uint256 internal constant _gracePeriod = 2 days;

    uint256 internal _subscriptionGasRequirement = 100000000;

    mapping(uint256 => SubscriptionProfile) internal _subscriptionProfiles;
    
    mapping(address => address) internal _deployedSubscriptions;

    mapping(uint256 => mapping(uint256 => mapping (address => address))) internal _subscriptionCurrency;

    address internal _treasury;

    IBBProfiles internal immutable _bbProfiles;
    IBBTiers internal immutable _bbTiers;

    constructor(address bbProfiles, address bbTiers, address treasury) {
        _bbProfiles = IBBProfiles(bbProfiles);
        _bbTiers = IBBTiers(bbTiers);

        _treasury = treasury;
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
        require(tierSet < _bbTiers.totalTierSets(profileId), BBErrorCodesV01.TIER_SET_NOT_EXIST);
        _;
    }

    function deploySubscriptions(address currency) external override returns(address) {
        require(_deployedSubscriptions[currency] == address(0), BBErrorCodesV01.ZERO_ADDRESS);

        IBBSubscriptions subscriptions = new BBSubscriptions(address(_bbProfiles), address(_bbTiers), address(this), currency);

        _deployedSubscriptions[currency] = address(subscriptions);

        emit DeployedSubscription(currency, address(subscriptions));
        return address(subscriptions);
    }

    function isSubscriptionsDeployed(address currency) external view override returns (bool) {
        return _deployedSubscriptions[currency] != address(0);
    }

    function getDeployedSubscriptions(address currency) external view override returns (address) {
        require(_deployedSubscriptions[currency] != address(0));
        return _deployedSubscriptions[currency];
    }

    function setTreasury(address account) external override onlyOwner {
        require(account != owner(), BBErrorCodesV01.NOT_OWNER);
        _treasury = account;
    }

    function setSubscriptionGasRequirement(uint256 requirement) external override onlyOwner {
        // Limit gas requirement to avoid exploit : 0.001 MATIC
        require(requirement <= 10 ** 15, BBErrorCodesV01.OUT_OF_BOUNDS);
        _subscriptionGasRequirement = requirement;
    }

    function getTreasury() external view override returns (address) {
        return _treasury;
    }

    function getGracePeriod() external pure override returns (uint256) {
        return _gracePeriod;
    }
    
    function getContributionBounds() external pure override returns (uint256, uint256) {
        return (_contributionLower, _contributionUpper);
    }

    function getSubscriptionGasRequirement() external view override returns (uint256) {
        return _subscriptionGasRequirement;
    }

    function setSubscriptionCurrency(uint256 profileId, uint256 tierId, address account, address currency) profileExists(profileId) external override {
        require(msg.sender == _deployedSubscriptions[currency], BBErrorCodesV01.NOT_OWNER);
        _subscriptionCurrency[profileId][tierId][account] = currency;
    }

    function getSubscriptionCurrency(uint256 profileId, uint256 tierId, address account) external view override profileExists(profileId) returns (address) {
        require(_subscriptionCurrency[profileId][tierId][account] != address(0));
        return _subscriptionCurrency[profileId][tierId][account];
    }

    function createSubscriptionProfile(uint256 profileId, uint256 tierSet, uint256 contribution) external override tierSetExists(profileId, tierSet) onlyProfileOwner(profileId) {
        require(_subscriptionProfiles[profileId].tierSet == 0, BBErrorCodesV01.SUBSCRIPTION_PROFILE_ALREADY_EXISTS);

        _setContribution(profileId, contribution);
        _subscriptionProfiles[profileId].tierSet = tierSet + 1;

        emit NewSubscriptionProfile(profileId, tierSet, contribution);
    }

    function getSubscriptionProfile(uint256 profileId) external view override profileExists(profileId) returns (uint256, uint256) {
        return (_subscriptionProfiles[profileId].tierSet - 1, _subscriptionProfiles[profileId].contribution);
    }

    function isSubscriptionProfileCreated(uint256 profileId) external view override profileExists(profileId) returns (bool) {
        return _subscriptionProfiles[profileId].tierSet > 0;
    }

    function setContribution(uint256 profileId, uint256 contribution) external override profileExists(profileId) onlyProfileOwner(profileId){
        _setContribution(profileId, contribution);
        emit EditContribution(profileId, contribution);
    }
    
    function _setContribution(uint256 profileId, uint256 contribution) internal {
        require(contribution >= _contributionLower, BBErrorCodesV01.OUT_OF_BOUNDS);
        require(contribution <= _contributionUpper, BBErrorCodesV01.OUT_OF_BOUNDS);

        _subscriptionProfiles[profileId].contribution = contribution;
    }

    function isSubscriptionActive(uint256 profileId, uint256 tierId, address account) external view override profileExists(profileId) returns (bool) {
        (address profileOwner,,) = _bbProfiles.getProfile(profileId);

        if(profileOwner == account) {
            return true;
        }

        if(profileOwner.code.length > 0) {
            try IBBPermissionsV01(profileOwner).canViewSubscription(account) returns (bool success) {
                if(success)
                    return success;
            } catch { }
        }

        if(_subscriptionCurrency[profileId][tierId][account] == address(0)) {
            return false;
        }

        IBBSubscriptions subscriptions = IBBSubscriptions(_deployedSubscriptions[_subscriptionCurrency[profileId][tierId][account]]);
        (,uint256 expiration,) = subscriptions.getSubscription(profileId, tierId, account);

        return block.timestamp < expiration + _gracePeriod;
    }
}