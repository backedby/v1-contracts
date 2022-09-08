// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "../interfaces/IBBProfiles.sol";
import "../interfaces/IBBTiers.sol";
import "../interfaces/IBBSubscriptionsFactory.sol";

contract ProfileSetupHelper {
    IBBProfiles _bbProfiles;
    IBBTiers _bbTiers;
    IBBSubscriptionsFactory _bbSubFactory;
    uint256[] _defaultPrices;
    string[] _defaultCids;
    address[] _defaultCurrencies;
    uint256[] _defaultMul;

    constructor(
        IBBProfiles bbProfiles,
        IBBTiers bbTiers,
        IBBSubscriptionsFactory bbSubFactory,
        uint256[] memory defaultPrices,
        string[] memory defaultCids,
        address[] memory defaultCurrencies,
        uint256[] memory defaultMul
    ) {
        _bbProfiles = bbProfiles;
        _bbTiers = bbTiers;
        _bbSubFactory = bbSubFactory;
        _defaultPrices = defaultPrices;
        _defaultCids = defaultCids;
        _defaultCurrencies = defaultCurrencies;
        _defaultMul = defaultMul;
    }

    function SimpleProfileSetup(string memory profileCid, uint256 contribution)
        public
        returns (uint256 profileId, uint256 tierSetId)
    {
        (profileId, tierSetId) = AdvancedProfileSetup(profileCid, _defaultPrices, _defaultCids, contribution);
    }

    function AdvancedProfileSetup(
        string memory profileCid,
        uint256[] memory tierPrices,
        string[] memory tierCids,
        uint256 contribution
    ) public returns (uint256 profileId, uint256 tierSetId) {
        profileId = _bbProfiles.createProfile(
            address(this),
            address(this),
            profileCid
        );
        tierSetId = _bbTiers.createTiers(
            profileId,
            tierPrices,
            tierCids,
            _defaultCurrencies,
            _defaultMul
        );

        _bbSubFactory.createSubscriptionProfile(
            profileId,
            tierSetId,
            contribution
        );

        _bbProfiles.editProfile(profileId, msg.sender, msg.sender, profileCid);
    }
}
