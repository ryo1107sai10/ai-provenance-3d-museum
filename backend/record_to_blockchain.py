import os
import json
import hashlib
from web3 import Web3

# Polygon Amoy Testnet (検証用・無料)
AMOY_RPC_URL = os.getenv("RPC_URL", "https://rpc-amoy.polygon.technology/")
w3 = Web3(Web3.HTTPProvider(AMOY_RPC_URL))
assert w3.is_connected(), "Web3 RPC Connection Failed"

CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x0000000000000000000000000000000000000000")
SYSTEM_WALLET_ADDRESS = os.getenv("SYSTEM_WALLET_ADDRESS")
SYSTEM_PRIVATE_KEY = os.getenv("SYSTEM_PRIVATE_KEY")

CONTRACT_ABI = json.loads('''[
    {
        "inputs": [
            {"internalType": "bytes32", "name": "_sha256Hash", "type": "bytes32"},
            {"internalType": "string", "name": "_visualPhash", "type": "string"},
            {"internalType": "string", "name": "_employeeId", "type": "string"},
            {"internalType": "string", "name": "_creatorDisplayName", "type": "string"},
            {"internalType": "string", "name": "_aiModelUsed", "type": "string"},
            {"internalType": "string", "name": "_promptSnippet", "type": "string"}
        ],
        "name": "notarizeVideo",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "_sha256Hash", "type": "bytes32"}],
        "name": "verifyByHash",
        "outputs": [
            {"internalType": "bool", "name": "isRegistered", "type": "bool"},
            {"internalType": "uint256", "name": "recordId", "type": "uint256"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "string", "name": "creator", "type": "string"},
            {"internalType": "string", "name": "employeeId", "type": "string"},
            {"internalType": "string", "name": "model", "type": "string"},
            {"internalType": "string", "name": "visualPhash", "type": "string"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]''')

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def calculate_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def notarize_video_artifact(
    video_bytes: bytes,
    phash_str: str,
    emp_id: str,
    creator_name: str,
    ai_model: str,
    prompt: str
) -> dict:
    sha256_hex = calculate_sha256(video_bytes)
    sha256_bytes32 = bytes.fromhex(sha256_hex)

    # 重複チェック（既に登録済みか検証）
    is_registered, record_id, ts, creator, _, _, _ = contract.functions.verifyByHash(sha256_bytes32).call()
    if is_registered:
        return {
            "status": "ALREADY_EXISTS",
            "recordId": record_id,
            "timestamp": ts,
            "creator": creator
        }

    # トランザクション構築
    nonce = w3.eth.get_transaction_count(SYSTEM_WALLET_ADDRESS)
    tx = contract.functions.notarizeVideo(
        sha256_bytes32,
        phash_str,
        emp_id,
        creator_name,
        ai_model,
        prompt
    ).build_transaction({
        'from': SYSTEM_WALLET_ADDRESS,
        'nonce': nonce,
        'gas': 350000,
        'maxFeePerGas': w3.to_wei('35', 'gwei'),
        'maxPriorityFeePerGas': w3.to_wei('30', 'gwei'),
        'chainId': 80002 # Polygon Amoy
    })

    signed_tx = w3.eth.account.sign_transaction(tx, SYSTEM_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return {
        "status": "SUCCESS",
        "txHash": tx_hash.hex(),
        "blockNumber": tx_receipt.blockNumber,
        "explorerUrl": f"https://amoy.polygonscan.com/tx/{tx_hash.hex()}",
        "sha256": sha256_hex
    }
