import ccxt
import pandas as pd
import mplfinance as mpf

# Seleziona gli exchange specificati
exchange_names = ['binance']#, 'coinbase', 'okx', 'bybit']# 'kraken', 'bitfinex', 'kucoin', 'bingx', 'huobi', 'upbit']

# Inizializza un dizionario per mantenere gli oggetti exchange
exchanges = {}

# Popola il dizionario con gli oggetti exchange
for exchange_name in exchange_names:
    exchange_class = getattr(ccxt, exchange_name)
    exchanges[exchange_name] = exchange_class()

# Definisci il mercato (ad esempio BTC/USDT)
symbol = 'BTC/USDT'


# Funzione per ottenere i dati OHLC da un exchange
def get_ohlcv(exchange, symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m')
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching OHLCV data from {exchange.id}: {e}")
        return None


# Funzione per ottenere il libro degli ordini da un exchange
def get_order_book(exchange, symbol):
    try:
        order_book = exchange.fetch_order_book(symbol)
        return order_book
    except Exception as e:
        print(f"Error fetching order book from {exchange.id}: {e}")
        return None


# Inizializza un DataFrame vuoto per i dati OHLC
ohlcv_data = pd.DataFrame()

# Inizializza liste per i prezzi bid e ask
all_bid_prices = []
all_ask_prices = []

# Ottieni i dati da ciascun exchange specificato
for exchange_name, exchange in exchanges.items():
    if exchange.has['fetchOHLCV'] and exchange.has['fetchOrderBook']:
        print(f"Fetching data from {exchange_name}")

        # Ottieni i dati OHLC
        df = get_ohlcv(exchange, symbol)
        if df is not None:
            ohlcv_data = ohlcv_data._append(df)

        # Ottieni il libro degli ordini
        order_book = get_order_book(exchange, symbol)
        if order_book is not None:
            bids = order_book['bids']
            asks = order_book['asks']
            bid_prices = [bid[0] for bid in bids]
            ask_prices = [ask[0] for ask in asks]
            all_bid_prices.extend(bid_prices)
            all_ask_prices.extend(ask_prices)

# Rimuovi duplicati e ordina i dati OHLC
ohlcv_data = ohlcv_data[~ohlcv_data.index.duplicated(keep='first')]
ohlcv_data.sort_index(inplace=True)

# Crea linee orizzontali per ordini bid e ask
hlines = all_bid_prices
#hlines_ = all_ask_prices

# Configura le linee orizzontali per mplfinance
hline_dict = dict(hlines=hlines, colors=['green'] * len(hlines), linewidths=0.03, linestyle='-.')
#hline_dict = dict(hlines=hlines_, colors=['red'] * len(hlines), linewidths=0.02, linestyle=':')
# Configura il grafico a candele con le linee orizzontali
mpf.plot(ohlcv_data, type='candle', style='charles', title=f'{symbol} Candlestick Chart (Aggregated)',
         ylabel='Price', volume=True, hlines=hline_dict)
