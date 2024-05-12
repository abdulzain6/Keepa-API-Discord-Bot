# Keepa API Discord Bot

This Discord bot integrates with the Keepa API to fetch and display detailed product information directly within Discord. The bot uses embeds to present data such as ASIN, seller details, brand, pricing, and more, making it a valuable tool for users interested in market research or e-commerce.

## Features

- **Product Information Embeds**: Displays comprehensive product details in a structured format on Discord.
- **Dynamic Links**: Includes clickable links to Amazon and Google for deeper product research.
- **API Integration**: Uses Keepa for real-time product data retrieval.

## Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Keepa API Access Key

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/Keepa-API-Discord-Bot.git
cd Keepa-API-Discord-Bot
```

2. **Install the required Python packages:**

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables in your system or define them in your deployment settings:

```plaintext
BOT_TOKEN=your_discord_bot_token_here
KEEPA_KEY=your_keepa_api_key_here
```

## Usage

To run the bot:

```bash
python main.py
```

Once running, the bot will listen for commands on Discord and respond with product information embeds based on Keepa API data.

## Contributing

Contributions to the bot are welcome! Please fork this repository, make your changes, and submit a pull request.