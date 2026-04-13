#!/usr/bin/env python3
import sys
import requests

# CONFIGURATION
RPC_URL = "https://mainnet.base.org"
METHOD = "eth_getTransactionByHash"

def get_tx_input_rpc(tx_hash):
    """Fetches transaction data directly via JSON-RPC."""
    print(f"")
    print(f"Querying RPC for transaction hash: {tx_hash}")
    print(f"")
    print(f"Sending RPC request to {RPC_URL} via {METHOD} to fetch transaction details...")
    print(f"")

    payload = {
        "jsonrpc": "2.0",
        "method": METHOD,
        "params": [tx_hash],
        "id": 1
    }
    
    try:
        response = requests.post(RPC_URL, json=payload)
        response.raise_for_status()
        json_data = response.json()
        
        if "error" in json_data:
            print(f"RPC Error: {json_data['error'].get('message')}")
            sys.exit(1)
            
        result = json_data.get("result")
        if not result:
            print(f"Error: Transaction hash not found.")
            sys.exit(1)
            
        return result.get("input")
        
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")
        sys.exit(1)

def extract_sender_from_input(input_hex):
    """Parses the ERC-4337 handleOps input data via byte offsets."""
    if not input_hex or len(input_hex) < 328:
        return None
    
    # Normalize input
    data = input_hex[2:] if input_hex.startswith('0x') else input_hex
    selector = data[:8]

    if selector == "765e827f":
        print("Input extracted, matches handleOps selector 0x765e827f... proceeding to parse the sender address from the user op within...")
        
        # UserOp[0].sender is the first word of the struct.
        # Based on the fixed layout of the EntryPoint handleOps(UserOperation[], address):
        # The sender address word starts at index 264.
        sender_word = data[264:328]
        
        # Extract the last 40 characters (20 bytes) to get the clean address
        return "0x" + sender_word[-40:]
    else:
        print(f"Error: Selector {selector} does not match handleOps (765e827f).")
        return None

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <TX_HASH>")
        sys.exit(1)

    tx_hash = sys.argv[1]
    
    # 1. Fetch transaction input
    input_hex = get_tx_input_rpc(tx_hash)
    
    # 2. Extract sender
    sender = extract_sender_from_input(input_hex)
    
    # 3. Output result
    if sender:
        print("")
        print("════════════════════════════════════════════════════════════")
        print(f"SENDER ADDRESS EXTRACTED -> {sender}")
        print("════════════════════════════════════════════════════════════")
        print("")
    else:
        print("\nFailed to extract sender address. Transaction may not be an ERC-4337 UserOp.")

if __name__ == "__main__":
    main()
