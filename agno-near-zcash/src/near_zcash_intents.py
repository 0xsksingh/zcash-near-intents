"""
NEAR Intents with Zcash Integration - Core Functions

This module extends the NEAR Intents protocol with specialized support for Zcash (ZEC) transactions,
enabling shielded operations and cross-chain transfers through the NEAR Intents protocol.
"""

from typing import Dict, List, TypedDict, Union, Optional
import os
import json
import base64
import base58
import random
import requests
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Constants
MAX_GAS = 300 * 10 ** 12
SOLVER_BUS_URL = "https://solver-relay-v2.chaindefuser.com/rpc"

# Add Zcash to the asset map
ASSET_MAP = {
    'USDC': { 
        'token_id': 'a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.factory.bridge.near',
        'omft': 'eth-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.omft.near',
        'decimals': 6,
    },
    'NEAR': {
        'token_id': 'wrap.near',
        'decimals': 24,
    },
    'ZEC': {  # Add Zcash support
        'token_id': 'zcash.factory.bridge.near',  # Example token ID for Zcash on NEAR
        'omft': 'zcash-token.omft.near',  # Example OMFT for Zcash
        'decimals': 8,  # Zcash has 8 decimal places
        'shielded': True,  # Flag indicating shielded transaction support
    }
}

class Intent(TypedDict):
    intent: str
    diff: Dict[str, str]

class Quote(TypedDict):
    nonce: str
    signer_id: str
    verifying_contract: str
    deadline: str
    intents: List[Intent]

class ShieldingOptions(TypedDict):
    enabled: bool
    memo: Optional[str]
    viewing_key: Optional[str]

class ShieldedIntent(TypedDict):
    intent: str
    diff: Dict[str, str]
    shielding: ShieldingOptions

class ZcashCommitment(TypedDict):
    standard: str
    payload: Union[str, Dict]
    signature: str
    public_key: str
    shield_params: Optional[Dict]

def get_asset_id(token: str) -> str:
    """Get the asset identifier in the format expected by the solver bus."""
    if token == 'NEAR':
        return 'near'  # Native NEAR token
    elif token == 'ZEC':
        return 'nep141:%s' % ASSET_MAP[token]['token_id']  # ZEC on NEAR
    elif token == 'USDC':
        return 'nep141:a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.factory.bridge.near'  # USDC on NEAR
    return 'nep141:%s' % ASSET_MAP[token]['token_id']

def to_decimals(amount: float, decimals: int) -> str:
    """Convert human-readable amount to on-chain decimal representation."""
    return str(int(amount * 10 ** decimals))

def from_decimals(amount: str, decimals: int) -> float:
    """Convert on-chain decimal representation to human-readable amount."""
    return float(amount) / 10 ** decimals

def create_shielded_token_diff_quote(account, token_in: str, amount_in: float, 
                                    token_out: str, amount_out: float,
                                    shield_options: Optional[ShieldingOptions] = None) -> ZcashCommitment:
    """
    Creates a shielded quote for a token swap involving ZEC.
    
    Args:
        account: The NEAR account object
        token_in: Input token symbol (e.g., 'NEAR', 'ZEC')
        amount_in: Amount of input token to swap
        token_out: Output token symbol (e.g., 'ZEC', 'USDC')
        amount_out: Amount of output token to receive
        shield_options: Optional shielding parameters for privacy
        
    Returns:
        A signed commitment with shielding parameters
    """
    # Generate a random nonce
    nonce = base64.b64encode(random.getrandbits(256).to_bytes(32, byteorder='big')).decode('utf-8')
    
    # Default shielding options
    if shield_options is None and (token_in == 'ZEC' or token_out == 'ZEC'):
        shield_options = ShieldingOptions(enabled=True, memo=None, viewing_key=None)
    elif shield_options is None:
        shield_options = ShieldingOptions(enabled=False, memo=None, viewing_key=None)
    
    # Create the quote with proper token identifiers
    quote = Quote(
        nonce=nonce,
        signer_id=account.account_id,
        verifying_contract='intents.near',
        deadline=str(int(time.time() * 1000) + 120000),  # 2 minutes from now
        intents=[
            Intent(
                intent='token_diff',
                diff={
                    get_asset_id(token_in): '-' + to_decimals(float(amount_in), ASSET_MAP[token_in]['decimals']),
                    get_asset_id(token_out): to_decimals(float(amount_out), ASSET_MAP[token_out]['decimals'])
                }
            )
        ]
    )
    
    # Sign the quote
    quote_data = json.dumps(quote).encode('utf-8')
    signature = 'ed25519:' + base58.b58encode(account.signer.sign(quote_data)).decode('utf-8')
    public_key = 'ed25519:' + base58.b58encode(account.signer.public_key).decode('utf-8')
    
    # Create commitment with shield parameters if needed
    if shield_options['enabled']:
        return ZcashCommitment(
            standard="raw_ed25519",
            payload=json.dumps(quote),
            signature=signature,
            public_key=public_key,
            shield_params={
                "shielded": True,
                "memo": shield_options['memo'],
                "viewing_key": shield_options['viewing_key']
            }
        )
    else:
        return ZcashCommitment(
            standard="raw_ed25519",
            payload=json.dumps(quote),
            signature=signature,
            public_key=public_key,
            shield_params=None
        )

def publish_shielded_intent(signed_intent: ZcashCommitment) -> Dict:
    """Publishes a shielded intent to the Solver Bus."""
    logging.info("Publishing shielded intent to Solver Bus")
    
    try:
        response = requests.post(
            SOLVER_BUS_URL,
            json={
                "method": "intents_publishIntent",
                "params": {"signed_data": signed_intent},
                "id": 1,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()["result"]
    except Exception as e:
        logging.error(f"Failed to publish shielded intent: {e}")
        raise

def intent_swap_zec(account, token_in: str, amount_in: float, token_out: str, 
                    privacy_level: str = 'default') -> Dict:
    """
    Execute a swap intent involving ZEC, with options for privacy levels.
    
    Args:
        account: The NEAR account object
        token_in: Input token symbol (e.g., 'NEAR', 'ZEC')
        amount_in: Amount of input token to swap
        token_out: Output token symbol (e.g., 'ZEC', 'USDC') 
        privacy_level: Privacy level for the transaction ('default', 'shielded', 'transparent')
        
    Returns:
        Response from the Solver Bus
    """
    logging.info(f"Executing swap: {amount_in} {token_in} -> {token_out} with privacy level: {privacy_level}")
    
    # Create intent request
    request = IntentRequest().set_asset_in(token_in, amount_in).set_asset_out(token_out)
    
    # Fetch options from the Solver Bus
    options = fetch_options(request)
    if not options:
        raise ValueError(f"No swap options available for {token_in} to {token_out}")
    
    logging.info(f"Found {len(options)} swap options")
    best_option = select_best_option(options)
    logging.info(f"Selected best option: {best_option}")
    
    # Set up shielding options based on privacy level
    if privacy_level == 'shielded' and (token_in == 'ZEC' or token_out == 'ZEC'):
        shield_options = ShieldingOptions(
            enabled=True,
            memo=f"Swap {token_in} to {token_out}",
            viewing_key=None  # In a real implementation, this would be handled securely
        )
    else:
        shield_options = ShieldingOptions(enabled=False, memo=None, viewing_key=None)
    
    # Create and sign the intent
    signed_intent = create_shielded_token_diff_quote(
        account, 
        token_in, 
        amount_in, 
        token_out, 
        float(best_option['amount_out']),
        shield_options
    )
    
    # Publish the intent
    response = publish_shielded_intent(signed_intent)
    logging.info("Swap request submitted successfully")
    return response

class IntentRequest:
    """Request for intent execution with support for ZEC operations."""
    
    def __init__(self, request=None, thread=None, min_deadline_ms=120000):
        self.request = request or {}
        self.thread = thread
        self.min_deadline_ms = min_deadline_ms

    def set_asset_in(self, asset_name, amount):
        """Set the input asset for the intent."""
        if asset_name not in ASSET_MAP:
            raise ValueError(f"Unsupported asset: {asset_name}")
        
        self.request["assetIn"] = get_asset_id(asset_name)
        self.request["amountIn"] = to_decimals(amount, ASSET_MAP[asset_name]["decimals"])
        return self

    def set_asset_out(self, asset_name, amount=None):
        """Set the output asset for the intent."""
        if asset_name not in ASSET_MAP:
            raise ValueError(f"Unsupported asset: {asset_name}")
            
        self.request["assetOut"] = get_asset_id(asset_name)
        if amount is not None:
            self.request["amountOut"] = to_decimals(amount, ASSET_MAP[asset_name]["decimals"])
        return self
        
    def serialize(self):
        """Serialize the intent request for the Solver Bus."""
        result = {
            "assets": {
                "in": self.request["assetIn"],
                "out": self.request["assetOut"],
            },
            "amounts": {
                "in": self.request["amountIn"],
            },
            "deadline": {
                "type": "relative",
                "ms": self.min_deadline_ms
            }
        }
        
        if "amountOut" in self.request:
            result["amounts"]["out"] = self.request["amountOut"]
            
        if "slippage" in self.request:
            result["slippage"] = self.request["slippage"]
            
        return result

def fetch_options(request: IntentRequest) -> List[Dict]:
    """Fetch options from the Solver Bus for a given intent request."""
    logging.info("Fetching options from Solver Bus")
    
    try:
        response = requests.post(
            SOLVER_BUS_URL,
            json={
                "method": "intents_getQuotes",
                "params": request.serialize(),
                "id": 1,
            },
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()["result"]
    except Exception as e:
        logging.error(f"Failed to fetch options: {e}")
        return []

def select_best_option(options: List[Dict]) -> Dict:
    """
    Select the best option based on the amount of output token.
    
    Args:
        options: List of options from the Solver Bus
        
    Returns:
        The option with the maximum output token amount
    """
    if not options:
        raise ValueError("No options provided")
        
    # For ZEC and private swaps, we might prioritize privacy over best rate
    # This is a simple implementation that just picks the best rate
    return max(options, key=lambda x: float(x["amount_out"])) 