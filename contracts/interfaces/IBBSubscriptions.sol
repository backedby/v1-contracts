// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";

interface IBBSubscriptions is KeeperCompatibleInterface {
    function subscribe(uint256 profileId, uint256 tierId) external payable returns(uint256 subscriptionId);
    function unsubscribe(uint256 profileId, uint256 tierId) external;
    
    function withdrawToTreasury() external;

    function getSubscription(uint256 profileId, uint256 tierId, address subscriber) external view returns (uint256 price, uint256 expiration, bool cancelled);

    function setUpkeepGasRequirement(uint256 requirement) external;
    function getUpkeepGasRequirement() external view returns (uint256 requirement);
    function getSubscriptionGasRequirement() external view returns (uint256 requirement);
}