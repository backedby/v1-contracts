// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

interface IBBPermissions {
    function canViewSubscription(address account) external view returns(bool);
}
