// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IBBSubscriptionsFactory {
    function deploySubscriptions(address currency) external returns(address subscriptions);
    function isSubscriptionsDeployed(address currency) external view returns (bool deployed);
    function getDeployedSubscriptions(address currency) external view returns (address subscriptions);

    function setTreasuryOwner(address account) external;
    function setGasOracleOwner(address account) external;
    function setSubscriptionFeeOwner(address account) external;

    function getTreasuryOwner() external view returns (address treasury);
    function getGasOracleOwner() external view returns (address gasPriceOwner);
    function getSubscriptionFeeOwner() external view returns (address subscriptionFeeOwner);

    function setTreasury(address account) external;
    function setGasOracle(address account) external;
    function setSubscriptionFee(address currency, uint256 amount) external;

    function getTreasury() external view returns (address treasury);
    function getGasOracle() external view returns (address oracle);
    function getSubscriptionFee(address currency) external view returns (uint256 fee);

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
