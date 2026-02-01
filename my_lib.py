from IPython.display import display
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime as dt

info = pd.read_parquet('Data/InstrumentsInfo.parquet.gzip')

def today():
    return dt.today().strftime("%Y-%m-%d")

def summarise(symbol: str, rates: pd.DataFrame):
    
    try:
        symbol_info = info[info['symbol'] == symbol].T
        currency = symbol_info.iloc[:, 0]['currency']
        display(symbol_info)
    except:
        currency = input(f'Nie znaleziono ETF o tickere {symbol} w wewnętrznej bazie. Podaj walutę ETFa {symbol}: ')
        
    x = f'{currency}PLN'

    eurpln = yf.Ticker(f"{x}=X").history(start='1900-01-01', end=today(), interval='1d').reset_index()
    eurpln['Date'] = eurpln['Date'].apply(lambda el: el.strftime('%Y-%m-%d'))
    eurpln.index = pd.DatetimeIndex(eurpln['Date'])
    eurpln = eurpln['Close']

    etf = yf.Ticker(symbol).history(start='1900-01-01', end=today(), interval='1d').reset_index()
    etf['Date'] = etf['Date'].apply(lambda el: el.strftime('%Y-%m-%d'))
    etf.index = pd.DatetimeIndex(etf['Date'])
    etf = etf[['Close', 'Dividends']]

    data = etf.merge(eurpln, how='outer', on='Date').rename(columns={'Close_x': symbol, 'Close_y': x})
    data[f'{symbol}_PLN'] = data[symbol]*data[x]
    data[f'Dividends_PLN'] = data['Dividends']*data[x]
    data['Dividends rate'] = data[f'Dividends_PLN']/data[f'{symbol}_PLN']

    display(data[data['Dividends'] > 0].tail(6))

    fig, ax = plt.subplots(2, figsize=(10, 12))

    ### ax[0]
    data[f'{symbol}_PLN'].plot(label=f'{symbol}, PLN', ax=ax[0])

    ax_right = ax[0].twinx()
    rates.loc[rates.index >= etf.index[0], :].plot(ax=ax_right, alpha=0.5)

    ax[0].grid(visible=True)
    ax[0].legend(loc=(0.005, 0.93))
    ax_right.legend(loc=(0.005, 0.73))

    ### ax[1]
    data[symbol].plot(label=f'{symbol}, {currency}', ax=ax[1])

    ax_right = ax[1].twinx()
    rates.loc[rates.index >= etf.index[0], :].plot(ax=ax_right, alpha=0.5)

    ax[1].grid(visible=True)
    ax[1].legend(loc=(0.005, 0.93))
    ax_right.legend(loc=(0.005, 0.73))

    plt.show()