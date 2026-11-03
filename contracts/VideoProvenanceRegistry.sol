// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title VideoProvenanceRegistry — AI研修動画 真正性公証 (Pro spec)
/// @notice Existence / precedence proof only. No NFT, no transfer, no exclusion rights.
///         Wallet-less for employees: a system address notarizes on their behalf.
contract VideoProvenanceRegistry {
    struct ProvenanceRecord {
        bytes32 sha256Hash;
        string visualPhash;
        string employeeId;
        string creatorDisplayName;
        string aiModelUsed;
        string promptSnippet;
        uint256 blockTimestamp;
        uint256 blockNumber;
        address recordedBy;
    }

    address public admin;
    bool public paused;
    uint256 public totalRecordsCount;

    mapping(uint256 => ProvenanceRecord) public records;
    mapping(bytes32 => uint256) public hashToRecordId;
    mapping(string => uint256[]) private phashToRecordIds;

    event VideoNotarized(uint256 indexed recordId, bytes32 indexed sha256Hash, string employeeId, string creatorDisplayName, uint256 timestamp);
    event AdminTransferred(address indexed previousAdmin, address indexed newAdmin);
    event Paused(bool paused);

    modifier onlyAdmin() { require(msg.sender == admin, "Only admin"); _; }
    modifier whenNotPaused() { require(!paused, "Paused"); _; }

    constructor() { admin = msg.sender; }

    function transferAdmin(address newAdmin) external onlyAdmin {
        require(newAdmin != address(0), "Zero address");
        emit AdminTransferred(admin, newAdmin);
        admin = newAdmin;
    }

    function setPaused(bool _paused) external onlyAdmin {
        paused = _paused;
        emit Paused(_paused);
    }

    function notarizeVideo(
        bytes32 _sha256Hash,
        string calldata _visualPhash,
        string calldata _employeeId,
        string calldata _creatorDisplayName,
        string calldata _aiModelUsed,
        string calldata _promptSnippet
    ) external whenNotPaused returns (uint256) {
        require(_sha256Hash != bytes32(0), "Empty hash");
        require(hashToRecordId[_sha256Hash] == 0, "Video hash already notarized. Precedence exists.");

        totalRecordsCount++;
        uint256 currentId = totalRecordsCount;
        records[currentId] = ProvenanceRecord({
            sha256Hash: _sha256Hash,
            visualPhash: _visualPhash,
            employeeId: _employeeId,
            creatorDisplayName: _creatorDisplayName,
            aiModelUsed: _aiModelUsed,
            promptSnippet: _promptSnippet,
            blockTimestamp: block.timestamp,
            blockNumber: block.number,
            recordedBy: msg.sender
        });
        hashToRecordId[_sha256Hash] = currentId;
        if (bytes(_visualPhash).length > 0) phashToRecordIds[_visualPhash].push(currentId);

        emit VideoNotarized(currentId, _sha256Hash, _employeeId, _creatorDisplayName, block.timestamp);
        return currentId;
    }

    function verifyByHash(bytes32 _sha256Hash) external view returns (
        bool isRegistered, uint256 recordId, uint256 timestamp,
        string memory creator, string memory employeeId, string memory model, string memory visualPhash
    ) {
        uint256 id = hashToRecordId[_sha256Hash];
        if (id == 0) return (false, 0, 0, "", "", "", "");
        ProvenanceRecord memory r = records[id];
        return (true, id, r.blockTimestamp, r.creatorDisplayName, r.employeeId, r.aiModelUsed, r.visualPhash);
    }

    /// @notice Candidate lookup by perceptual hash (exact pHash match; fuzzy matching is off-chain)
    function findByPhash(string calldata _visualPhash) external view returns (uint256[] memory) {
        return phashToRecordIds[_visualPhash];
    }
}
