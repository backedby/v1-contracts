// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

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
        uint256 tierSetId,
        uint256 contribution
    );

    event EditContribution(
        uint256 profileId,
        uint256 contribution
    );

    struct SubscriptionProfile {
        uint256 tierSetId;
        uint256 contribution;
    }

    uint256 internal constant _contributionLower = 1;
    uint256 internal constant _contributionUpper = 100;

    uint256 internal constant _gracePeriod = 2 days;

    // Subscription profile ID => Subscription profile
    mapping(uint256 => SubscriptionProfile) internal _subscriptionProfiles;
    
    // ERC20 token => Deployed subscriptions contract
    mapping(address => address) internal _deployedSubscriptions;

    // Profile ID => Tier ID => Subscriber => ERC20 token
    mapping(uint256 => mapping(uint256 => mapping (address => address))) internal _subscriptionCurrency;

    address internal _treasury;

    IBBProfiles internal immutable _bbProfiles;
    IBBTiers internal immutable _bbTiers;

    constructor(address bbProfiles, address bbTiers, address treasury) {
        _bbProfiles = IBBProfiles(bbProfiles);
        _bbTiers = IBBTiers(bbTiers);

        _treasury = treasury;
    }

    /*
        @dev Reverts if msg.sender is not profile IDs owner
    */
    modifier onlyProfileOwner(uint256 profileId) {
        (address profileOwner,,) = _bbProfiles.getProfile(profileId);
        require(profileOwner == msg.sender, BBErrorCodesV01.NOT_OWNER);
        _;
    }

    /*
        @dev Reverts if profile ID does not exist
    */
    modifier profileExists(uint256 profileId) {
        require(profileId < _bbProfiles.totalProfiles(), BBErrorCodesV01.PROFILE_NOT_EXIST);
        _;
    }

    /*
        @dev Reverts if tier set ID does not exist
    */
    modifier tierSetExists(uint256 profileId, uint256 tierSetId) {
        require(profileId < _bbProfiles.totalProfiles(), BBErrorCodesV01.PROFILE_NOT_EXIST);
        require(tierSetId < _bbTiers.totalTierSets(profileId), BBErrorCodesV01.TIER_SET_NOT_EXIST);
        _;
    }

    /*
        @notice Gets the subscriptions contract of a ERC20 token

        @param ERC20 token

        @return The ERC20 token subscriptions contract
    */
    function deploySubscriptions(address currency) external override returns(address) {
        require(_deployedSubscriptions[currency] == address(0), BBErrorCodesV01.ZERO_ADDRESS);

        IBBSubscriptions subscriptions = new BBSubscriptions(address(_bbProfiles), address(_bbTiers), address(this), currency);
        
        _deployedSubscriptions[currency] = address(subscriptions);

        emit DeployedSubscription(currency, address(subscriptions));
        return address(subscriptions);
    }

    /*
        @notice Check if a ERC20 token has a deployed subscriptions contract

        @param ERC20 token

        @return True if ERC20 token has a deployed subscriptions contract, otherwise false
    */
    function isSubscriptionsDeployed(address currency) external view override returns (bool) {
        return _deployedSubscriptions[currency] != address(0);
    }

    /*
        @notice Get the address of a ERC20 tokens subscriptions contract

        @param ERC20 token

        @return ERC20 tokens subscriptions contract address
    */
    function getDeployedSubscriptions(address currency) external view override returns (address) {
        // Reverts if the ERC20 tokens subscriptions contract is not deployed
        require(_deployedSubscriptions[currency] != address(0));
        return _deployedSubscriptions[currency];
    }

    /*
        @notice Set the treasury address

        @param Treasury address
    */
    function setTreasury(address account) external override onlyOwner {
        _treasury = account;
    }

    /*
        @notice Get the treasury address

        @return Treasury address
    */
    function getTreasury() external view override returns (address) {
        return _treasury;
    }

    /*
        @notice Get the treasury address

        @return Treasury address
    */
    function getGracePeriod() external pure override returns (uint256) {
        return _gracePeriod;
    }
    
    /*
        @notice Get the treasury contribution bounds

        @return Lower bound
        @return Upper bound
    */
    function getContributionBounds() external pure override returns (uint256, uint256) {
        return (_contributionLower, _contributionUpper);
    }

    /*
        @dev Set a subscriptions ERC20 token

        @param Profile ID
        @param Tier ID
        @param Subscriber
        @param ERC20 token
    */
    function setSubscriptionCurrency(uint256 profileId, uint256 tierId, address account, address currency) profileExists(profileId) external override {
        // Msg.sender must be the ERC20 tokens subscriptions contract
        require(msg.sender == _deployedSubscriptions[currency], BBErrorCodesV01.NOT_OWNER);
        _subscriptionCurrency[profileId][tierId][account] = currency;
    }

    /*
        @notice Get a subscriptions ERC20 token

        @param Profile ID
        @param Tier ID
        @param Subscriber

        @return ERC20 token
    */
    function getSubscriptionCurrency(uint256 profileId, uint256 tierId, address account) external view override profileExists(profileId) returns (address) {
        // Subscription isn't active if subscriptions ERC20 token is the zero address, so revert
        require(_subscriptionCurrency[profileId][tierId][account] != address(0));
        return _subscriptionCurrency[profileId][tierId][account];
    }

    /*
        @notice Set the subscription gas requirement

        @param Currency to set the gas requirement for
        @param Subscription gas requirement
    */
    function setSubscriptionGasRequirement(address currency, uint256 requirement) external override onlyOwner {
        // Limit gas requirement to avoid exploit
        require(requirement <= block.gaslimit / 15, BBErrorCodesV01.OUT_OF_BOUNDS);
        require(_deployedSubscriptions[currency] != address(0), BBErrorCodesV01.UNSUPPORTED_CURRENCY);
        IBBSubscriptions(_deployedSubscriptions[currency]).setSubscriptionGasRequirement(requirement);
    }

    /*
        @notice Create a new subscription profile

        @param Profile ID
        @param Tier set ID
        @param Contribution
    */
    function createSubscriptionProfile(uint256 profileId, uint256 tierSetId, uint256 contribution) external override tierSetExists(profileId, tierSetId) onlyProfileOwner(profileId) {
        // Subscription profile already initialized
        require(_subscriptionProfiles[profileId].tierSetId == 0, BBErrorCodesV01.SUBSCRIPTION_PROFILE_ALREADY_EXISTS);

        _setContribution(profileId, contribution);
        // Add one to tier set ID so can also be used like a bool, zero means the value is uninitialized, greater than zero is the tier set ID minus one
        _subscriptionProfiles[profileId].tierSetId = tierSetId + 1;

        emit NewSubscriptionProfile(profileId, tierSetId, contribution);
    }

    /*
        @notice Get a subscription profile

        @param Profile ID

        @return Tier set ID
        @return Treasury contribution
    */
    function getSubscriptionProfile(uint256 profileId) external view override profileExists(profileId) returns (uint256, uint256) {
        // If subscription profile isnt initialized, tier set ID is zero, and so this reverts
        return (_subscriptionProfiles[profileId].tierSetId - 1, _subscriptionProfiles[profileId].contribution);
    }

    /*
        @notice Check a subscription profile is created

        @param Profile ID

        @return True if subscription profile is created, otherwise false
    */
    function isSubscriptionProfileCreated(uint256 profileId) external view override profileExists(profileId) returns (bool) {
        return _subscriptionProfiles[profileId].tierSetId > 0;
    }

    /*
        @notice Set a subscription profiles treasury contribution

        @param Profile ID
        @param Treasury contribution
    */
    function setContribution(uint256 profileId, uint256 contribution) external override profileExists(profileId) onlyProfileOwner(profileId){
        _setContribution(profileId, contribution);
        emit EditContribution(profileId, contribution);
    }

    /*
        @dev Set a subscription profiles treasury contribution

        @param Profile ID
        @param Treasury contribution
    */
    function _setContribution(uint256 profileId, uint256 contribution) internal {
        require(contribution >= _contributionLower, BBErrorCodesV01.OUT_OF_BOUNDS);
        require(contribution <= _contributionUpper, BBErrorCodesV01.OUT_OF_BOUNDS);

        _subscriptionProfiles[profileId].contribution = contribution;
    }

    /*
        @notice Check if an address has an active subscription at a specific tier

        @param Profile ID
        @param Tier ID
        @param Subscriber

        @return True if the subscription is active, otherwise false
    */
    function isSubscriptionActive(uint256 profileId, uint256 tierId, address account) external view override profileExists(profileId) returns (bool) {
        (address profileOwner,,) = _bbProfiles.getProfile(profileId);

        // Profile owner is always subscribed
        if(profileOwner == account) {
            return true;
        }

        // If profile owner is a contract, try checking for BackedBy permissions
        if(profileOwner.code.length > 0) {
            try IBBPermissionsV01(profileOwner).canViewSubscription(account) returns (bool success) {
                if(success)
                    return success;
            } catch { }
        }

        // If the subscription has no ERC20 token set, its not active
        if(_subscriptionCurrency[profileId][tierId][account] == address(0)) {
            return false;
        }

        // Get subscription values from deployed subscriptions contract
        IBBSubscriptions subscriptions = IBBSubscriptions(_deployedSubscriptions[_subscriptionCurrency[profileId][tierId][account]]);
        (,uint256 expiration,) = subscriptions.getSubscription(profileId, tierId, account);

        // If expiration plus grace period has elapsed, subscription is no longer active
        return block.timestamp < expiration + _gracePeriod;
    }
}