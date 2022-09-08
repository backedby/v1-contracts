// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract TestUsd is ERC20 {
    constructor (string memory _name, string memory _symbol) ERC20(_name,_symbol) {
        _mint(msg.sender, (10**12) * (10**18));
    }
}

contract TokenFaucet {
    IERC20 private _token;

    constructor(){
        _token = new TestUsd("Test USD", "tUSD");
    }

    function tokenAddress() external view returns(address) {
        return address(_token);
    }

    function getTokens(address receiver, uint256 amount) external {
        _token.transfer(receiver, amount);
    }
}