// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IBBSubscriptionsFactory {
    function deploySubscriptions(address currency) external returns(address subscriptions);
    function isSubscriptionsDeployed(address currency) external view returns (bool deployed);
    function getDeployedSubscriptions(address currency) external view returns (address subscriptions);

    function setTreasuryOwner(address account) external;
    function setGasPriceOwner(address account) external;
    function setUpkeepGasRequirementOwner(address account) external;

    function getTreasuryOwner() external view returns (address treasury);
    function getGasPriceOwner() external view returns (address gasPriceOwner);
    function getUpkeepGasRequirementOwner() external view returns (address upkeepGasRequirementOwner);

    function setTreasury(address account) external;
    function setGasPrice(uint256 gasPrice) external;
    function setUpkeepGasRequirement(address currency, uint256 amount) external;

    function getTreasury() external view returns (address treasury);
    function getGasPrice() external view returns (uint256 gasPrice);

    function getGracePeriod() external pure returns (uint256 gracePeriod);
    function getContributionBounds() external pure returns (uint256 lower, uint256 upper);

    function setSubscriptionCurrency(uint256 profileId, uint256 tierId, address account, address currency) external;
    function getSubscriptionCurrency(uint256 profileId, uint256 tierId, address account) external view returns (address currency);

    function createSubscriptionProfile(uint256 profileId, uint256 tierSetId, uint256 contribution) external;
    function setContribution(uint256 profileId, uint256 contribution) external;

    function getSubscriptionProfile(uint256 profileId) external view returns (uint256 tierSetId, uint256 contribution);
    function isSubscriptionProfileCreated(uint256 profileId) external view returns (bool created);

    function isSubscriptionActive(uint256 profileId, uint256 tierId, address account) external view returns (bool active);
}
