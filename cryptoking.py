from binance.client import Client
from binance.enums import *
import talib
import numpy as np

# Initialize Binance client
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Fetch available balance
balance = client.futures_account_balance()
usdt_balance = next(item for item in balance if item['asset'] == 'USDT')['balance']
print(f"Available balance: {usdt_balance} USDT")

# List of meme/new coins or all available coins
coins = ['DOGEUSDT', 'SANDUSDT', '1000SHIBUSDT', '1000FLOKIUSDT', '1MBABYDOGEUSDT']

# Define a function to get RSI and Moving Averages
def get_technical_indicators(symbol):
    # Get historical data for the coin (1h candles)
    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=100)
    close_prices = [float(kline[4]) for kline in klines]  # Close prices are at index 4

    # Calculate RSI
    rsi = talib.RSI(np.array(close_prices), timeperiod=14)[-1]

    # Calculate short and long MA
    short_ma = talib.SMA(np.array(close_prices), timeperiod=20)[-1]
    long_ma = talib.SMA(np.array(close_prices), timeperiod=50)[-1]

    return rsi, short_ma, long_ma

# Define a function to find the best coin based on RSI
def find_best_coin(coins):
    best_coin = None
    lowest_rsi = float('inf')

    for coin in coins:
        rsi, short_ma, long_ma = get_technical_indicators(coin)

        # Find coin with the lowest RSI (potential rebound)
        print(f"Analyzing {coin}:")
        print(f"RSI: {rsi}")
        print(f"Short MA: {short_ma}")
        print(f"Long MA: {long_ma}")

        if rsi < 30 and rsi < lowest_rsi:
            best_coin = coin
            lowest_rsi = rsi

    return best_coin

# Calculate the trade amount using 100x leverage
def calculate_trade_amount(symbol, balance, leverage=100):
    # For a 100x leverage, you need a tiny amount of USDT for a large position
    trade_amount = 5  # USDT to use for trade
    position_size = trade_amount * leverage
    return position_size

# Place an order on the best coin
def place_order(symbol, trade_amount):
    try:
        # Set leverage to 100x
        client.futures_change_leverage(symbol=symbol, leverage=100)
        
        # Calculate quantity for the market order (using available balance)
        ticker = client.futures_ticker(symbol=symbol)
        current_price = float(ticker['lastPrice'])

        # Calculate quantity (using available balance and trade amount)
        quantity = trade_amount / current_price

        # Place market buy order
        order = client.futures_create_order(
            symbol=symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )

        print(f"Market order placed for {symbol} with {trade_amount} USDT.")
        print(order)
    except Exception as e:
        print(f"Error placing order for {symbol}: {e}")

# Find the best coin based on RSI and technical analysis
best_coin = find_best_coin(coins)
if best_coin:
    print(f"Best coin for 100x trade: {best_coin}")
    trade_amount = calculate_trade_amount(best_coin, usdt_balance)
    place_order(best_coin, trade_amount)
else:
    print("No suitable coin found based on RSI and technical indicators.")
