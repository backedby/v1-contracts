// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

import "./BBErrorsV01.sol";

import "./interfaces/IBBProfiles.sol";
import "./interfaces/IBBStoreRouter.sol";
import "./interfaces/IBBCashier.sol";

contract BBStoreRouter is IBBStoreRouter {
    event NewStore (
        uint256 storeId,
        uint256 profileId,
        uint256 contribution,
        address nft,
        address cashier,
        string cid
    );

    event EditStore (
        uint256 storeId,
        uint256 profileId,
        uint256 contribution,
        address nft,
        address cashier,
        string cid
    );
    
    event BuyItem (
        uint256 storeId,
        uint256 amount,
        address currency
    );

    struct Store {
        uint256 profileId;
        uint256 contribution;
        address nft;
        address cashier;
        string cid;
    }
    
    // Store ID => Store data
    mapping(uint256 => Store) _stores;
    uint256 _totalStores;

    IBBProfiles internal immutable _bbProfiles;

    uint256 internal constant _contributionLower = 1;
    uint256 internal constant _contributionUpper = 100;

    constructor(address bbProfiles) {
        _bbProfiles = IBBProfiles(bbProfiles);
    }

    /*
        @dev Reverts if store ID does not exist

        @param Store ID
    */
    modifier storeExists(uint256 storeId) {
        require(storeId < _totalStores);
        _;
    }

    /*
        @dev Reverts if msg.sender is not profile IDs owner

        @param Profile ID
    */
    modifier onlyProfileOwner(uint256 profileId) {
        (address profileOwner,,) = _bbProfiles.getProfile(profileId);
        require(profileOwner == msg.sender, BBErrorCodesV01.NOT_OWNER);
        _;
    }

    /*
        @notice Returns the total number of created stores

        @return Total number of stores
    */
    function totalStores() external view override returns (uint256) {
        return _totalStores;
    }

    /*
        @notice Returns a stores variables

        @param Store ID

        @return Profile that owns this store
        @return Stores treasury contribution percentage
        @return NFT contract associated with the store
        @return Cashier contract associated with the store
        @return Store CID        
    */
    function getStore(uint256 storeId) external view override storeExists(storeId) returns (uint256, uint256, address, address, string memory) {
        return (_stores[storeId].profileId, _stores[storeId].contribution, _stores[storeId].nft, _stores[storeId].cashier, _stores[storeId].cid);
    }

    /*
        @notice Creates a new store

        @param Profile that owns this store
        @param Stores treasury contribution percentage
        @param NFT contract associated with the store
        @param Cashier contract associated with the store
        @param Store CID

        @return Created stores ID
    */
    function createStore(uint256 profileId, uint256 contribution, address nft, address cashier, string memory cid) external override onlyProfileOwner(profileId) returns (uint256 storeId) {
        require(contribution >= _contributionLower, BBErrorCodesV01.OUT_OF_BOUNDS);
        require(contribution <= _contributionUpper, BBErrorCodesV01.OUT_OF_BOUNDS);

        storeId = _totalStores;

        _stores[_totalStores] = Store(profileId, contribution, nft, cashier, cid);
        _totalStores++;

        emit NewStore(storeId, profileId, contribution, nft, cashier, cid);
    }

    /*
        @notice Set an existing profiles variables
    
        @param Store ID
        @param Profile that owns this store
        @param Stores treasury contribution percentage
        @param NFT contract associated with the store
        @param Cashier contract associated with the store
        @param Store CID    
    */
    function editStore(uint256 storeId, uint256 profileId, uint256 contribution, address nft, address cashier, string memory cid) external override storeExists(storeId) onlyProfileOwner(_stores[storeId].profileId) {
        require(contribution >= _contributionLower, BBErrorCodesV01.OUT_OF_BOUNDS);
        require(contribution <= _contributionUpper, BBErrorCodesV01.OUT_OF_BOUNDS);
        
        _stores[storeId] = Store(profileId, contribution, nft, cashier, cid);

        emit EditStore(storeId, profileId, contribution, nft, cashier, cid);
    }

    /*
        @notice Buys an NFT from a store

        @param Store ID
        @param Expected purchase price 
        @param ERC20 token
        @param Buy data

        @return Returned buy data
    */
    function buy(uint256 storeId, uint256 expectedPrice, address currency, bytes memory buyData) external override storeExists(storeId) returns (bytes memory) {
        bytes memory returnData = IBBCashier(_stores[storeId].cashier).buy(storeId, msg.sender, expectedPrice, currency, buyData);

        (,address receiver,) = _bbProfiles.getProfile(_stores[storeId].profileId);

        _pay(msg.sender, receiver, expectedPrice, currency, _stores[storeId].contribution);

        emit BuyItem(storeId, expectedPrice, currency);

        return returnData;
    }

    /*
        @dev Transfer ERC20 tokens from address to profile receiver and treasury

        @param ERC20 token spender
        @param ERC20 token receiver
        @param ERC20 token amount
        @param ERC20 token contract
        @param Treasury contribution percentage

        @return True if transfer succeeded, otherwise false
    */
    function _pay(address spender, address receiver, uint256 amount, address currency, uint256 treasuryContribution) internal returns (bool) {
        IERC20 token = IERC20(currency);

        // Check that the contract has enough allowance to process this transfer
        if ((token.allowance(spender, address(this)) >= amount) && token.balanceOf(spender) >= amount) { 
            token.transferFrom(spender, address(this), amount);

            uint256 receiverAmount = (amount * (100 - treasuryContribution)) / 100;

            if(receiverAmount > 0) {
                token.transfer(receiver, receiverAmount);
            }

            // Payment processed
            return true;
        } 

        // Insufficient funds
        return false;
    }
}
