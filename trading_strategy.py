import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fetch_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    # Squeeze if columns are MultiIndex or single column DF
    if isinstance(data['Close'], pd.DataFrame):
        data['Close'] = data['Close'].iloc[:, 0]
    return data

def mean_reversion_strategy(data, window=20):
    # Ensure we use Series for calculations
    close = data['Close'].squeeze()
    data['mean'] = close.rolling(window=window).mean()
    std_series = close.rolling(window=window).std().replace(0, np.nan)
    
    # Explicitly calculate and squeeze the result
    z_score = (close - data['mean'].squeeze()) / std_series.squeeze()
    data['z_score'] = z_score
    
    data['position'] = np.where(data['z_score'] < -1, 1, np.where(data['z_score'] > 1, -1, 0))
    return data

def momentum_strategy(data, window=50, momentum_threshold=0.05):
    close = data['Close'].squeeze()
    data['momentum'] = close.pct_change(periods=window)
    data['position'] = np.where(data['momentum'] > momentum_threshold, 1, np.where(data['momentum'] < -momentum_threshold, -1, 0))
    return data

def combine_strategies(data, momentum_priority_threshold=0.04):
    data['combined_position'] = 0
    data.loc[data['momentum'] > momentum_priority_threshold, 'combined_position'] = 1
    data.loc[data['momentum'] < -momentum_priority_threshold, 'combined_position'] = -1
    mask = (data['combined_position'] == 0)
    data.loc[mask, 'combined_position'] = data.loc[mask, 'position_mr']
    return data

def calculate_max_drawdown(cumulative_returns):
    if cumulative_returns.empty or cumulative_returns.isnull().all(): return 0.0
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns - peak) / peak
    return drawdown.min()

def calculate_win_rate(strategy_returns):
    wins = strategy_returns[strategy_returns > 0].count()
    total = strategy_returns.dropna().count()
    return wins / total if total > 0 else 0.0

def backtest_strategy(data):
    returns = data['Close'].squeeze().pct_change()
    data['strategy_returns'] = returns * data['combined_position'].shift(1)
    data['cumulative_returns'] = (1 + data['strategy_returns'].fillna(0)).cumprod()
    excess = data['strategy_returns']
    sharpe = np.sqrt(252) * excess.mean() / excess.std() if excess.std() != 0 else np.nan
    return data, sharpe

def main(ticker='MSFT', start_date=None, end_date=None, momentum_trade_threshold=0.05, momentum_priority_threshold=0.04):
    if start_date is None: start_date = (pd.Timestamp.today() - pd.DateOffset(years=5)).strftime('%Y-%m-%d')
    if end_date is None: end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    data = fetch_stock_data(ticker, start_date, end_date)
    data = mean_reversion_strategy(data)
    data['position_mr'] = data['position'].copy()
    data = momentum_strategy(data, momentum_threshold=momentum_trade_threshold)
    data = combine_strategies(data, momentum_priority_threshold=momentum_priority_threshold)
    data, sharpe = backtest_strategy(data)
    initial_inv = 10000
    final_val = initial_inv * data['cumulative_returns'].iloc[-1]
    bnh = (1 + data['Close'].squeeze().pct_change().fillna(0)).cumprod()
    return sharpe, final_val, data, bnh, initial_inv
