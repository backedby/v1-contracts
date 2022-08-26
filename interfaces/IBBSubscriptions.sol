// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@chainlink/contracts/src/v0.8/interfaces/KeeperCompatibleInterface.sol";

interface IBBSubscriptions is KeeperCompatibleInterface {
    function subscribe(uint256 profileId, uint256 tierId) external payable returns(uint256 subscriptionId);
    function unsubscribe(uint256 profileId, uint256 tierId) external;
    
    function withdrawToTreasury() external;

    function getSubscription(uint256 profileId, uint256 tierId, address account) external view returns (uint256 price, uint256 expiration, bool cancelled);
}