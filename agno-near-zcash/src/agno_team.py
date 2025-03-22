"""
Multi-Agent Team for Zcash on NEAR Intents

This module implements a team of specialized agents that work together to 
provide comprehensive Zcash-based services through the NEAR Intents protocol.

The team includes:
1. Portfolio Manager: Analyzes and manages the token portfolio
2. Privacy Advisor: Recommends optimal privacy settings for transactions
3. Market Analyst: Provides market insights and pricing data
4. Transaction Coordinator: Orchestrates the overall transaction process
"""

import os
import logging
from textwrap import dedent
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import Agno components
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team

# Import ZEC Agent
from zec_agent import ZcashAgent

class ZecAgnoTool:
    """Custom tool for Agno agents to interact with the ZcashAgent."""
    
    def __init__(self, zec_agent: ZcashAgent):
        """
        Initialize the ZEC Agno tool with a ZcashAgent instance.
        
        Args:
            zec_agent: The ZcashAgent instance for performing operations
        """
        self.zec_agent = zec_agent
    
    def get_portfolio(self) -> Dict[str, float]:
        """
        Get the current token portfolio.
        
        Returns:
            Dictionary mapping token symbols to balances
        """
        return self.zec_agent.get_portfolio()
    
    def analyze_portfolio(self) -> Dict:
        """
        Analyze the current portfolio and provide insights.
        
        Returns:
            Analysis results including token distribution and value
        """
        return self.zec_agent.analyze_portfolio()
    
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
        return self.zec_agent.swap_to_zec(token_in, amount_in, privacy_level)
    
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
        return self.zec_agent.swap_from_zec(token_out, amount_in, privacy_level)
    
    def set_privacy_preferences(self, preferences: Dict[str, Any]) -> None:
        """
        Update privacy preferences for Zcash operations.
        
        Args:
            preferences: Dictionary with privacy settings
        """
        return self.zec_agent.set_privacy_preferences(preferences)
    
    def deposit_near(self, amount: float) -> Dict:
        """
        Deposit NEAR for intent operations.
        
        Args:
            amount: Amount of NEAR to deposit
            
        Returns:
            Transaction result
        """
        return self.zec_agent.deposit_near(amount)


def create_zec_team(zec_agent: ZcashAgent) -> Team:
    """
    Create a team of specialized agents for Zcash operations.
    
    Args:
        zec_agent: The ZcashAgent instance for performing operations
        
    Returns:
        Team of Agno agents
    """
    # Create the ZEC Agno tool
    zec_tool = ZecAgnoTool(zec_agent)
    
    # Create the Portfolio Manager agent
    portfolio_manager = Agent(
        name="Portfolio Manager",
        role="Analyze and manage token portfolios",
        model=OpenAIChat(id="gpt-4o"),
        tools=[],
        instructions=dedent("""\
            You are an expert portfolio manager specializing in cryptocurrency portfolios.
            
            Your responsibilities include:
            1. Analyzing the current portfolio composition
            2. Recommending portfolio adjustments based on goals
            3. Monitoring token balances and distributions
            4. Calculating portfolio metrics (value, diversity, privacy ratio)
            5. Suggesting optimal entry and exit points for trades
            
            When analyzing portfolios, focus on:
            - Balance between privacy coins (ZEC) and other assets
            - Overall portfolio value and growth potential
            - Risk management and diversification
            - Privacy-preservation goals
            
            Always present your analysis with clear data points and visualizations when possible.
            Use tables and percentages to make information easy to understand.
        """),
        add_name_to_instructions=True,
        markdown=True,
    )
    
    # Create the Privacy Advisor agent
    privacy_advisor = Agent(
        name="Privacy Advisor",
        role="Recommend optimal privacy settings for transactions",
        model=OpenAIChat(id="gpt-4o"),
        tools=[],
        instructions=dedent("""\
            You are a privacy expert specializing in Zcash and shielded transactions.
            
            Your responsibilities include:
            1. Recommending appropriate privacy levels for transactions
            2. Explaining the implications of different privacy settings
            3. Advising on best practices for maintaining financial privacy
            4. Suggesting optimal configurations for shielded operations
            5. Highlighting potential privacy risks in transaction patterns
            
            When making recommendations, consider:
            - The type of transaction being performed
            - The sensitivity of the information involved
            - The user's privacy preferences and goals
            - The balance between privacy and convenience
            - Regulatory considerations and compliance requirements
            
            Always prioritize privacy while ensuring practical usability.
            Explain technical concepts in simple, accessible language.
        """),
        add_name_to_instructions=True,
        markdown=True,
    )
    
    # Create the Market Analyst agent
    market_analyst = Agent(
        name="Market Analyst",
        role="Provide market insights and pricing data",
        model=OpenAIChat(id="gpt-4o"),
        tools=[],
        instructions=dedent("""\
            You are a cryptocurrency market analyst specializing in ZEC and cross-chain markets.
            
            Your responsibilities include:
            1. Providing price analysis for ZEC and related tokens
            2. Identifying market trends and opportunities
            3. Monitoring liquidity across different exchanges
            4. Analyzing swap rates and spreads
            5. Predicting short and medium-term price movements
            
            When analyzing markets, focus on:
            - Current price levels and recent movements
            - Trading volume and liquidity indicators
            - Cross-chain price differences and arbitrage opportunities
            - Market sentiment and news impact
            - Technical indicators and chart patterns
            
            Present your analysis with charts, trends, and clear entry/exit suggestions.
            Include both bullish and bearish perspectives for balanced insights.
        """),
        add_name_to_instructions=True,
        markdown=True,
    )
    
    # Create the Transaction Coordinator agent
    transaction_coordinator = Agent(
        name="Transaction Coordinator",
        role="Orchestrate the overall transaction process",
        model=OpenAIChat(id="gpt-4o"),
        tools=[],
        instructions=dedent("""\
            You are an expert in cryptocurrency transactions, specializing in cross-chain operations.
            
            Your responsibilities include:
            1. Coordinating the end-to-end transaction process
            2. Ensuring optimal execution of swaps and transfers
            3. Monitoring transaction status and confirmations
            4. Troubleshooting issues and suggesting solutions
            5. Optimizing for cost, speed, and privacy
            
            When coordinating transactions, focus on:
            - Verifying all transaction parameters before execution
            - Securing the best possible rates through optimal routing
            - Balancing privacy requirements with execution efficiency
            - Ensuring proper error handling and recovery options
            - Providing clear status updates throughout the process
            
            Guide users through each step with clear instructions and confirmations.
            Always verify critical details before proceeding with high-value transactions.
        """),
        add_name_to_instructions=True,
        markdown=True,
    )
    
    # Create the team
    zec_team = Team(
        name="ZEC Intent Team",
        members=[portfolio_manager, privacy_advisor, market_analyst, transaction_coordinator],
        model=OpenAIChat(id="gpt-4o"),
        mode="coordinate",
        success_criteria=dedent("""\
            Successfully executed the user's request related to ZEC transactions, portfolio management, or privacy settings.
        """),
        instructions=dedent("""\
            You are the lead coordinator for a team of AI agents specializing in Zcash operations on NEAR.
            
            Your team includes:
            1. Portfolio Manager - Analyzes and manages token portfolios
            2. Privacy Advisor - Recommends optimal privacy settings
            3. Market Analyst - Provides market insights and pricing data
            4. Transaction Coordinator - Orchestrates the transaction process
            
            Your responsibilities:
            1. Route user requests to the appropriate specialist(s)
            2. Synthesize information from multiple team members
            3. Present a unified and coherent response to the user
            4. Ensure that all aspects of a request are addressed
            5. Coordinate complex operations involving multiple steps
            
            When responding to users:
            - Provide clear, actionable information
            - Include relevant data and visualizations when appropriate
            - Explain complex concepts in accessible language
            - Be transparent about limitations and risks
            - Prioritize both privacy and usability
            
            First understand what the user is trying to achieve, then coordinate your team members to fulfill that goal.
        """),
        add_datetime_to_instructions=True,
        show_tool_calls=True,
        markdown=True,
        enable_agentic_context=True,
        show_members_responses=True,
    )
    
    return zec_team


def process_user_request(zec_agent: ZcashAgent, user_request: str) -> str:
    """
    Process a user request through the ZEC team.
    
    Args:
        zec_agent: The ZcashAgent instance for performing operations
        user_request: The user's request or question
        
    Returns:
        The team's response to the user request
    """
    logging.info(f"Processing user request: {user_request}")
    
    # Create the ZEC team
    zec_team = create_zec_team(zec_agent)
    
    # Process the request
    response = zec_team.get_response(user_request)
    
    logging.info(f"Team response generated for request: {user_request}")
    return response


def main():
    """Example usage of the ZEC team."""
    # Path to account file (would be set by environment in production)
    account_path = os.getenv('NEAR_ACCOUNT_FILE', './account_file.json')
    
    try:
        # Initialize the ZEC agent
        zec_agent = ZcashAgent(account_path)
        
        # Example user requests
        example_requests = [
            "What's the current state of my portfolio?",
            "I want to swap 1 NEAR to ZEC with maximum privacy.",
            "What's the market outlook for ZEC today?",
            "How can I optimize my portfolio for both growth and privacy?",
        ]
        
        # Process each request
        for request in example_requests:
            print(f"\n\n=== User Request: {request} ===\n")
            response = process_user_request(zec_agent, request)
            print(response)
    
    except Exception as e:
        logging.error(f"Error in main: {e}")


if __name__ == "__main__":
    main() 