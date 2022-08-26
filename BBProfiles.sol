// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "./BBErrorsV01.sol";
import "./interfaces/IBBProfiles.sol";

contract BBProfiles is IBBProfiles {
    event NewProfile(
        uint256 profileId,
        address owner,
        address receiver,
        string cid
    );

    event EditProfile(
        uint256 profileId,
        address owner,
        address receiver,
        string cid
    );

    struct Profile {
        address owner;
        address receiver;
        string cid;
    }

    mapping(uint256 => Profile) internal _profiles;

    uint256 internal _totalProfiles;

    // Owner => Total index => Profile ID
    mapping(address => mapping(uint256 => uint256)) private _ownedProfiles;
    // Owner => Profile ID => Total index
    mapping(address => mapping(uint256 => uint256)) private _ownedProfilesIndexes;
    // Owner => Total profiles owned
    mapping(address => uint256) private _ownersTotalProfiles;

    modifier profileExists(uint256 profileId) {
      require(profileId < _totalProfiles, BBErrorCodesV01.ZERO_ADDRESS);
      _;
    }

    /*
        @notice Creates a new profile

        @param Profile owner
        @param Profiles revenue receiver
        @param Profile CID
    */
    function createProfile(address owner, address receiver, string memory cid) external override returns(uint256 profileId) {
        require(owner != address(0), BBErrorCodesV01.ZERO_ADDRESS);
        profileId = _totalProfiles;
        _profiles[_totalProfiles] = Profile(owner, receiver, cid);

        _ownedProfiles[owner][_ownersTotalProfiles[owner]] = _totalProfiles;
        _ownedProfilesIndexes[owner][_totalProfiles] = _ownersTotalProfiles[owner];
        _ownersTotalProfiles[owner]++;

        _totalProfiles++;

        emit NewProfile(_totalProfiles - 1, owner, receiver, cid);
    }

    /*
        @notice Set a profiles variables

        @param Profile ID
        @param New profile owner
        @param New profile receiver
        @param New profile CID
    */
    function editProfile(uint256 profileId, address owner, address receiver, string memory cid) external override profileExists(profileId){
        require(_profiles[profileId].owner == msg.sender, BBErrorCodesV01.NOT_OWNER);
        
        if (msg.sender != owner) {

            _ownedProfiles[msg.sender][_ownersTotalProfiles[msg.sender] - 1] = _ownedProfiles[msg.sender][_ownedProfilesIndexes[msg.sender][profileId]];
            _ownedProfilesIndexes[msg.sender][profileId] = 0;
            _ownersTotalProfiles[msg.sender]--;

            _ownedProfiles[owner][_ownersTotalProfiles[owner]] = profileId;
            _ownedProfilesIndexes[owner][profileId] = _ownersTotalProfiles[owner];
            _ownersTotalProfiles[owner]++;
        }
        
        _profiles[profileId] = Profile(owner, receiver, cid);

        emit EditProfile(profileId, owner, _profiles[profileId].receiver, cid);
    } 

    /*
        @notice Returns the total number of created profiles

        @return Total number of profiles
    */
    function totalProfiles() view external override returns (uint256) {
        return _totalProfiles;
    }

    /*
        @notice Returns a profiles values

        @param Profile ID

        @return Profile owner
        @return Profile revenue receiver
        @return Profile CID
    */
    function getProfile(uint256 profileId) view external override profileExists(profileId) returns (address, address, string memory) {
        return (_profiles[profileId].owner, _profiles[profileId].receiver, _profiles[profileId].cid);
    }

    function getOwnersProfiles(address owner) external view override returns (uint256[] memory) {
        uint256[] memory profileIds = new uint256[](_ownersTotalProfiles[owner]);

        for(uint256 i = 0; i < _ownersTotalProfiles[owner]; i++) {
            profileIds[i] = _ownedProfiles[owner][i];
        }

        return profileIds;
    }

    /*
        @notice Returns the number of profiles an address owns

        @param Owner address

        @return Profile count
    */
    function ownersTotalProfiles(address owner) view external returns (uint256) {
        return _ownersTotalProfiles[owner];
    }

    function isProfileOwner(uint256 profileId, address account) external view profileExists(profileId) returns(bool) {
        return _ownedProfiles[account][profileId] == _ownedProfilesIndexes[account][_ownedProfiles[account][profileId]] && 
                _ownedProfiles[account][profileId] < _ownersTotalProfiles[account];
    }
}
