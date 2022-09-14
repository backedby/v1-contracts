// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import "./DateTimeLibrary.sol";
import "./BBErrorsV01.sol";
import "./interfaces/IBBProfiles.sol";
import "./interfaces/IBBTiers.sol";
import "./interfaces/IBBSubscriptionsFactory.sol";
import "./interfaces/IBBSubscriptions.sol";

contract BBSubscriptions is IBBSubscriptions, Ownable {
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

    uint256 internal _subscriptionGasRequirement = 225000;

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

            _currency.transfer(receiver, (amount * (100 - treasuryContribution)) / 100);

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
        uint256 gasAtStart = gasleft();
        (uint256[] memory renewIndexes, address refundReceiver) = abi.decode(renewalData, (uint256[], address));

        for(uint256 i; i < renewIndexes.length; i++) {
            // Revert on bad renewal data
            require(_subscriptions[renewIndexes[i]].expiration < block.timestamp, BBErrorCodesV01.SUBSCRIPTION_NOT_EXPIRED);
            require(_subscriptions[renewIndexes[i]].cancelled == false, BBErrorCodesV01.SUBSCRIPTION_CANCELLED);

            (uint256 tierSet, uint256 contribution) = _bbSubscriptionsFactory.getSubscriptionProfile(_subscriptions[renewIndexes[i]].profileId);

            // Check the subscription tier still exists
            if(_subscriptions[renewIndexes[i]].tierId < _bbTiers.totalTiers(_subscriptions[renewIndexes[i]].profileId, tierSet)) {
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
                    continue;
                }
            }

            // Subscription payment failed, or subscription tier no longer exists, therefore cancel the subscription
            _subscriptions[renewIndexes[i]].cancelled = true;

            emit Unsubscribed(_subscriptions[renewIndexes[i]].profileId, _subscriptions[renewIndexes[i]].tierId, _subscriptions[renewIndexes[i]].subscriber);
        }

        // Calculate the gas refund, add 30327 extra gas for the rest of the function
        uint256 gasBudget = (_subscriptionGasRequirement * tx.gasprice) * renewIndexes.length;
        uint256 gasSpent = gasAtStart - gasleft() + 30327;
        uint256 refund = gasSpent * tx.gasprice;

        // Check the refund isnt greater than the gas budget
        if (refund > gasBudget) {
            refund = gasBudget;
        }

        // Transfer gas refund to refund receiver
        refundReceiver.call{value: refund}("");
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

        for(uint256 i; i < checkLength; i++) {
            uint256 subscriptionIndex = lowerBound + i;

            // If subscription has expired, increment total number of subscriptions to renew
            if(_subscriptions[subscriptionIndex].expiration < block.timestamp && _subscriptions[subscriptionIndex].cancelled == false) {               
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

        uint256[] memory renewIndexes = new uint256[](renewalCount);

        uint256 renewalIndex;

        for(uint256 i; i < checkLength; i++) {
            uint256 subscriptionIndex = lowerBound + i;

            // If subscription has expired, add the subscription ID to the array of IDs to renew
            if(_subscriptions[subscriptionIndex].expiration < block.timestamp && _subscriptions[subscriptionIndex].cancelled == false) {
                renewIndexes[renewalIndex] = subscriptionIndex;
                renewalIndex++;
            }
        }

        return (true, abi.encode(renewIndexes, refundReceiver));
    }

    /*
        @notice Subscribe to a profile

        @param Profile ID
        @param Tier ID
        
        @return Subscription ID
    */
    function subscribe(uint256 profileId, uint256 tierId) external payable override returns(uint256 subscriptionId) {
        require(msg.value >= getSubscriptionGasEstimate(tx.gasprice), BBErrorCodesV01.INSUFFICIENT_PREPAID_GAS);

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
        @notice Get subscription gas requirement

        @return Subscription gas requirement
    */
    function getSubscriptionGasRequirement() external view override returns (uint256) {
        return _subscriptionGasRequirement;
    }

    /*
        @notice Set the subscription gas requirement

        @param Subscription gas requirement
    */
    function setSubscriptionGasRequirement(uint256 requirement) external override onlyOwner {
        _subscriptionGasRequirement = requirement;
    }
    
    /*
        @notice Estimate gas required to subscribe

        @param Gas price

        @return 5 years of gas for subscription
    */   
    function getSubscriptionGasEstimate(uint256 gasprice) public view override returns(uint256) {
        return gasprice * _subscriptionGasRequirement * 60;
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