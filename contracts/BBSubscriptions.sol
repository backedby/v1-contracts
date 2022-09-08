// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

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

    mapping (uint256 => Subscription) internal _subscriptions;
    uint256 internal _totalSubscriptions;
    // Profile ID => Tier ID => Subscriber => Subscription ID + 1
    mapping(uint256 => mapping(uint256 => mapping(address => uint256))) internal _subscriptionIndexes;

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

    function checkUpkeep(bytes calldata checkData) external view override returns (bool, bytes memory) {
        (uint256 lowerBound, uint256 upperBound, address refundReceiver) = abi.decode(checkData, (uint256, uint256, address));

        require(lowerBound <= upperBound, BBErrorCodesV01.OUT_OF_BOUNDS);

        if(upperBound >= _totalSubscriptions) {
            upperBound = _totalSubscriptions - 1;
        }

        uint256 renewalCount;
        uint256 checkLength = (upperBound - lowerBound) + 1;

        for(uint256 i; i < checkLength; i++) {
            uint256 subscriptionIndex = lowerBound + i;

            if(_subscriptions[subscriptionIndex].expiration < block.timestamp && _subscriptions[subscriptionIndex].cancelled == false) {               
                renewalCount++;
            }
        }

        if(renewalCount == 0) {
            return (false, "");
        }

        uint256[] memory renewIndexes = new uint256[](renewalCount);

        uint256 renewalIndex;

        for(uint256 i; i < checkLength; i++) {
            uint256 subscriptionIndex = lowerBound + i;

            if(_subscriptions[subscriptionIndex].expiration < block.timestamp && _subscriptions[subscriptionIndex].cancelled == false) {
                renewIndexes[renewalIndex] = subscriptionIndex;
                renewalIndex++;
            }
        }

        return (true, abi.encode(renewIndexes, refundReceiver));
    }

    function performUpkeep(bytes calldata renewalData) external override {
        uint256 gasAtStart = gasleft();
        (uint256[] memory renewIndexes, address refundReceiver) = abi.decode(renewalData, (uint256[], address));

        for(uint256 i; i < renewIndexes.length; i++) {
            require(_subscriptions[renewIndexes[i]].expiration < block.timestamp, BBErrorCodesV01.SUBSCRIPTION_NOT_EXPIRED);
            require(_subscriptions[renewIndexes[i]].cancelled == false, BBErrorCodesV01.SUBSCRIPTION_CANCELLED);

            (uint256 tierSet, uint256 contribution) = _bbSubscriptionsFactory.getSubscriptionProfile(_subscriptions[renewIndexes[i]].profileId);

            if(_subscriptions[renewIndexes[i]].tierId < _bbTiers.totalTiers(_subscriptions[renewIndexes[i]].profileId, tierSet)) {
                (,address profileReceiver,) = _bbProfiles.getProfile(_subscriptions[renewIndexes[i]].profileId);

                bool paid = _pay(
                    _subscriptions[renewIndexes[i]].subscriber,
                    profileReceiver,
                    _subscriptions[renewIndexes[i]].price,
                    contribution
                );

                if(paid) {
                    _subscriptions[renewIndexes[i]].expiration = block.timestamp + 30 days;      
                    continue;
                }
            }

            _subscriptions[renewIndexes[i]].cancelled = true;

            emit Unsubscribed(_subscriptions[renewIndexes[i]].profileId, _subscriptions[renewIndexes[i]].tierId, _subscriptions[renewIndexes[i]].subscriber);
        }

        // Calculate the gas refund, add 29143 extra wei for the rest of the function
        uint256 gasBudget = (_bbSubscriptionsFactory.getSubscriptionGasRequirement() / 60) * renewIndexes.length;
        uint256 gasSpent = gasAtStart - gasleft() + 29143;
        uint256 refund = gasSpent * tx.gasprice;

        // Check the refund isnt greater than the gas budget
        if (refund > gasBudget) {
            refund = gasBudget;
        }

        refundReceiver.call{value: refund};
    }

    function _pay(address owner, address receiver, uint256 amount, uint256 daoContribution) internal returns (bool) {
        // Check that the contract has enough allowance to process this transfer
        if ((_currency.allowance(owner, address(this)) >= amount) && _currency.balanceOf(owner) >= amount) { 
            _currency.transferFrom(owner, address(this), amount);

            _currency.transfer(receiver, (amount * (100 - daoContribution)) / 100);

            // Payment processed
            return true;
        } 

        // Insufficient funds
        return false;
    }

    function subscribe(uint256 profileId, uint256 tierId) external payable override returns(uint256 subscriptionId) {
        require(msg.value >= _bbSubscriptionsFactory.getSubscriptionGasRequirement(), BBErrorCodesV01.INSUFFICIENT_PREPAID_GAS);

        if(_bbSubscriptionsFactory.isSubscriptionActive(profileId, tierId, msg.sender) == true) {
            (,,bool cancelled) = IBBSubscriptions(_bbSubscriptionsFactory.getDeployedSubscriptions(_bbSubscriptionsFactory.getSubscriptionCurrency(profileId, tierId, msg.sender))).getSubscription(profileId, tierId, msg.sender);
            require(cancelled == true, BBErrorCodesV01.SUBSCRIPTION_ACTIVE);
        }

        (uint256 tierSet,) = _bbSubscriptionsFactory.getSubscriptionProfile(profileId);

        uint256 price = _bbTiers.getTierPrice(profileId, tierSet, tierId, address(_currency));

        require(_currency.allowance(msg.sender, address(this)) >= price * 60, BBErrorCodesV01.INSUFFICIENT_ALLOWANCE);

        uint256 index = _totalSubscriptions;

        if(_subscriptionIndexes[profileId][tierId][msg.sender] == 0) {
            _subscriptionIndexes[profileId][tierId][msg.sender] = _totalSubscriptions + 1;
            _totalSubscriptions++;
        }
        else {
            index = _subscriptionIndexes[profileId][tierId][msg.sender] - 1;
        }

        subscriptionId = index;

        _subscriptions[index] = Subscription(
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

    function unsubscribe(uint256 profileId, uint256 tierId) external override {
        uint256 id = _getSubscriptionId(profileId, tierId, msg.sender);
        require(_subscriptions[id].subscriber == msg.sender, BBErrorCodesV01.NOT_SUBSCRIPTION_OWNER);
        require(_subscriptions[id].cancelled == false, BBErrorCodesV01.SUBSCRIPTION_CANCELLED);

        _subscriptions[id].cancelled = true;

        emit Unsubscribed(profileId, tierId, msg.sender);
    }

    function withdrawToTreasury() public {
        _currency.transfer(_bbSubscriptionsFactory.getTreasury(), _currency.balanceOf(address(this)));
    }

    function getSubscription(uint256 profileId, uint256 tierId, address account) external view returns (uint256, uint256, bool) {
        uint256 id = _getSubscriptionId(profileId, tierId, account);

        return (
            _subscriptions[id].price,
            _subscriptions[id].expiration,
            _subscriptions[id].cancelled
        );
    }

    function _getSubscriptionId(uint256 profileId, uint256 tierId, address subscriber) internal view returns (uint256) {
        require(_subscriptionIndexes[profileId][tierId][subscriber] > 0, BBErrorCodesV01.SUBSCRIPTION_NOT_EXIST);
        return _subscriptionIndexes[profileId][tierId][subscriber] - 1;
    }
}