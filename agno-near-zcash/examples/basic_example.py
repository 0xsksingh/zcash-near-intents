#!/usr/bin/env python3
"""
Basic example demonstrating the Zcash AI Agent system on NEAR Intents.

This example shows how to:
1. Initialize the ZcashAgent
2. Create a multi-agent team using Agno
3. Process user requests related to Zcash operations
4. Perform privacy-preserving token swaps
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Import our modules
from zec_agent import ZcashAgent
from agno_team import create_zec_team, process_user_request

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Load environment variables
    load_dotenv(override=True)
    
    # Get account file path from environment
    account_path = os.getenv('NEAR_ACCOUNT_FILE', './account_file.json')
    
    try:
        print("\n=== Initializing Zcash AI Agent ===\n")
        
        # Initialize the ZEC agent
        zec_agent = ZcashAgent(account_path)
        
        # Get and display the current portfolio
        portfolio = zec_agent.get_portfolio()
        print("Current Portfolio:")
        for token, balance in portfolio.items():
            print(f"  {token}: {balance}")
        
        # Example of portfolio analysis
        analysis = zec_agent.analyze_portfolio()
        print("\nPortfolio Analysis:")
        print(f"  Total Value (NEAR): {analysis['total_value_near']}")
        print(f"  Privacy Ratio: {analysis['privacy_ratio']}%")
        print("  Distribution:")
        for token, percentage in analysis['distributions'].items():
            print(f"    {token}: {percentage:.2f}%")
        
        # Example of using the multi-agent team
        print("\n=== Interacting with the ZEC AI Team ===\n")
        
        # Create the ZEC team
        zec_team = create_zec_team(zec_agent)
        
        # Example user requests
        example_requests = [
            "What's the current state of my portfolio and how can I improve its privacy?",
            "I want to swap 0.5 NEAR to ZEC with maximum privacy. What should I consider?",
            "What's the market outlook for ZEC and is now a good time to accumulate?"
        ]
        
        # Process each request
        for request in example_requests:
            print(f"\n\n=== User Request: {request} ===\n")
            response = process_user_request(zec_agent, request)
            print(response)
        
        # Example of a token swap if there's sufficient balance
        near_balance = portfolio.get('NEAR', 0)
        if near_balance > 1.0:
            print("\n\n=== Executing a NEAR to ZEC Swap with Shielding ===\n")
            
            # Deposit NEAR for intent operations (if needed)
            try:
                deposit_result = zec_agent.deposit_near(0.1)
                print(f"Deposit result: {deposit_result}")
            except Exception as e:
                if "already registered" in str(e).lower():
                    print("NEAR already deposited for intent operations")
                else:
                    raise
            
            # Execute the swap
            swap_amount = 0.5
            print(f"Swapping {swap_amount} NEAR to ZEC with shielded privacy...")
            result = zec_agent.swap_to_zec('NEAR', swap_amount, 'shielded')
            print(f"Swap result: {result}")
            
            # Update and display the new portfolio
            updated_portfolio = zec_agent.get_portfolio()
            print("\nUpdated Portfolio:")
            for token, balance in updated_portfolio.items():
                print(f"  {token}: {balance}")
        else:
            print("\n\n=== Insufficient NEAR balance for swap demonstration ===")
            print(f"Current NEAR balance: {near_balance}, need at least 1.0 NEAR to demonstrate swap")
        
        print("\n=== Example completed successfully ===")
    
    except Exception as e:
        logging.error(f"Error in example: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 