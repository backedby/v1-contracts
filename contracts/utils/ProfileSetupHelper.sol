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
    bool[] _defaultDeprecated;
    address[] _defaultCurrencies;
    uint256[] _defaultMul;

    constructor(
        IBBProfiles bbProfiles,
        IBBTiers bbTiers,
        IBBSubscriptionsFactory bbSubFactory,
        uint256[] memory defaultPrices,
        string[] memory defaultCids,
        bool[] memory defaultDeprecated,
        address[] memory defaultCurrencies,
        uint256[] memory defaultMul
    ) {
        _bbProfiles = bbProfiles;
        _bbTiers = bbTiers;
        _bbSubFactory = bbSubFactory;
        _defaultPrices = defaultPrices;
        _defaultCids = defaultCids;
        _defaultDeprecated = defaultDeprecated;
        _defaultCurrencies = defaultCurrencies;
        _defaultMul = defaultMul;
    }

    function SimpleProfileSetup(string memory profileCid, uint256 contribution)
        public
        returns (uint256 profileId, uint256 tierSetId)
    {
        (profileId, tierSetId) = AdvancedProfileSetup(profileCid, _defaultPrices, _defaultCids, _defaultDeprecated, contribution);
    }

    function AdvancedProfileSetup(
        string memory profileCid,
        uint256[] memory tierPrices,
        string[] memory tierCids,
        bool[] memory tierDeprecated,
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
            tierDeprecated,
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
