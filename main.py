import ccxt
import pandas as pd
import mplfinance as mpf

# Seleziona l'exchange (ad esempio Binance)
exchange = ccxt.binance()

# Definisci il mercato (ad esempio BTC/USDT)
symbol = 'BTC/USDT'

# Ottieni i dati OHLC (Open, High, Low, Close) del mercato
ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h')  # Puoi cambiare il timeframe

# Crea un DataFrame da pandas
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Ottieni il libro degli ordini
order_book = exchange.fetch_order_book(symbol)
bids = order_book['bids']
#asks = order_book['asks']

# Separare i prezzi per bid e ask
bid_prices = [bid[0] for bid in bids]
#ask_prices = [ask[0] for ask in asks]

# Crea linee orizzontali per ordini bid e ask
hlines = bid_prices #+ #ask_prices

# Configura le linee orizzontali per mplfinance
hline_dict = dict(hlines=hlines, colors=['green']*len(hlines), linewidths=0.5, linestyle='-')

# Configura il grafico a candele con le linee orizzontali
mpf.plot(df, type='candle', style='charles', title=f'{symbol} Candlestick Chart',
         ylabel='Price', volume=True, hlines=hline_dict)

