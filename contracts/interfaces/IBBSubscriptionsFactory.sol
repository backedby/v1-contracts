// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

interface IBBSubscriptionsFactory {
    function deploySubscriptions(address currency) external returns(address subscriptions);
    function isSubscriptionsDeployed(address currency) external view returns (bool);
    function getDeployedSubscriptions(address currency) external view returns (address);
    
    function setTreasury(address account) external;
    function setSubscriptionGasRequirement(uint256 requirement) external;

    function getTreasury() external view returns (address);
    function getGracePeriod() external pure returns (uint256);
    function getContributionBounds() external pure returns (uint256, uint256);
    function getSubscriptionGasRequirement() external view returns (uint256);

    function setSubscriptionCurrency(uint256 profileId, uint256 tierId, address account, address currency) external;
    function getSubscriptionCurrency(uint256 profileId, uint256 tierId, address account) external view returns (address);

    function createSubscriptionProfile(uint256 profileId, uint256 tierSet, uint256 contribution) external;
    function setContribution(uint256 profileId, uint256 contribution) external;

    function getSubscriptionProfile(uint256 profileId) external view returns (uint256 tierSet, uint256 contribution);
    function isSubscriptionProfileCreated(uint256 profileId) external view returns (bool);

    function isSubscriptionActive(uint256 profileId, uint256 tierId, address account) external view returns (bool);
}
