import trading_strategy
import pandas as pd
import matplotlib.pyplot as plt

def run_volatile_portfolio_analysis():
    # Optimal parameters found via grid search
    portfolio_params = [
        {'ticker': 'NVDA', 'trade_t': 0.01, 'priority_t': 0.02},
        {'ticker': 'TSLA', 'trade_t': 0.01, 'priority_t': 0.04},
        {'ticker': 'AMD',  'trade_t': 0.01, 'priority_t': 0.02},
        {'ticker': 'META', 'trade_t': 0.01, 'priority_t': 0.06}
    ]
    
    results = []
    for p in portfolio_params:
        print(f'Running analysis for {p["ticker"]}...')
        sharpe, final_val, data, bnh, init = trading_strategy.main(
            ticker=p['ticker'],
            momentum_trade_threshold=p['trade_t'],
            momentum_priority_threshold=p['priority_t']
        )
        results.append({
            'Ticker': p['ticker'],
            'Sharpe': sharpe,
            'Final Value': final_val
        })
    
    summary_df = pd.DataFrame(results)
    print('\n--- Analysis Summary ---')
    print(summary_df.to_string(index=False))

if __name__ == '__main__':
    run_volatile_portfolio_analysis()
