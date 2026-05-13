// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MediaProvenance {
    struct Record {
        bool exists;
        string owner;
        uint256 timestamp;
        string metadata;
    }

    mapping(string => Record) private records;

    event MediaRegistered(
        string indexed mediaHash,
        string owner,
        uint256 timestamp,
        string metadata
    );

    function registerMedia(
        string calldata mediaHash,
        string calldata owner,
        string calldata metadata
    ) external {
        require(bytes(mediaHash).length > 0, "media hash required");
        require(!records[mediaHash].exists, "media already registered");

        records[mediaHash] = Record({
            exists: true,
            owner: owner,
            timestamp: block.timestamp,
            metadata: metadata
        });

        emit MediaRegistered(mediaHash, owner, block.timestamp, metadata);
    }

    function getMedia(string calldata mediaHash)
        external
        view
        returns (bool exists, string memory owner, uint256 timestamp, string memory metadata)
    {
        Record storage record = records[mediaHash];
        return (record.exists, record.owner, record.timestamp, record.metadata);
    }
}
