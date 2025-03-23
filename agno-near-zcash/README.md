# Zcash x NEAR Intents AI Agent

A multi-agent platform for privacy-focused crypto operations using Zcash, NEAR Intents, and Agno AI.

![Zcash x NEAR Intents](https://forum.zcashcommunity.com/uploads/default/original/3X/e/6/e646cb90bec8a45d86e74a9e0ec7860bb29c94e4.png)

## Overview

This project demonstrates an AI-powered trading bot that stores, manages, and transacts ZEC across blockchains using NEAR Intents and shielded transactions. It combines:

- **NEAR Intents Protocol**: For cross-chain token swaps and intent-driven transactions
- **Zcash Integration**: For privacy-preserving financial operations
- **Agno Multi-Agent Framework**: For intelligent collaboration between specialized AI agents

## Features

- 🛡️ **Privacy-Preserving Swaps**: Shielded ZEC transactions for maximum privacy
- 🔄 **Cross-Chain Operations**: Swap between NEAR, ZEC, and other tokens seamlessly
- 📊 **Portfolio Management**: AI-driven analysis and optimization of token holdings
- 🤖 **Specialized Agent Team**: Multiple agents collaborating to achieve user goals
- 🔐 **Privacy-First Design**: Built with privacy considerations at the core

## Architecture

### Components

1. **ZcashAgent** (`zec_agent.py`): Core agent that interfaces with NEAR Intents for ZEC operations
2. **Multi-Agent Team** (`agno_team.py`): Coordinates specialized agents for different functions:
   - Portfolio Manager: Analyzes and optimizes token holdings
   - Privacy Advisor: Recommends optimal privacy settings
   - Market Analyst: Provides market insights and pricing information
   - Transaction Coordinator: Orchestrates the end-to-end transaction process
3. **NEAR Intents with ZEC** (`near_zcash_intents.py`): Extended NEAR Intents functionality with Zcash support

### Flow Diagram

```
User Request → Agno Team → ZcashAgent → NEAR Intents → ZEC Operations
     ↑                                                     ↓
     └──────────────── Response/Analysis ─────────────────┘
```

## Getting Started

### Prerequisites

- Python 3.8+
- NEAR account with private key
- OpenAI API key for Agno agents

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agno-near-zcash.git
   cd agno-near-zcash
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your NEAR account file:
   ```bash
   cp account_file.example.json account_file.json
   # Edit account_file.json with your NEAR account details
   ```

4. Set your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```

### Usage

#### Basic Example

Run the basic example to see the system in action:

```bash
python examples/basic_example.py
```

This will:
1. Initialize the ZcashAgent
2. Retrieve and analyze your token portfolio
3. Demonstrate the multi-agent team's capabilities
4. Execute a sample NEAR to ZEC swap with privacy options (if sufficient balance)

#### Custom Usage

You can integrate the system into your own applications:

```python
from zec_agent import ZcashAgent
from agno_team import process_user_request

# Initialize the agent
zec_agent = ZcashAgent("./account_file.json")

# Get your portfolio
portfolio = zec_agent.get_portfolio()
print(portfolio)

# Process a natural language request through the AI team
response = process_user_request(zec_agent, "Swap 1 NEAR to ZEC with maximum privacy")
print(response)

# Directly execute a privacy-preserving swap
result = zec_agent.swap_to_zec("NEAR", 1.0, "shielded")
print(result)
```

## Privacy Considerations

This system is designed with privacy as a core focus:

- All ZEC operations can utilize Zcash's shielded transaction capabilities
- Privacy levels can be configured per transaction ("transparent" or "shielded")
- The Privacy Advisor agent helps users understand privacy implications
- Default settings prioritize privacy while maintaining usability

## Development

### Project Structure

```
agno-near-zcash/
├── src/
│   ├── near_zcash_intents.py  # Core NEAR-ZEC integration
│   ├── zec_agent.py           # Main Zcash agent
│   └── agno_team.py           # Multi-agent team setup
├── examples/
│   └── basic_example.py       # Usage example
└── README.md
```

### Extending the System

You can extend this system by:

1. Adding new agent types to the team in `agno_team.py`
2. Supporting additional tokens in `near_zcash_intents.py`
3. Enhancing privacy features in `zec_agent.py`
4. Creating new examples demonstrating specific use cases

## Hackathon Submission

This project was developed for the Zcash x NEAR Intents Hackathon, demonstrating how AI agents can interact with ZEC to create self-sovereign, private financial tools leveraging NEAR's Intents protocol.

## License

MIT

## Acknowledgments

- [NEAR Intents](https://docs.near-intents.org/) for the cross-chain transaction protocol
- [Zcash](https://z.cash/) for privacy-preserving blockchain technology
- [Agno](https://docs.agno.com/) for the multi-agent AI framework 