import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fetch_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    # Ensure we get a simple Series for Close even if yfinance returns a MultiIndex DataFrame
    if isinstance(data, pd.DataFrame) and isinstance(data.columns, pd.MultiIndex):
        data_close = data['Close'].iloc[:, 0]
    elif isinstance(data.get('Close'), pd.DataFrame):
        data_close = data['Close'].iloc[:, 0]
    else:
        data_close = data['Close']
    
    clean_df = pd.DataFrame({'Close': data_close.squeeze()})
    return clean_df.dropna()

def mean_reversion_strategy(data, window=20):
    close = data['Close']
    data['mean'] = close.rolling(window=window).mean()
    std_series = close.rolling(window=window).std()
    std_series_cleaned = std_series.replace(0, np.nan)
    data['z_score'] = (close - data['mean']) / std_series_cleaned
    data['position'] = np.where(data['z_score'] < -1, 1, np.where(data['z_score'] > 1, -1, 0))
    return data

def momentum_strategy(data, window=50, momentum_threshold=0.05):
    data['momentum'] = data['Close'].pct_change(periods=window)
    data['position'] = np.where(data['momentum'] > momentum_threshold, 1,
                                np.where(data['momentum'] < -momentum_threshold, -1, 0))
    return data

def combine_strategies(data, momentum_priority_threshold=0.04):
    data['combined_position'] = 0
    data.loc[data['momentum'] > momentum_priority_threshold, 'combined_position'] = 1
    data.loc[data['momentum'] < -momentum_priority_threshold, 'combined_position'] = -1
    no_strong_momentum_mask = (data['combined_position'] == 0)
    data.loc[no_strong_momentum_mask, 'combined_position'] = data.loc[no_strong_momentum_mask, 'position_mr']
    return data

def backtest_strategy(data):
    data['returns'] = data['Close'].pct_change()
    data['strategy_returns'] = data['returns'] * data['combined_position'].shift(1)
    data['cumulative_returns'] = (1 + data['strategy_returns'].fillna(0)).cumprod()
    daily_risk_free_rate = 0.00 / 252
    excess_returns = data['strategy_returns'] - daily_risk_free_rate
    excess_returns_cleaned = excess_returns.dropna()
    if not excess_returns_cleaned.empty and excess_returns_cleaned.std() != 0:
        sharpe_ratio = np.sqrt(252) * excess_returns_cleaned.mean() / excess_returns_cleaned.std()
    else:
        sharpe_ratio = np.nan
    return data, sharpe_ratio

def main(ticker='MSFT', start_date=None, end_date=None, momentum_window=50, momentum_trade_threshold=0.05, momentum_priority_threshold=0.04):
    if start_date is None:
        start_date = (pd.Timestamp.today() - pd.DateOffset(years=5)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

    data = fetch_stock_data(ticker, start_date, end_date)
    if data.empty:
        return np.nan, 10000, data, pd.Series(), 10000
        
    data = mean_reversion_strategy(data)
    data['position_mr'] = data['position'].copy()
    data = momentum_strategy(data, window=momentum_window, momentum_threshold=momentum_trade_threshold)
    data = combine_strategies(data, momentum_priority_threshold=momentum_priority_threshold)
    data, sharpe_ratio = backtest_strategy(data)

    initial_investment = 10000
    final_val = initial_investment * data['cumulative_returns'].iloc[-1] if not data.empty else initial_investment
    buy_and_hold_returns = (1 + data['Close'].pct_change().fillna(0)).cumprod()

    return sharpe_ratio, final_val, data, buy_and_hold_returns, initial_investment
