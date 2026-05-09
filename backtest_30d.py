import trading_strategy
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def run_30_day_analysis():
    portfolio_configs = [
        {'ticker': 'NFLX', 'trade_t': 0.005, 'priority_t': 0.02},
        {'ticker': 'META', 'trade_t': 0.010, 'priority_t': 0.06},
        {'ticker': 'NVDA', 'trade_t': 0.010, 'priority_t': 0.02},
        {'ticker': 'AMD',  'trade_t': 0.010, 'priority_t': 0.02},
        {'ticker': 'TSLA', 'trade_t': 0.010, 'priority_t': 0.04}
    ]
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    all_cumulative_returns = {}
    
    for config in portfolio_configs:
        print(f'Backtesting {config["ticker"]}...') 
        _, _, data, _, _ = trading_strategy.main(
            ticker=config['ticker'],
            start_date=start_date,
            end_date=end_date,
            momentum_trade_threshold=config['trade_t'],
            momentum_priority_threshold=config['priority_t']
        )
        recent = data.tail(30).copy()
        recent['cumulative'] = (1 + recent['strategy_returns'].fillna(0)).cumprod()
        all_cumulative_returns[config['ticker']] = recent['cumulative']

    plt.figure(figsize=(14, 7))
    for ticker, series in all_cumulative_returns.items():
        plt.plot(series.index, series.values, label=ticker)
    plt.title('30-Day Strategy Performance')
    plt.legend()
    plt.savefig('recent_30d_performance.png')
    print('Analysis complete. Plot saved as recent_30d_performance.png')

if __name__ == '__main__':
    run_30_day_analysis()
