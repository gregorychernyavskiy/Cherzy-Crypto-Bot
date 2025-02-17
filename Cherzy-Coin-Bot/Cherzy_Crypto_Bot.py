import time
import asyncio
import logging
from aiohttp import ClientSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import google.generativeai as genai
import telegram
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Configure Gemini
genai.configure(api_key="")

# Telegram bot configuration
chat_id = 
bot_token = ''
bot = telegram.Bot(token=bot_token)

# Cryptocurrency symbols
symbols = {
    'Bitcoin': 'BTCUSDT_UMCBL',
    'Ethereum': 'ETHUSDT_UMCBL',
    'BNB': 'BNBUSDT_UMCBL',
    'Solana': 'SOLUSDT_UMCBL',
    'Toncoin': 'TONUSDT_UMCBL',
    'XRP': 'XRPUSDT_UMCBL',
    'USD Coin': 'USDCUSDT_UMCBL',
    'Cardano': 'ADAUSDT_UMCBL',
    'Dogecoin': 'DOGEUSDT_UMCBL',
    'Shiba Inu': 'SHIBUSDT_UMCBL',
    'PAX Gold': 'PAXGUSDT_UMCBL',
    'Maker': 'MKRUSDT_UMCBL',
    'Bitcoin Cash': 'BCHUSDT_UMCBL',
    'Litecoin': 'LTCUSDT_UMCBL',
    'Compound': 'COMPUSDT_UMCBL',
    'Avalanche': 'AVAXUSDT_UMCBL',
    'Ethereum Classic': 'ETCUSDT_UMCBL',
    'Chainlink': 'LINKUSDT_UMCBL',
    'Arweave': 'ARUSDT_UMCBL',
    'Neo': 'NEOUSDT_UMCBL',
    'Uniswap': 'UNIUSDT_UMCBL',
    'Aptos': 'APTUSDT_UMCBL',
    'Polkadot': 'DOTUSDT_UMCBL',
    'Cosmos': 'ATOMUSDT_UMCBL',
    'Filecoin': 'FILUSDT_UMCBL',
    'Sui': 'SUIUSDT_UMCBL',
    'THORChain': 'RUNEUSDT_UMCBL',
    'Immutable': 'IMXUSDT_UMCBL',
    'Tezos': 'XTZUSDT_UMCBL',
    'ApeCoin': 'APEUSDT_UMCBL',
    'PancakeSwap': 'CAKEUSDT_UMCBL',
    'Lido DAO': 'LDOUSDT_UMCBL',
    'Optimism': 'OPUSDT_UMCBL',
    'Core': 'COREUSDT_UMCBL',
    'Safe': 'SAFEUSDT_UMCBL',
    'Internet Computer': 'ICPUSDT_UMCBL',
    'Axie Infinity': 'AXSUSDT_UMCBL',
    'Helium': 'HNTUSDT_UMCBL',
    'Bitget Token': 'BGBUSDT_UMCBL',
    'NEAR Protocol': 'NEARUSDT_UMCBL',
    'LayerZero': 'ZROUSDT_UMCBL',
    'Pendle': 'PENDLEUSDT_UMCBL',
    'Convex Finance': 'CVXUSDT_UMCBL',
    'EigenLayer': 'EIGENUSDT_UMCBL',
    'Arkham': 'ARKMUSDT_UMCBL',
    'dYdX': 'DYDXUSDT_UMCBL',
    'Stellar': 'XLMUSDT_UMCBL',
    'Artificial Intelligence': 'AIUSDT_UMCBL'
}

# Persistent menu for better user experience
persistent_menu = ReplyKeyboardMarkup(
    [
        ["Get Prices", "Get Recommendations"]  # Buttons in a row
    ],
    resize_keyboard=True,  # Adjust button size
    one_time_keyboard=False  # Keep buttons persistent
)

# Add inline buttons for specific interactions
keyboard = [
    [InlineKeyboardButton("Get Prices for Crypto", callback_data='prices')],
    [InlineKeyboardButton("Get Recommendations", callback_data='recommend')]
]
reply_markup = InlineKeyboardMarkup(keyboard)

# Function to fetch historical price data using CoinGecko with retries
async def fetch_with_retries(session, url, params, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                logger.warning(f"Attempt {attempt + 1}: Failed with status {response.status}")
        except Exception as e:
            logger.error(f"Error during API call: {e}")
        await asyncio.sleep(1)  # Wait before retrying
    return {}

# Function to fetch historical price data using CoinGecko with enhanced error handling
async def fetch_price_history(symbol, intervals=["7d", "1d", "1h"]):
    """
    Fetch historical price data for a cryptocurrency symbol using CoinGecko.
    """
    symbol_mapping = {
    "BTCUSDT_UMCBL": "bitcoin",
    "BTCUSDT": "bitcoin",
    "ETHUSDT_UMCBL": "ethereum",
    "ETHUSDT": "ethereum",
    "BNBUSDT_UMCBL": "binancecoin",
    "BNBUSDT": "binancecoin",
    "SOLUSDT_UMCBL": "solana",
    "SOLUSDT": "solana",
    "TONUSDT_UMCBL": "toncoin",
    "TONUSDT": "toncoin",
    "XRPUSDT_UMCBL": "ripple",
    "XRPUSDT": "ripple",
    "USDCUSDT_UMCBL": "usd-coin",
    "USDCUSDT": "usd-coin",
    "ADAUSDT_UMCBL": "cardano",
    "ADAUSDT": "cardano",
    "DOGEUSDT_UMCBL": "dogecoin",
    "DOGEUSDT": "dogecoin",
    "SHIBUSDT_UMCBL": "shiba-inu",
    "SHIBUSDT": "shiba-inu",
    "PAXGUSDT_UMCBL": "pax-gold",
    "PAXGUSDT": "pax-gold",
    "MKRUSDT_UMCBL": "maker",
    "MKRUSDT": "maker",
    "BCHUSDT_UMCBL": "bitcoin-cash",
    "BCHUSDT": "bitcoin-cash",
    "LTCUSDT_UMCBL": "litecoin",
    "LTCUSDT": "litecoin",
    "COMPUSDT_UMCBL": "compound",
    "COMPUSDT": "compound",
    "AVAXUSDT_UMCBL": "avalanche",
    "AVAXUSDT": "avalanche",
    "ETCUSDT_UMCBL": "ethereum-classic",
    "ETCUSDT": "ethereum-classic",
    "LINKUSDT_UMCBL": "chainlink",
    "LINKUSDT": "chainlink",
    "ARUSDT_UMCBL": "arweave",
    "ARUSDT": "arweave",
    "NEOUSDT_UMCBL": "neo",
    "NEOUSDT": "neo",
    "UNIUSDT_UMCBL": "uniswap",
    "UNIUSDT": "uniswap",
    "APTUSDT_UMCBL": "aptos",
    "APTUSDT": "aptos",
    "DOTUSDT_UMCBL": "polkadot",
    "DOTUSDT": "polkadot",
    "ATOMUSDT_UMCBL": "cosmos",
    "ATOMUSDT": "cosmos",
    "FILUSDT_UMCBL": "filecoin",
    "FILUSDT": "filecoin",
    "SUIUSDT_UMCBL": "sui",
    "SUIUSDT": "sui",
    "RUNEUSDT_UMCBL": "thorchain",
    "RUNEUSDT": "thorchain",
    "IMXUSDT_UMCBL": "immutable",
    "IMXUSDT": "immutable",
    "XTZUSDT_UMCBL": "tezos",
    "XTZUSDT": "tezos",
    "APEUSDT_UMCBL": "apecoin",
    "APEUSDT": "apecoin",
    "CAKEUSDT_UMCBL": "pancakeswap",
    "CAKEUSDT": "pancakeswap",
    "LDOUSDT_UMCBL": "lido-dao",
    "LDOUSDT": "lido-dao",
    "OPUSDT_UMCBL": "optimism",
    "OPUSDT": "optimism",
    "COREUSDT_UMCBL": "core",
    "COREUSDT": "core",
    "SAFEUSDT_UMCBL": "safe",
    "SAFEUSDT": "safe",
    "ICPUSDT_UMCBL": "internet-computer",
    "ICPUSDT": "internet-computer",
    "AXSUSDT_UMCBL": "axie-infinity",
    "AXSUSDT": "axie-infinity",
    "HNTUSDT_UMCBL": "helium",
    "HNTUSDT": "helium",
    "BGBUSDT_UMCBL": "bitget-token",
    "BGBUSDT": "bitget-token",
    "NEARUSDT_UMCBL": "near-protocol",
    "NEARUSDT": "near-protocol",
    "ZROUSDT_UMCBL": "layerzero",
    "ZROUSDT": "layerzero",
    "PENDLEUSDT_UMCBL": "pendle",
    "PENDLEUSDT": "pendle",
    "CVXUSDT_UMCBL": "convex-finance",
    "CVXUSDT": "convex-finance",
    "EIGENUSDT_UMCBL": "eigenlayer",
    "EIGENUSDT": "eigenlayer",
    "ARKMUSDT_UMCBL": "arkham",
    "ARKMUSDT": "arkham",
    "DYDXUSDT_UMCBL": "dydx",
    "DYDXUSDT": "dydx",
    "XLMUSDT_UMCBL": "stellar",
    "XLMUSDT": "stellar",
    "AIUSDT_UMCBL": "artificial-intelligence",
    "AIUSDT": "artificial-intelligence"
    }


    if symbol not in symbol_mapping:
        logger.error(f"Symbol {symbol} not found in mapping.")
        return {"error": f"Symbol {symbol} not found in mapping."}

    coin_id = symbol_mapping[symbol]
    base_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "7"}

    try:
        async with ClientSession() as session:
            data = await fetch_with_retries(session, base_url, params)
            if not data:
                logger.error(f"No response or data returned for {coin_id}.")
                return {"error": f"No data returned for {coin_id}."}

            if "prices" not in data or not data["prices"]:
                logger.error(f"No price data found for {coin_id}. Response: {data}")
                return {"error": f"No price data found for {coin_id}."}

            # Extract historical prices
            prices = data["prices"]
            current_price = prices[-1][1]

            # Extract historical prices based on intervals
            one_hour_ago_price = next(
                (price[1] for price in reversed(prices) if time.time() - price[0] / 1000 >= 3600), None
            )
            one_day_ago_price = next(
                (price[1] for price in reversed(prices) if time.time() - price[0] / 1000 >= 86400), None
            )
            one_week_ago_price = prices[0][1] if len(prices) > 0 else None

            return {
                "7d": one_week_ago_price,
                "1d": one_day_ago_price,
                "1h": one_hour_ago_price,
                "current": current_price
            }
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        return {"error": f"Exception occurred: {e}"}

# Function to calculate recommendations based on price history
async def calculate_recommendation(symbol):
    data = await fetch_price_history(symbol)
    if "error" in data:
        return f"Error: {data['error']}"

    if not data or not data.get("current"):
        return f"No historical data available for {symbol}."

    current_price = data["current"]
    recommendations = []

    for interval in ["7d", "1d", "1h"]:
        old_price = data.get(interval)
        if not old_price:
            recommendations.append(f"No {interval} data available.")
            continue

        percentage_change = ((current_price - old_price) / old_price) * 100
        if percentage_change < -10:
            recommendations.append(f"{interval}: Buy! Price dropped by {percentage_change:.2f}%.")
        elif percentage_change > 10:
            recommendations.append(f"{interval}: Hold! Price increased by {percentage_change:.2f}%.")
        else:
            recommendations.append(f"{interval}: Neutral ({percentage_change:.2f}%).")

    return "\n".join(recommendations)

async def handle_text_commands(update, context):
    text = update.message.text
    if text == "Get Recommendations":
        await show_coin_list(update, context)
    elif text == "Get Prices":
        await handle_prices(update, context)
    else:
        await update.message.reply_text("I didn't understand that. Please use the buttons.")

async def fetch_prices():
    async with ClientSession() as session:
        results = {}
        for name, symbol in symbols.items():
            price = await fetch_price(session, symbol)
            results[name] = price
        return results

async def fetch_price(session, symbol):
    url = f'https://capi.bitget.com/api/mix/v1/market/ticker?symbol={symbol}'
    try:
        async with session.get(url) as response:
            if response.status != 200:
                return f"Error {response.status}: Failed to fetch {symbol}"
            data = await response.json()
            if 'data' in data and 'last' in data['data']:
                return float(data['data']['last'])
            return f"No data for {symbol}"
    except Exception as e:
        return f"Exception: {str(e)}"

async def show_coin_list(update, context):
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"recommend_{symbol}")]
        for name, symbol in symbols.items()
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Choose a coin to get a recommendation:", reply_markup=reply_markup
    )

async def handle_specific_recommendation(update, context):
    query = update.callback_query.data
    symbol = query.split("_")[1]  # Extract the symbol from callback data

    recommendation = await calculate_recommendation(symbol)
    vitality = await fetch_vitality_metrics(symbol)

    if "error" in vitality:
        vitality_info = vitality["error"]
    else:
        vitality_info = (
            f"Market Cap: ${vitality['market_cap']:,.2f}\n"
            f"24h Volume: ${vitality['volume_24h']:,.2f}\n"
            f"Circulating Supply: {vitality['circulating_supply']:,.2f}"
        )

    await update.callback_query.message.reply_text(
        f"{symbol} Recommendations:\n{recommendation}\n\nVitality Metrics:\n{vitality_info}"
    )

async def handle_prices(update, context):
    logger.info("Button clicked: Fetching prices...")
    prices = await fetch_prices()
    message = "\n".join(
        f"{name}: ${price:,.2f}" if isinstance(price, float) else f"{name}: {price}"
        for name, price in prices.items()
    )
    await update.message.reply_text(f"Current Prices:\n{message}")

async def start(update, context):
    await update.message.reply_text(
        "Welcome to Cherzy Crypto Bot! Use the buttons below to interact.",
        reply_markup=persistent_menu  # Attach the persistent menu
    )

async def fetch_vitality_metrics(symbol):
    """
    Fetch trading volume, market cap, and other vitality metrics for a cryptocurrency symbol.
    """
    symbol_mapping = {
    "BTCUSDT_UMCBL": "bitcoin",
    "BTCUSDT": "bitcoin",
    "ETHUSDT_UMCBL": "ethereum",
    "ETHUSDT": "ethereum",
    "BNBUSDT_UMCBL": "binancecoin",
    "BNBUSDT": "binancecoin",
    "SOLUSDT_UMCBL": "solana",
    "SOLUSDT": "solana",
    "TONUSDT_UMCBL": "toncoin",
    "TONUSDT": "toncoin",
    "XRPUSDT_UMCBL": "ripple",
    "XRPUSDT": "ripple",
    "USDCUSDT_UMCBL": "usd-coin",
    "USDCUSDT": "usd-coin",
    "ADAUSDT_UMCBL": "cardano",
    "ADAUSDT": "cardano",
    "DOGEUSDT_UMCBL": "dogecoin",
    "DOGEUSDT": "dogecoin",
    "SHIBUSDT_UMCBL": "shiba-inu",
    "SHIBUSDT": "shiba-inu",
    "PAXGUSDT_UMCBL": "pax-gold",
    "PAXGUSDT": "pax-gold",
    "MKRUSDT_UMCBL": "maker",
    "MKRUSDT": "maker",
    "BCHUSDT_UMCBL": "bitcoin-cash",
    "BCHUSDT": "bitcoin-cash",
    "LTCUSDT_UMCBL": "litecoin",
    "LTCUSDT": "litecoin",
    "COMPUSDT_UMCBL": "compound",
    "COMPUSDT": "compound",
    "AVAXUSDT_UMCBL": "avalanche",
    "AVAXUSDT": "avalanche",
    "ETCUSDT_UMCBL": "ethereum-classic",
    "ETCUSDT": "ethereum-classic",
    "LINKUSDT_UMCBL": "chainlink",
    "LINKUSDT": "chainlink",
    "ARUSDT_UMCBL": "arweave",
    "ARUSDT": "arweave",
    "NEOUSDT_UMCBL": "neo",
    "NEOUSDT": "neo",
    "UNIUSDT_UMCBL": "uniswap",
    "UNIUSDT": "uniswap",
    "APTUSDT_UMCBL": "aptos",
    "APTUSDT": "aptos",
    "DOTUSDT_UMCBL": "polkadot",
    "DOTUSDT": "polkadot",
    "ATOMUSDT_UMCBL": "cosmos",
    "ATOMUSDT": "cosmos",
    "FILUSDT_UMCBL": "filecoin",
    "FILUSDT": "filecoin",
    "SUIUSDT_UMCBL": "sui",
    "SUIUSDT": "sui",
    "RUNEUSDT_UMCBL": "thorchain",
    "RUNEUSDT": "thorchain",
    "IMXUSDT_UMCBL": "immutable",
    "IMXUSDT": "immutable",
    "XTZUSDT_UMCBL": "tezos",
    "XTZUSDT": "tezos",
    "APEUSDT_UMCBL": "apecoin",
    "APEUSDT": "apecoin",
    "CAKEUSDT_UMCBL": "pancakeswap",
    "CAKEUSDT": "pancakeswap",
    "LDOUSDT_UMCBL": "lido-dao",
    "LDOUSDT": "lido-dao",
    "OPUSDT_UMCBL": "optimism",
    "OPUSDT": "optimism",
    "COREUSDT_UMCBL": "core",
    "COREUSDT": "core",
    "SAFEUSDT_UMCBL": "safe",
    "SAFEUSDT": "safe",
    "ICPUSDT_UMCBL": "internet-computer",
    "ICPUSDT": "internet-computer",
    "AXSUSDT_UMCBL": "axie-infinity",
    "AXSUSDT": "axie-infinity",
    "HNTUSDT_UMCBL": "helium",
    "HNTUSDT": "helium",
    "BGBUSDT_UMCBL": "bitget-token",
    "BGBUSDT": "bitget-token",
    "NEARUSDT_UMCBL": "near-protocol",
    "NEARUSDT": "near-protocol",
    "ZROUSDT_UMCBL": "layerzero",
    "ZROUSDT": "layerzero",
    "PENDLEUSDT_UMCBL": "pendle",
    "PENDLEUSDT": "pendle",
    "CVXUSDT_UMCBL": "convex-finance",
    "CVXUSDT": "convex-finance",
    "EIGENUSDT_UMCBL": "eigenlayer",
    "EIGENUSDT": "eigenlayer",
    "ARKMUSDT_UMCBL": "arkham",
    "ARKMUSDT": "arkham",
    "DYDXUSDT_UMCBL": "dydx",
    "DYDXUSDT": "dydx",
    "XLMUSDT_UMCBL": "stellar",
    "XLMUSDT": "stellar",
    "AIUSDT_UMCBL": "artificial-intelligence",
    "AIUSDT": "artificial-intelligence"
    }

    if symbol not in symbol_mapping:
        return {"error": f"Symbol {symbol} not found in mapping."}
    coin_id = symbol_mapping[symbol]
    base_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

    try:
        async with ClientSession() as session:
            async with session.get(base_url) as response:
                if response.status != 200:
                    return {"error": f"Failed to fetch data for {coin_id}, status: {response.status}"}

                data = await response.json()

                # Extract relevant metrics
                market_cap = data["market_data"]["market_cap"]["usd"]
                volume_24h = data["market_data"]["total_volume"]["usd"]
                circulating_supply = data["market_data"]["circulating_supply"]

                return {
                    "market_cap": market_cap,
                    "volume_24h": volume_24h,
                    "circulating_supply": circulating_supply
                }
    except Exception as e:
        return {"error": f"Exception occurred: {e}"}

def setup_bot():
    try:
        application = Application.builder().token(bot_token).build()
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        # Text handlers for persistent menu commands
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_commands))
        # Button/Callback handlers
        application.add_handler(CallbackQueryHandler(handle_specific_recommendation))

        # Start the bot
        logger.info("Starting the bot...")
        application.run_polling()
        logger.info("Bot has stopped.")  # Log after the bot stops
    except Exception as e:
        logger.error(f"An error occurred: {e}")

# Function to dynamically fetch Binance symbols
def fetch_binance_symbols():
    """
    Fetch cryptocurrency symbols from Binance's API and map them to their base asset names.
    """
    try:
        response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
        response.raise_for_status()
        symbols_data = response.json().get('symbols', [])
        # Create a mapping of symbols to their base asset names
        return {symbol['symbol']: symbol['baseAsset'].lower() for symbol in symbols_data}
    except Exception as e:
        logger.error(f"Error fetching Binance symbols: {e}")
        return {}

# Example integration in the bot's main loop
if __name__ == '__main__':
    # Fetch symbols at startup
    binance_symbols = fetch_binance_symbols()

    if not binance_symbols:
        logger.error("Failed to fetch Binance symbols. Check the API connection.")

    try:
        setup_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")
