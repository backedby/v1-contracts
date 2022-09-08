// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

interface IBBPermissionsV01 {
    function canViewSubscription(address account) external view returns(bool);
}
