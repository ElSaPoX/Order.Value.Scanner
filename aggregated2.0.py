import ccxt
import pandas as pd
import mplfinance as mpf

# Seleziona gli exchange specificati
exchange_names = ['binance', 'coinbase', 'bybit', 'bitfinex'] #, 'kraken']# 'okx', 'bybit', 'kraken', 'bitfinex', 'kucoin', 'bingx', 'huobi', 'upbit']

# Inizializza un dizionario per mantenere gli oggetti exchange
exchanges = {}

# Popola il dizionario con gli oggetti exchange
for exchange_name in exchange_names:
    exchange_class = getattr(ccxt, exchange_name)
    exchanges[exchange_name] = exchange_class()

# Definisci il mercato (ad esempio BTC/USDT)
symbol = 'BTC/USDT'
order_value_threshold = 100000  # soglia di valore dell'ordine


# Funzione per ottenere i dati OHLC da un exchange
def get_ohlcv(exchange, symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='4h')
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

        if exchange_name == 'binance':
            # Ottieni i dati OHLC
            df = get_ohlcv(exchange, symbol)
            if df is not None:
                ohlcv_data = ohlcv_data._append(df)

        # Ottieni il libro degli ordini
        order_book = get_order_book(exchange, symbol)
        if order_book is not None:
            bids = order_book['bids']
            asks = order_book['asks']

            # Filtra ordini bid
            for bid in bids:
                bid_price, bid_amount = bid[:2]  # Prendi solo prezzo e quantità
                if bid_price * bid_amount >= order_value_threshold:
                    all_bid_prices.append(bid_price)

            # Filtra ordini ask
            for ask in asks:
                ask_price, ask_amount = ask[:2]  # Prendi solo prezzo e quantità
                if ask_price * ask_amount >= order_value_threshold:
                    all_ask_prices.append(ask_price)

# Rimuovi duplicati e ordina i dati OHLC
ohlcv_data = ohlcv_data[~ohlcv_data.index.duplicated(keep='first')]
ohlcv_data.sort_index(inplace=True)

# Crea linee orizzontali per ordini bid e ask
hlines = all_bid_prices + all_ask_prices

# Configura le linee orizzontali per mplfinance con diversi stili di linea
hline_styles = ['-', '--', '-.', ':']
hline_colors = ['green', 'red', 'blue', 'orange']

hlineask_dict = dict(hlines=all_ask_prices, colors=hline_colors * (len(hlines) // len(hline_colors) + 1),
                  linewidths=0.5, linestyle=hline_styles * (len(hlines) // len(hline_styles) + 1))
hlinebid_dict = dict(hlines=all_bid_prices, colors=hline_colors * (len(hlines) // len(hline_colors) + 1),
                  linewidths=0.5, linestyle=hline_styles * (len(hlines) // len(hline_styles) + 1))
# Crea addplot per oggetto1
addplot1 = [mpf.make_addplot([level] * len(ohlcv_data), color='red', linestyle='-') for level in all_ask_prices]

# Crea addplot per oggetto2
addplot2 = [mpf.make_addplot([level] * len(ohlcv_data), color='green', linestyle='-') for level in all_bid_prices]

# Combina gli addplot
addplots = addplot1 + addplot2

print(len(all_bid_prices), len(all_ask_prices))


#Configura il grafico a candele con le linee orizzontali
mpf.plot(ohlcv_data, type='candle', style='charles', title=f'{symbol} Candlestick Chart (Aggregated)',
         ylabel='Price', volume=True, addplot= addplots)




