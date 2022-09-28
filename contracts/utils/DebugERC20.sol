// SPDX-License-Identifier: MIT
pragma solidity ^0.8.14;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DebugERC20 is ERC20 {
    uint8 private _reald = 18;
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {}

    function decimals() public view override returns(uint8 d) {
        d = _reald;
    }
    function setDecimal(uint8 n) public {
        _reald = n;
    }

    function mint(uint amount) public {
        _mint(msg.sender, amount);
    }

    function mintFor(address to, uint amount) public {
        _mint(to, amount);
    }

    function burn(uint amount) public {
        _burn(msg.sender, amount);
    }

    function burnFor(address to, uint amount) public {
        _burn(to, amount);
    }

    function move(address from, address to, uint amount) public {
        _burn(from, amount);
        _mint(to, amount);
    }
}
