// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "./BBErrorsV01.sol";
import "./interfaces/IBBProfiles.sol";
import "./interfaces/IBBTiers.sol";
import "./interfaces/IBBSubscriptionsFactory.sol";
import "./interfaces/IBBSubscriptions.sol";
import "./interfaces/IBBPermissionsV01.sol";
import "./interfaces/IBBGasOracle.sol";
import "./BBSubscriptions.sol";

contract BBSubscriptionsFactory is IBBSubscriptionsFactory {
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
    mapping(uint256 => mapping(uint256 => mapping (address => address))) internal _subscriptionCurrencies;

    address internal _treasury;

    IBBGasOracle internal _gasOracle;

    // ERC20 token => Subscription fee
    mapping(address => uint256) internal _subscriptionFees;

    address internal _treasuryOwner;
    address internal _gasOracleOwner;
    address internal _subscriptionFeeOwner;

    IBBProfiles internal immutable _bbProfiles;
    IBBTiers internal immutable _bbTiers;

    constructor(address bbProfiles, address bbTiers, address treasury) {
        _bbProfiles = IBBProfiles(bbProfiles);
        _bbTiers = IBBTiers(bbTiers);

        _treasury = treasury;

        _treasuryOwner = msg.sender;
        _gasOracleOwner = msg.sender;
        _subscriptionFeeOwner = msg.sender;
    }

    /*
        @dev Reverts if profile ID does not exist

        @param Profile ID
    */
    modifier profileExists(uint256 profileId) {
        require(profileId < _bbProfiles.totalProfiles(), BBErrorCodesV01.PROFILE_NOT_EXIST);
        _;
    }

    /*
        @dev Reverts if tier set ID does not exist

        @param Profile ID
        @param Tier set ID
    */
    modifier tierSetExists(uint256 profileId, uint256 tierSetId) {
        require(profileId < _bbProfiles.totalProfiles(), BBErrorCodesV01.PROFILE_NOT_EXIST);
        require(tierSetId < _bbTiers.totalTierSets(profileId), BBErrorCodesV01.TIER_SET_NOT_EXIST);
        _;
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
        @dev Reverts if msg.sender is not treasury owner
    */
    modifier onlyTreasuryOwner {
        require(msg.sender == _treasuryOwner, BBErrorCodesV01.NOT_OWNER);
        _;
    }

    /*
        @dev Reverts if msg.sender is not gas oracle owner
    */
    modifier onlyGasOracleOwner {
        require(msg.sender == _gasOracleOwner, BBErrorCodesV01.NOT_OWNER);
        _;
    }

    /*
        @dev Reverts if msg.sender is not subscription fee owner
    */
    modifier onlySubscriptionFeeOwner {
        require(msg.sender == _subscriptionFeeOwner, BBErrorCodesV01.NOT_OWNER);
        _;
    }

    /*
        @notice Deploys the subscriptions contract of a ERC20 token

        @param ERC20 token

        @return The ERC20 tokens subscriptions contract
    */
    function deploySubscriptions(address currency) external override returns(address) {
        require(_deployedSubscriptions[currency] == address(0), BBErrorCodesV01.ZERO_ADDRESS);

        IBBSubscriptions subscriptions = new BBSubscriptions(address(_bbProfiles), address(_bbTiers), address(this), currency);
        
        _deployedSubscriptions[currency] = address(subscriptions);
        _subscriptionFees[currency] = 13500000;

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
        @notice Sets the treasury owner

        @param Treasury owner address
    */
    function setTreasuryOwner(address account) external override onlyTreasuryOwner {
        _treasuryOwner = account;
    }

    /*
        @notice Set the gas price owner

        @param Gas price owner address
    */
    function setGasOracleOwner(address account) external override onlyGasOracleOwner {
        _gasOracleOwner = account;
    }

    /*
        @notice Sets the subscription fee owner

        @param Subscription fee owner
    */
    function setSubscriptionFeeOwner(address account) external override onlySubscriptionFeeOwner {
        _subscriptionFeeOwner = account;
    }

    /*
        @notice Get the treasury owner

        @return Treasury address
    */
    function getTreasuryOwner() external view returns (address) {
        return _treasuryOwner;
    }

    /*
        @notice Get the gas oracle owner

        @return Gas price owner address
    */
    function getGasOracleOwner() external view returns (address) {
        return _gasOracleOwner;
    }
    
    /*
        @notice Get the subscription fee owner

        @return Subscription fee owner address
    */
    function getSubscriptionFeeOwner() external view returns (address) {
        return _subscriptionFeeOwner;
    }

    /*
        @notice Set the treasury address

        @param Treasury address
    */
    function setTreasury(address account) external override onlyTreasuryOwner {
        _treasury = account;
    }

    /*
        @notice Set the gas price oracle

        @param Gas price contract
    */
    function setGasOracle(address account) external override onlyGasOracleOwner {
        _gasOracle = IBBGasOracle(account);
    }

    /*
        @notice Set the subscription fee

        @param ERC20 token to set the subscription fee for
        @param Subscription fee
    */
    function setSubscriptionFee(address currency, uint256 amount) external override onlySubscriptionFeeOwner {
        require(_deployedSubscriptions[currency] != address(0), BBErrorCodesV01.UNSUPPORTED_CURRENCY);
        _subscriptionFees[currency] = amount;
    }

    /*
        @notice Get the treasury address

        @return Treasury address
    */
    function getTreasury() external view override returns (address treasury) {
        return _treasury;
    }

    /*
        @notice Get the gas oracles address

        @return Gas oracle
    */
    function getGasOracle() external view override returns (address oracle) {
        return address(_gasOracle);
    }

    /*
        @notice Get the subscription fee

        @param ERC20 token to set the subscription fee for

        @return Subscription fee
    */
    function getSubscriptionFee(address currency) external view returns (uint256 fee) {
        require(_deployedSubscriptions[currency] != address(0), BBErrorCodesV01.UNSUPPORTED_CURRENCY);
        return _subscriptionFees[currency] * _gasOracle.getGasPrice();
    }

    /*
        @notice Get the subscription expiration grace period

        @return Grace period in seconds
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
        _subscriptionCurrencies[profileId][tierId][account] = currency;
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
        require(_subscriptionCurrencies[profileId][tierId][account] != address(0));
        return _subscriptionCurrencies[profileId][tierId][account];
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
        @notice Check if an address has an active subscription to a profile tier

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
        if(_subscriptionCurrencies[profileId][tierId][account] == address(0)) {
            return false;
        }

        // Get subscription values from deployed subscriptions contract
        IBBSubscriptions subscriptions = IBBSubscriptions(_deployedSubscriptions[_subscriptionCurrencies[profileId][tierId][account]]);
        (,,uint256 expiration,) = subscriptions.getSubscriptionFromProfile(profileId, tierId, account);

        // If expiration plus grace period has elapsed, subscription is no longer active
        return block.timestamp < expiration + _gracePeriod;
    }
}