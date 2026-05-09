import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Fetch stock data
def fetch_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Mean-reversion strategy
def mean_reversion_strategy(data, window=20):
    data['mean'] = data['Close'].rolling(window=window).mean()

    # Explicitly ensure components are Series before arithmetic to prevent multi-column DataFrame error
    close_series = data['Close']
    if isinstance(close_series, pd.DataFrame):
        # If it's a DataFrame, take the first column and squeeze it to a Series
        close_series = close_series.iloc[:, 0].squeeze()

    mean_series = data['mean']
    if isinstance(mean_series, pd.DataFrame):
        # If it's a DataFrame, take the first column and squeeze it to a Series
        mean_series = mean_series.iloc[:, 0].squeeze()

    std_series = data['Close'].rolling(window=window).std()
    if isinstance(std_series, pd.DataFrame):
        # If it's a DataFrame, take the first column and squeeze it to a Series
        std_series = std_series.iloc[:, 0].squeeze()

    # Handle potential division by zero within the Series context
    std_series_cleaned = std_series.replace(0, np.nan)

    # Perform the calculation, which should now robustly yield a Series
    z_score_result_series = (close_series - mean_series) / std_series_cleaned

    # Explicitly ensure the final result is a Series before assignment
    if isinstance(z_score_result_series, pd.DataFrame):
        z_score_result_series = z_score_result_series.iloc[:, 0].squeeze()

    data['z_score'] = z_score_result_series

    # Set position based on z_score
    data['position'] = np.where(data['z_score'] < -1, 1, np.where(data['z_score'] > 1, -1, 0))
    return data

# Momentum strategy
def momentum_strategy(data, window=20):
    data['momentum'] = data['Close'].pct_change(periods=window)
    # Set position based on momentum
    data['position'] = np.where(data['momentum'] > 0, 1, -1)
    return data

# Combine strategies
def combine_strategies(data):
    # This function expects 'position_x' and 'position_y' to be present in the DataFrame
    data['combined_position'] = (data['position_x'] + data['position_y']) / 2
    data['combined_position'] = data['combined_position'].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return data

# Backtest the strategy
def backtest_strategy(data):
    data['returns'] = data['Close'].pct_change()
    # Ensure 'combined_position' is available and aligned
    data['strategy_returns'] = data['returns'] * data['combined_position'].shift(1)
    data['cumulative_returns'] = (1 + data['strategy_returns']).cumprod()

    # Calculate Sharpe Ratio
    # Assume a risk-free rate (e.g., 0 for simplicity, or 0.01 / 252 for daily data)
    daily_risk_free_rate = 0.00 / 252  # 0% annual risk-free rate
    excess_returns = data['strategy_returns'] - daily_risk_free_rate

    # Exclude NaN values from calculation
    excess_returns_cleaned = excess_returns.dropna()
    if not excess_returns_cleaned.empty:
        sharpe_ratio = np.sqrt(252) * excess_returns_cleaned.mean() / excess_returns_cleaned.std()
    else:
        sharpe_ratio = np.nan # Or handle as appropriate if no valid returns

    return data, sharpe_ratio

# Function to calculate Max Drawdown
def calculate_max_drawdown(cumulative_returns):
    if cumulative_returns.empty or cumulative_returns.isnull().all():
        return 0.0
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns - peak) / peak
    max_drawdown = drawdown.min()
    return max_drawdown

# Function to calculate Win Rate
def calculate_win_rate(strategy_returns):
    # A trade is considered a "win" if the return is positive
    winning_trades = strategy_returns[strategy_returns > 0].count()
    total_trades = strategy_returns.dropna().count()
    if total_trades == 0:
        return 0.0
    win_rate = winning_trades / total_trades
    return win_rate

# Main function
def main():
    ticker = 'AAPL'
    end_date = pd.Timestamp.today().strftime('%Y-%m-%d')
    start_date = (pd.Timestamp.today() - pd.DateOffset(years=5)).strftime('%Y-%m-%d')

    # Fetch data
    data = fetch_stock_data(ticker, start_date, end_date)

    # Apply strategies and store positions in separate columns
    data = mean_reversion_strategy(data)
    data['position_mr'] = data['position'].copy() # Store mean-reversion position

    data = momentum_strategy(data)
    data['position_mom'] = data['position'].copy() # Store momentum position

    # Assign to position_x and position_y for combine_strategies
    data['position_x'] = data['position_mr']
    data['position_y'] = data['position_mom']

    data = combine_strategies(data)

    # Backtest and get Sharpe Ratio
    data, sharpe_ratio = backtest_strategy(data)

    # Calculate profit and loss
    initial_investment = 10000
    # Handle cases where cumulative_returns might be empty or all NaN
    final_value = initial_investment * data['cumulative_returns'].iloc[-1] if not data['cumulative_returns'].empty and not data['cumulative_returns'].isnull().all() else initial_investment
    profit_loss = final_value - initial_investment

    # Calculate Buy and Hold returns for comparison
    buy_and_hold_returns = (1 + data['returns']).cumprod()
    buy_and_hold_final_value = initial_investment * buy_and_hold_returns.iloc[-1] if not buy_and_hold_returns.empty and not buy_and_hold_returns.isnull().all() else initial_investment
    buy_and_hold_profit_loss = buy_and_hold_final_value - initial_investment

    # Calculate Max Drawdown for both strategies
    strategy_max_drawdown = calculate_max_drawdown(data['cumulative_returns'])
    buy_and_hold_max_drawdown = calculate_max_drawdown(buy_and_hold_returns)

    # Calculate Win Rate for the strategy
    strategy_win_rate = calculate_win_rate(data['strategy_returns'])

    # Print results
    print(f"Investment Period: {start_date} to {end_date}")
    print(f"Initial Investment: ${initial_investment:.2f}")
    print(f"
Strategy Performance:")
    print(f"Final Value: ${final_value:.2f}")
    print(f"Profit/Loss: ${profit_loss:.2f}")
    print(f"Sharpe Ratio: {sharpe_ratio:.4f}")
    print(f"Maximum Drawdown: {strategy_max_drawdown:.4f}")
    print(f"Win Rate: {strategy_win_rate:.2%}")

    print(f"
Benchmark (Buy and Hold) Performance:")
    print(f"Final Value: ${buy_and_hold_final_value:.2f}")
    print(f"Profit/Loss: ${buy_and_hold_profit_loss:.2f}")
    print(f"Maximum Drawdown: {buy_and_hold_max_drawdown:.4f}")

    # Plot results
    plt.figure(figsize=(12, 6))
    plt.plot(data['cumulative_returns'], label='Strategy Returns')
    plt.plot(buy_and_hold_returns, label='Buy and Hold Returns')
    plt.legend()
    plt.title('Cumulative Returns: Strategy vs. Buy and Hold')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.grid(True)
    plt.savefig('cumulative_returns.png') # Save the plot to a file
    plt.show()

if __name__ == '__main__':
    main()