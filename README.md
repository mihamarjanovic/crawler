# Ethereum Transactions Crawler

This application fetches and displays Ethereum transaction data (ETH and ERC-20 tokens) for a given wallet address starting from a specified block using the Etherscan API. It also calculates the ETH balance at a specific date (YYYY-MM-DD).

## Features
- Fetches ETH transactions (from, to, amount, gas cost, timestamp, block number).
- Fetches ERC-20 token transactions (from, to, amount, token symbol).
- Calculates ETH balance at a given date (bonus feature).
- Displays results in a web interface using Flask.

## Requirements
- Python 3.8+
- Dependencies: `requests`, `flask`

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd ethereum-crawler