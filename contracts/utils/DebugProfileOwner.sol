// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "../interfaces/IBBPermissionsV01.sol";

contract DebugProfileOwner is IBBPermissionsV01 {
    mapping(address => bool) isOwner;
    constructor() {
        isOwner[msg.sender] = true;
    }
    function setOwner(address newguy, bool canOwner) public {
        require(isOwner[msg.sender]); // dev: not an admin
        isOwner[newguy] = canOwner;
    }
    function canViewSubscription(address member) external view override returns(bool) {
        return isOwner[member];
    }
}