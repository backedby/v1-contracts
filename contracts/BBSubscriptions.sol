// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "./utils/DateTimeLibrary.sol";
import "./BBErrorsV01.sol";
import "./interfaces/IBBProfiles.sol";
import "./interfaces/IBBTiers.sol";
import "./interfaces/IBBSubscriptionsFactory.sol";
import "./interfaces/IBBSubscriptions.sol";

contract BBSubscriptions is IBBSubscriptions {
    event Subscribed(
        uint256 profileId,
        uint256 tierId,
        address subscriber
    );

    event Unsubscribed (
        uint256 profileId,
        uint256 tierId,
        address subscriber
    );

    struct Subscription {
        uint256 profileId;
        uint256 tierId;
        address subscriber;
        uint256 price;
        uint256 expiration;
        bool cancelled;
    }

    // Subscription ID => Subscription
    mapping (uint256 => Subscription) internal _subscriptions;
    uint256 internal _totalSubscriptions;

    // Profile ID => Tier ID => Subscriber => Subscription ID + 1
    mapping(uint256 => mapping(uint256 => mapping(address => uint256))) internal _subscriptionIndexes;

    uint256 internal _upkeepGasRequirement = 225000;

    IBBProfiles internal immutable _bbProfiles;
    IBBTiers internal immutable _bbTiers;
    IBBSubscriptionsFactory internal immutable _bbSubscriptionsFactory;

    IERC20 internal immutable _currency;

    constructor(address bbProfiles, address bbTiers, address bbSubscriptionsFactory, address currency) {
        _bbProfiles = IBBProfiles(bbProfiles);
        _bbTiers = IBBTiers(bbTiers);
        _bbSubscriptionsFactory = IBBSubscriptionsFactory(bbSubscriptionsFactory);

        _currency = IERC20(currency);
    }

    /*
        @dev Reverts if msg.sender is not upkeepGasRequirementOwner
    */
    modifier onlySubscriptionsFactory {
        require(msg.sender == address(_bbSubscriptionsFactory), BBErrorCodesV01.NOT_OWNER);
        _;
    }

    /*
        @dev Transfer ERC20 tokens from address to receiver and treasury

        @param ERC20 token owner
        @param ERC20 token receiver
        @param ERC20 token amount
        @param Treasury contribution percentage

        @return True if transfer succeeded, otherwise false
    */
    function _pay(address owner, address receiver, uint256 amount, uint256 treasuryContribution) internal returns (bool) {
        // Check that the contract has enough allowance to process this transfer
        if ((_currency.allowance(owner, address(this)) >= amount) && _currency.balanceOf(owner) >= amount) { 
            _currency.transferFrom(owner, address(this), amount);

            uint256 receiverAmount = (amount * (100 - treasuryContribution)) / 100;

            if(receiverAmount > 0) {
                _currency.transfer(receiver, receiverAmount);
            }

            // Payment processed
            return true;
        } 

        // Insufficient funds
        return false;
    }

    /*
        @notice Renew subscriptions within a range

        @param Array of subscription IDs to renew and refund receiver packed into bytes array
    */
    function performUpkeep(bytes calldata renewalData) external override {
        (uint256[] memory renewIndexes, address refundReceiver) = abi.decode(renewalData, (uint256[], address));
        
        uint256 gasAtStart = gasleft();
        uint256 renewCount;

        for(uint256 i; i < renewIndexes.length; i++) {
            require(renewIndexes[i] < _totalSubscriptions, BBErrorCodesV01.SUBSCRIPTION_NOT_EXIST);

            if(_subscriptions[renewIndexes[i]].expiration < block.timestamp && _subscriptions[renewIndexes[i]].cancelled == false) {
                (uint256 tierSetId, uint256 contribution) = _bbSubscriptionsFactory.getSubscriptionProfile(_subscriptions[renewIndexes[i]].profileId);

                // Check the subscription tier still exists, and the token is still accepted by the creator
                if(_subscriptions[renewIndexes[i]].tierId < _bbTiers.totalTiers(_subscriptions[renewIndexes[i]].profileId, tierSetId) && _bbTiers.isCurrencySupported(_subscriptions[renewIndexes[i]].profileId, tierSetId, address(_currency))) {
                    (,address profileReceiver,) = _bbProfiles.getProfile(_subscriptions[renewIndexes[i]].profileId);

                    bool paid = _pay(
                        _subscriptions[renewIndexes[i]].subscriber,
                        profileReceiver,
                        _subscriptions[renewIndexes[i]].price,
                        contribution
                    );

                    if(paid) {
                        // Subscription payment succeeded, so extended expiration timestamp
                        _subscriptions[renewIndexes[i]].expiration = block.timestamp + (DateTimeLibrary.getDaysInMonth(block.timestamp) * 1 days);    

                        renewCount++;
                        continue;
                    }
                }

                // Subscription payment failed, or subscription tier no longer exists, therefore cancel the subscription
                _subscriptions[renewIndexes[i]].cancelled = true;

                emit Unsubscribed(_subscriptions[renewIndexes[i]].profileId, _subscriptions[renewIndexes[i]].tierId, _subscriptions[renewIndexes[i]].subscriber);

                renewCount++;
            }
        }

        require(renewCount > 0, BBErrorCodesV01.UPKEEP_FAIL);

        // Calculate the gas refund, add 30327 gas for the rest of the function, 26215 for decoding the renewal data, and 423 multiplied by the number of indexes renewed
        uint256 gasBudget = (_upkeepGasRequirement * _bbSubscriptionsFactory.getGasPrice()) * renewCount;
        uint256 refund = (gasAtStart - gasleft() + (56542 + (423 * renewCount))) * _bbSubscriptionsFactory.getGasPrice();
        // Invalid ID refund penalty
        refund = refund - ((refund / renewIndexes.length) * (renewIndexes.length - renewCount));

        // Check the refund isnt greater than the gas budget
        if (refund > gasBudget) {
            refund = gasBudget;
        }

        // Transfer gas refund to refund receiver
        refundReceiver.call{value: refund}("");
    }

    /*
        @notice Subscribe to a profile

        @param Profile ID
        @param Tier ID
        
        @return Subscription ID
    */
    function subscribe(uint256 profileId, uint256 tierId) external payable override returns(uint256 subscriptionId) {
        require(msg.value >= getSubscriptionGasRequirement(), BBErrorCodesV01.INSUFFICIENT_PREPAID_GAS);

        if(_bbSubscriptionsFactory.isSubscriptionActive(profileId, tierId, msg.sender) == true) {
            (,,bool cancelled) = IBBSubscriptions(_bbSubscriptionsFactory.getDeployedSubscriptions(_bbSubscriptionsFactory.getSubscriptionCurrency(profileId, tierId, msg.sender))).getSubscription(profileId, tierId, msg.sender);
            require(cancelled == true, BBErrorCodesV01.SUBSCRIPTION_ACTIVE);
        }

        (uint256 tierSet,) = _bbSubscriptionsFactory.getSubscriptionProfile(profileId);

        uint256 price = _bbTiers.getTierPrice(profileId, tierSet, tierId, address(_currency));

        require(_currency.allowance(msg.sender, address(this)) >= price * 60, BBErrorCodesV01.INSUFFICIENT_ALLOWANCE);

        subscriptionId = _totalSubscriptions;

        if(_subscriptionIndexes[profileId][tierId][msg.sender] == 0) {
            _subscriptionIndexes[profileId][tierId][msg.sender] = _totalSubscriptions + 1;
            _totalSubscriptions++;
        }
        else {
            subscriptionId = _subscriptionIndexes[profileId][tierId][msg.sender] - 1;
        }

        _subscriptions[subscriptionId] = Subscription(
            profileId, 
            tierId, 
            msg.sender, 
            price,
            block.timestamp + 30 days, 
            false
        ); 

        (,address profileReceiver,) = _bbProfiles.getProfile(profileId);
        (,uint256 contribution) = _bbSubscriptionsFactory.getSubscriptionProfile(profileId);

        require(_pay(msg.sender, profileReceiver, price, contribution ), BBErrorCodesV01.INSUFFICIENT_BALANCE);

        _bbSubscriptionsFactory.setSubscriptionCurrency(profileId, tierId, msg.sender, address(_currency));

        withdrawToTreasury();

        emit Subscribed(profileId, tierId, msg.sender);
    }

    /*
        @notice Unsubscribe from a profile

        @param Profile ID
        @param Tier ID        
    */
    function unsubscribe(uint256 profileId, uint256 tierId) external override {
        uint256 id = _getSubscriptionId(profileId, tierId, msg.sender);
        require(_subscriptions[id].subscriber == msg.sender, BBErrorCodesV01.NOT_SUBSCRIPTION_OWNER);
        require(_subscriptions[id].cancelled == false, BBErrorCodesV01.SUBSCRIPTION_CANCELLED);

        _subscriptions[id].cancelled = true;

        emit Unsubscribed(profileId, tierId, msg.sender);
    }

    /*
        @notice Check if there are subscriptions to renew within a range

        @param Lower bound, upper bound, minimum number of IDs to renew, maximum number of IDs to renew, and refund receiver packed into bytes array

        @return True if there are subscriptions to renew within the lower and upper bound, otherwise false
        @return Array of subscription IDs to renew and refund receiver packed into bytes array
    */
    function checkUpkeep(bytes calldata checkData) external view override returns (bool, bytes memory) {
        (uint256 lowerBound, uint256 upperBound, uint256 minRenews, uint256 maxRenews, address refundReceiver) = abi.decode(checkData, (uint256, uint256, uint256, uint256, address));

        // Limit upper bound within total subscriptions
        if(upperBound >= _totalSubscriptions) {
            upperBound = _totalSubscriptions - 1;
        }

        // Lower bound must be less than upper bound
        require(lowerBound <= upperBound, BBErrorCodesV01.OUT_OF_BOUNDS);

        uint256 renewalCount;
        uint256 checkLength = (upperBound - lowerBound) + 1;

        uint256[] memory maxRenewIndexes = new uint256[](maxRenews);

        for(uint256 i; i < checkLength; i++) {
            uint256 subscriptionIndex = lowerBound + i;

            // If subscription has expired, increment total number of subscriptions to renew
            if(_subscriptions[subscriptionIndex].expiration < block.timestamp && _subscriptions[subscriptionIndex].cancelled == false) {               
                maxRenewIndexes[renewalCount] = subscriptionIndex;
                renewalCount++;

                if(renewalCount >= maxRenews) {
                    break;
                }
            }
        }

        // If subscriptions to renew is zero or less than minimum required renewals, return false
        if(renewalCount == 0 || renewalCount < minRenews) {
            return (false, "");
        }

        // Return the maximum number of indexes that can be renewed
        if(renewalCount == maxRenews) {
            return (true, abi.encode(maxRenewIndexes, refundReceiver));
        }

        // Resize renewal indexes array
        uint256[] memory renewIndexes = new uint256[](renewalCount);

        for(uint256 i; i < renewalCount; i++) {
            renewIndexes[i] = maxRenewIndexes[i];
        }

        return (true, abi.encode(renewIndexes, refundReceiver));
    }

    /*
        @notice Get subscription gas requirement

        @return Subscription gas requirement
    */
    function getUpkeepGasRequirement() external view override returns (uint256) {
        return _upkeepGasRequirement;
    }

    /*
        @notice Set the subscription gas requirement

        @param Subscription gas requirement
    */
    function setUpkeepGasRequirement(uint256 requirement) external override onlySubscriptionsFactory {
        _upkeepGasRequirement = requirement;
    }
    
    /*
        @notice Gas required to subscribe

        @return 5 years of gas for subscription
    */   
    function getSubscriptionGasRequirement() public view override returns(uint256) {
        return _upkeepGasRequirement * _bbSubscriptionsFactory.getGasPrice() * 60;
    }

    /*
        @notice Transfers this contracts tokens to the subscription factory treasury
    */
    function withdrawToTreasury() public {
        _currency.transfer(_bbSubscriptionsFactory.getTreasury(), _currency.balanceOf(address(this)));
    }

    /*
        @notice Get a subscriptions values

        @param Profile ID
        @param Tier ID
        @param Subscriber

        @return Price (monthly)
        @return Expiration
        @return Subscription cancelled
    */
    function getSubscription(uint256 profileId, uint256 tierId, address subscriber) external view returns (uint256, uint256, bool) {
        uint256 id = _getSubscriptionId(profileId, tierId, subscriber);

        return (
            _subscriptions[id].price,
            _subscriptions[id].expiration,
            _subscriptions[id].cancelled
        );
    }

    /*
        @dev Get a subscription ID

        @param Profile ID
        @param Tier ID
        @param Subscriber

        @return Subscription ID
    */
    function _getSubscriptionId(uint256 profileId, uint256 tierId, address subscriber) internal view returns (uint256) {
        require(_subscriptionIndexes[profileId][tierId][subscriber] > 0, BBErrorCodesV01.SUBSCRIPTION_NOT_EXIST);
        return _subscriptionIndexes[profileId][tierId][subscriber] - 1;
    }
}