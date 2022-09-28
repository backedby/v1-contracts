// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

contract testmapping {
    struct MyStruct {
        address subber;
        uint something;
    }
    mapping(uint => MyStruct) data;
    constructor() {
        data[0] = MyStruct(address(1337), 7331);
        data[1] = MyStruct(address(4444), 5555);
    }

    function d() public view returns(MyStruct[] memory rtn) {
        rtn = new MyStruct[](2);
        rtn[0] = data[0];
        rtn[1] = data[1];
    }

}