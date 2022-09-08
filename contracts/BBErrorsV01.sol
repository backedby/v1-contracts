// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

library BBErrorCodesV01 {
    string public constant NOT_OWNER = "1";
    string public constant OUT_OF_BOUNDS = "2";
    string public constant NOT_SUBSCRIPTION_OWNER = "3";
    string public constant POST_NOT_EXIST = "4";
    string public constant PROFILE_NOT_EXIST = "5";
    string public constant TIER_SET_NOT_EXIST = "6";
    string public constant TIER_NOT_EXIST = "7";
    string public constant SUBSCRIPTION_NOT_EXIST = "8";
    string public constant ZERO_ADDRESS = "9";
    string public constant SUBSCRIPTION_NOT_EXPIRED = "10";
    string public constant SUBSCRIPTION_CANCELLED = "11";
    string public constant UPKEEP_FAIL = "12";
    string public constant INSUFFICIENT_PREPAID_GAS = "13";
    string public constant INSUFFICIENT_ALLOWANCE = "14";
    string public constant INSUFFICIENT_BALANCE = "15";
    string public constant SUBSCRIPTION_ACTIVE = "16";
    string public constant INVALID_LENGTH = "17";
    string public constant UNSUPPORTED_CURRENCY = "18";
    string public constant SUBSCRIPTION_PROFILE_ALREADY_EXISTS = "19";
}