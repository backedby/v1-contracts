// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

/*
import "./BBErrorsV01.sol";
BBErrorCodesV01.
BBErrorCodesV01.PROFILE_NOT_EXIST
BBErrorCodesV01.NOT_PROFILE_OWNER
BBErrorCodesV01.OUT_OF_BOUNDS
*/
library BBErrorCodesV01 {
    string public constant NOT_OWNER = "1";
    string public constant OUT_OF_BOUNDS = "2";
    string public constant NOT_SUBSCRIPTION_OWNER = "3";
    string public constant POST_NOT_EXIST = "4";
    string public constant PROFILE_NOT_EXIST = "5";
    string public constant TIER_NOT_EXIST = "6";
    string public constant SUBSCRIPTION_NOT_EXIST = "7";
    string public constant ZERO_ADDRESS = "8";
    string public constant SUBSCRIPTION_NOT_EXPIRED = "9";
    string public constant SUBSCRIPTION_CANCELLED = "10";
    string public constant UPKEEP_FAIL = "11";
    string public constant INSUFFICIENT_PREPAID_GAS = "12";
    string public constant INSUFFICIENT_ALLOWANCE = "13";
    string public constant SUBSCRIPTION_ACTIVE = "14";
    string public constant INVALID_LENGTH = "15";
    string public constant UNSUPPORTED_CURRENCY = "16";
}