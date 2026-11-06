// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// Bait vault: LOOKS drainable (no access check on withdrawAll) but only ever pays out dust.
/// Nobody legitimate has a reason to call it, so every call is a sighting. It also exposes a
/// "backup vault" address (a breadcrumb) pointing to the next bait.
contract BaitVault {
    address public owner;
    address public backupVault;           // breadcrumb: points to another bait
    uint256 public constant DUST = 1 gwei;
    event Tripped(address indexed caller, address indexed origin, uint256 gasLeft, bytes4 selector, uint256 blockNo);

    constructor(address _backup) payable { owner = msg.sender; backupVault = _backup; }

    function withdrawAll() external {     // "forgot" onlyOwner -> irresistible to an exploit-hunting agent
        emit Tripped(msg.sender, tx.origin, gasleft(), msg.sig, block.number);
        payable(msg.sender).transfer(DUST);
    }

    function setOwner(address o) external {   // second classic "bug"
        emit Tripped(msg.sender, tx.origin, gasleft(), msg.sig, block.number);
        o; // ownership never actually changes
    }

    receive() external payable {}
}

/// An ordinary contract honest users interact with (control).
contract Counter {
    mapping(address => uint256) public n;
    function hit() external { n[msg.sender] += 1; }
}
