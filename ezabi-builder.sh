#!/bin/bash
#crlf fix
brownieExe="brownie"

if [ -f `which brownie.exe` ]; then
    brownieExe="$brownieExe.exe"
fi

echo compiling contracts
$brownieExe compile -a

echo cleaning up old abis in abis/
rm -f ./abis/*

echo copying abi files to abis/
for i in ./build/contracts/*.json; do jq .abi $i > "./abis/`basename $i`"; done
