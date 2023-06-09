// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

interface IBBCashier {
    function buy(uint256 storeId, address buyer, uint256 expectedPrice, address currency, bytes memory buyData) external returns (bytes memory);
}