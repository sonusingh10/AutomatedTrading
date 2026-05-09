import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import trading_strategy
from datetime import datetime, timedelta

def analyze_30d_anomalies():
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    tickers = ['NFLX', 'META', 'NVDA', 'AMD', 'TSLA']
    
    plt.figure(figsize=(14, 10))
    for i, ticker in enumerate(tickers):
        _, _, data, _, _ = trading_strategy.main(
            ticker=ticker, start_date=start_date, end_date=end_date,
            momentum_trade_threshold=0.01, momentum_priority_threshold=0.04
        )
        recent = data['strategy_returns'].tail(30).dropna()
        mean_ret, std_ret = recent.mean(), recent.std()
        z_scores = (recent - mean_ret) / std_ret
        outliers = recent[np.abs(z_scores) > 3]
        
        plt.subplot(len(tickers), 1, i+1)
        plt.plot(recent.index, recent.values, label=f'{ticker} Returns')
        plt.fill_between(recent.index, mean_ret - 2*std_ret, mean_ret + 2*std_ret, color='gray', alpha=0.2)
        if not outliers.empty:
            plt.scatter(outliers.index, outliers.values, color='red', zorder=5)
        plt.title(f'{ticker} Stability Analysis')
    plt.tight_layout()
    plt.savefig('return_stability_analysis.png')

if __name__ == '__main__':
    analyze_30d_anomalies()
