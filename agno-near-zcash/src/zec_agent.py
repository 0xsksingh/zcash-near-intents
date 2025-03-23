"""
Zcash AI Agent for NEAR Intents

This agent specializes in handling Zcash transactions through the NEAR Intents protocol.
It provides privacy-preserving swap functionality and portfolio management.
"""

import os
import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import NEAR Intents with Zcash integration
from near_zcash_intents import (
    ASSET_MAP,
    ShieldingOptions,
    IntentRequest,
    intent_swap_zec,
    publish_shielded_intent,
    fetch_options,
    select_best_option,
    create_shielded_token_diff_quote,
    get_asset_id,
    to_decimals,
    from_decimals
)

class ZcashAgent:
    """
    AI agent for interacting with Zcash on NEAR Intents.
    Specializes in privacy-preserving operations and cross-chain swaps.
    """
    
    def __init__(self, account_file: str):
        """
        Initialize the ZEC agent with a NEAR account.
        
        Args:
            account_file: Path to the NEAR account credentials file
        """
        self.account_file = account_file
        self.account = self._load_account(account_file)
        self._validate_account()
        self._register_with_intents()
        self.portfolio = {}
        self.privacy_preferences = {
            'default_level': 'shielded',  # Options: 'transparent', 'shielded'
            'auto_shield': True,          # Automatically shield incoming ZEC
            'memos_enabled': True,        # Include transaction memos
            'viewing_keys': {}            # Stored securely
        }
        logging.info(f"ZEC agent initialized for account {self.account.account_id}")
    
    def _load_account(self, account_file: str):
        """Load NEAR account from file."""
        if not os.path.exists(account_file):
            raise FileNotFoundError(f"Account file not found: {account_file}")
        
        try:
            # Import here to avoid circular imports
            from near_zcash_intents import account as load_account
            return load_account(account_file)
        except Exception as e:
            logging.error(f"Failed to load account: {e}")
            raise
    
    def _validate_account(self):
        """Validate that the account exists and has sufficient balance."""
        try:
            account_state = self.account.state()
            if not account_state:
                raise ValueError(f"Account {self.account.account_id} not found or not accessible")
                
            balance_near = float(account_state['amount']) / 10**24  # Convert yoctoNEAR to NEAR
            logging.info(f"Account state: Balance {balance_near:.4f} NEAR")
            
            if balance_near < 0.1:  # Minimum balance check
                raise ValueError(f"Insufficient balance ({balance_near} NEAR). Minimum required: 0.1 NEAR")
        except Exception as e:
            logging.error(f"Error checking account state: {e}")
            raise
    
    def _register_with_intents(self):
        """Register account with the NEAR Intents contract."""
        try:
            # Import here to avoid circular imports
            from near_zcash_intents import register_intent_public_key
            register_intent_public_key(self.account)
            logging.info("Public key registered successfully with intents.near contract")
        except Exception as e:
            error_str = str(e)
            if "public key already exists" in error_str or "already registered" in error_str.lower():
                logging.info("Public key already registered with intents.near contract")
            else:
                logging.error(f"Failed to register public key: {e}")
                raise
    
    def deposit_near(self, amount: float) -> Dict:
        """
        Deposit NEAR for intent operations.
        
        Args:
            amount: Amount of NEAR to deposit
            
        Returns:
            Transaction result
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than 0")
        
        logging.info(f"Depositing {amount} NEAR for intent operations")
        
        try:
            # Import here to avoid circular imports
            from near_zcash_intents import register_token_storage, intent_deposit
            
            # Check current balance before deposit
            account_state = self.account.state()
            if not account_state:
                raise ValueError(f"Account {self.account.account_id} not found or not accessible")
                
            balance_near = float(account_state['amount']) / 10**24
            
            if balance_near < amount:
                raise ValueError(f"Insufficient balance ({balance_near:.4f} NEAR) for deposit of {amount:.4f} NEAR")
            
            # Register storage if needed
            try:
                register_token_storage(self.account, "NEAR", other_account="intents.near")
                logging.info("Storage registered for NEAR token")
            except Exception as e:
                if "already registered" not in str(e).lower():
                    raise
                logging.info("Storage already registered for NEAR token")
            
            # Deposit NEAR
            result = intent_deposit(self.account, "NEAR", float(amount))
            logging.info("Deposit transaction submitted successfully")
            return result
        except Exception as e:
            logging.error(f"Failed to deposit NEAR: {e}")
            raise
    
    def swap_to_zec(self, token_in: str, amount_in: float, privacy_level: Optional[str] = None) -> Dict:
        """
        Swap a token to ZEC with optional privacy settings.
        
        Args:
            token_in: Input token symbol (e.g., 'NEAR', 'USDC')
            amount_in: Amount of input token to swap
            privacy_level: Privacy level for the transaction ('transparent', 'shielded')
            
        Returns:
            Transaction result
        """
        if amount_in <= 0:
            raise ValueError("Swap amount must be greater than 0")
        
        if token_in not in ASSET_MAP:
            raise ValueError(f"Unsupported input token: {token_in}. Supported tokens: {list(ASSET_MAP.keys())}")
        
        # Use default privacy level if not specified
        if privacy_level is None:
            privacy_level = self.privacy_preferences['default_level']
        
        logging.info(f"Swapping {amount_in} {token_in} to ZEC with privacy level: {privacy_level}")
        
        try:
            result = intent_swap_zec(
                account=self.account,
                token_in=token_in,
                amount_in=amount_in,
                token_out="ZEC",
                privacy_level=privacy_level
            )
            
            logging.info(f"Successfully swapped {amount_in} {token_in} to ZEC")
            return result
        except Exception as e:
            logging.error(f"Failed to swap to ZEC: {e}")
            raise
    
    def swap_from_zec(self, token_out: str, amount_in: float, privacy_level: Optional[str] = None) -> Dict:
        """
        Swap ZEC to another token with optional privacy settings.
        
        Args:
            token_out: Output token symbol (e.g., 'NEAR', 'USDC')
            amount_in: Amount of ZEC to swap
            privacy_level: Privacy level for the transaction ('transparent', 'shielded')
            
        Returns:
            Transaction result
        """
        if amount_in <= 0:
            raise ValueError("Swap amount must be greater than 0")
        
        if token_out not in ASSET_MAP:
            raise ValueError(f"Unsupported output token: {token_out}. Supported tokens: {list(ASSET_MAP.keys())}")
        
        # Use default privacy level if not specified
        if privacy_level is None:
            privacy_level = self.privacy_preferences['default_level']
        
        logging.info(f"Swapping {amount_in} ZEC to {token_out} with privacy level: {privacy_level}")
        
        try:
            result = intent_swap_zec(
                account=self.account,
                token_in="ZEC",
                amount_in=amount_in,
                token_out=token_out,
                privacy_level=privacy_level
            )
            
            logging.info(f"Successfully swapped {amount_in} ZEC to {token_out}")
            return result
        except Exception as e:
            logging.error(f"Failed to swap from ZEC: {e}")
            raise
    
    def get_balance(self, token: str) -> float:
        """
        Get the balance of a specific token.
        
        Args:
            token: Token symbol (e.g., 'NEAR', 'ZEC', 'USDC')
            
        Returns:
            Token balance
        """
        if token not in ASSET_MAP:
            raise ValueError(f"Unsupported token: {token}. Supported tokens: {list(ASSET_MAP.keys())}")
        
        logging.info(f"Getting balance for {token}")
        
        try:
            # For native NEAR token
            if token == "NEAR":
                account_state = self.account.state()
                balance = float(account_state['amount']) / 10**24
            else:
                # For other tokens, query the token contract
                token_id = ASSET_MAP[token]['token_id']
                balance_raw = self.account.view_function(
                    token_id,
                    'ft_balance_of',
                    {'account_id': self.account.account_id}
                )
                
                if not balance_raw or not balance_raw.get('result'):
                    return 0.0
                
                # Convert raw balance to human-readable amount
                balance = from_decimals(balance_raw['result'], ASSET_MAP[token]['decimals'])
            
            logging.info(f"Balance for {token}: {balance}")
            return balance
        except Exception as e:
            logging.error(f"Failed to get balance for {token}: {e}")
            return 0.0
    
    def get_portfolio(self) -> Dict[str, float]:
        """
        Get the full portfolio with balances for all supported tokens.
        
        Returns:
            Dictionary mapping token symbols to balances
        """
        logging.info("Getting full portfolio")
        
        portfolio = {}
        for token in ASSET_MAP.keys():
            try:
                portfolio[token] = self.get_balance(token)
            except Exception as e:
                logging.warning(f"Failed to get balance for {token}: {e}")
                portfolio[token] = 0.0
        
        self.portfolio = portfolio
        return portfolio
    
    def set_privacy_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Update privacy preferences for Zcash operations.
        
        Args:
            preferences: Dictionary with privacy settings
        """
        valid_keys = {
            'default_level', 'auto_shield', 'memos_enabled', 'viewing_keys'
        }
        
        # Validate preferences
        for key in preferences:
            if key not in valid_keys:
                logging.warning(f"Unknown privacy preference: {key}")
        
        # Update preferences
        for key in valid_keys:
            if key in preferences:
                self.privacy_preferences[key] = preferences[key]
        
        logging.info(f"Updated privacy preferences: {self.privacy_preferences}")
    
    def analyze_portfolio(self) -> Dict:
        """
        Analyze the current portfolio and provide insights.
        
        Returns:
            Analysis results including token distribution and value
        """
        logging.info("Analyzing portfolio")
        
        # Get current portfolio
        portfolio = self.get_portfolio()
        
        # Calculate total value in NEAR (simplified)
        # In a real implementation, we would fetch exchange rates
        total_value_near = portfolio.get('NEAR', 0.0)
        
        # Add placeholder values for other tokens (would use real rates in production)
        zec_value_near = portfolio.get('ZEC', 0.0) * 10  # Example rate: 1 ZEC = 10 NEAR
        usdc_value_near = portfolio.get('USDC', 0.0) * 0.25  # Example rate: 1 USDC = 0.25 NEAR
        
        total_value_near += zec_value_near + usdc_value_near
        
        # Calculate distributions
        distributions = {}
        if total_value_near > 0:
            for token, balance in portfolio.items():
                if token == 'NEAR':
                    value_near = balance
                elif token == 'ZEC':
                    value_near = balance * 10  # Example rate
                elif token == 'USDC':
                    value_near = balance * 0.25  # Example rate
                else:
                    value_near = 0
                
                distributions[token] = (value_near / total_value_near) * 100
        
        analysis = {
            'portfolio': portfolio,
            'total_value_near': total_value_near,
            'distributions': distributions,
            'privacy_ratio': self._calculate_privacy_ratio(portfolio)
        }
        
        logging.info(f"Portfolio analysis complete: {analysis}")
        return analysis
    
    def _calculate_privacy_ratio(self, portfolio: Dict[str, float]) -> float:
        """
        Calculate the ratio of privacy-preserving assets in the portfolio.
        
        Args:
            portfolio: Dictionary mapping token symbols to balances
            
        Returns:
            Percentage of portfolio in privacy-preserving assets
        """
        total_value = sum(portfolio.values())
        if total_value <= 0:
            return 0.0
        
        # ZEC is our privacy-preserving asset
        privacy_value = portfolio.get('ZEC', 0.0)
        return (privacy_value / total_value) * 100


def main():
    """
    Example usage of the ZEC agent.
    """
    # Path to account file (would be set by environment in production)
    account_path = os.getenv('NEAR_ACCOUNT_FILE', './account_file.json')
    
    try:
        # Initialize the ZEC agent
        agent = ZcashAgent(account_path)
        
        # Get and display portfolio
        portfolio = agent.get_portfolio()
        print("Current Portfolio:")
        for token, balance in portfolio.items():
            print(f"  {token}: {balance}")
        
        # Example swap (only executed if there's sufficient balance)
        near_balance = portfolio.get('NEAR', 0)
        if near_balance > 1.0:
            print(f"\nSwapping 1.0 NEAR to ZEC (shielded)...")
            result = agent.swap_to_zec('NEAR', 1.0, 'shielded')
            print(f"Swap result: {result}")
        
        # Analyze portfolio
        analysis = agent.analyze_portfolio()
        print("\nPortfolio Analysis:")
        print(f"  Total Value (NEAR): {analysis['total_value_near']}")
        print(f"  Privacy Ratio: {analysis['privacy_ratio']}%")
        print("  Distribution:")
        for token, percentage in analysis['distributions'].items():
            print(f"    {token}: {percentage:.2f}%")
    
    except Exception as e:
        logging.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 