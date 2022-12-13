// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import {IBBGasOracle} from "../interfaces/IBBGasOracle.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract DebugGasOracle is IBBGasOracle, Ownable {
    uint256 _gasPrice = 30 gwei;
    function getGasPrice() external view override returns (uint256) {
        return _gasPrice;
    }

    function setGasPrice(uint256 newPrice) public onlyOwner {
        _gasPrice = newPrice;
    }
}
