# Combined Mean-Reversion and Momentum Stock Trading Strategy

This repository contains Python code for a stock trading strategy that combines mean-reversion and momentum principles. The script backtests the strategy against historical data and compares its performance with a simple 'Buy and Hold' approach, providing key performance metrics. The strategy has been enhanced and optimized for better performance in trending markets.

## Strategy Overview

The core idea is to identify trading opportunities by looking for both:
1.  **Mean Reversion**: Prices tending to return to their historical mean.
2.  **Momentum**: Prices continuing their current trend.

This revised strategy now **prioritizes strong momentum signals** to better capture upward (and downward) trends.


## Optimized Strategy Parameters

To achieve the results documented in this analysis, use the following ticker-specific parameters in the `main()` function:

| Ticker | Trade Threshold | Priority Threshold | Expected Result (5Y) |
| :--- | :--- | :--- | :--- |
| **NFLX** | 0.005 | 0.02 | ~279.5% Return |
| **META** | 0.010 | 0.06 | ~174.5% Return |
| **NVDA** | 0.010 | 0.02 | ~60.6% Return |
| **AMD** | 0.010 | 0.02 | -24.5% (Improved over default) |
| **TSLA** | 0.010 | 0.04 | -35.4% (Neutral vs baseline) |

### Usage Example
```python
import trading_strategy
# Example for NFLX
sharpe, value, data, bnh, init = trading_strategy.main(
    ticker='NFLX', 
    momentum_trade_threshold=0.005, 
    momentum_priority_threshold=0.02
)
```

## Final Optimized Parameter Summary
| Ticker   |   Trade Threshold |   Priority Threshold |   Sharpe Ratio |
|:---------|------------------:|---------------------:|---------------:|
| NFLX     |             0.005 |                 0.02 |         0.8386 |
| NVDA     |             0.01  |                 0.02 |         0.4395 |
| TSLA     |             0.01  |                 0.04 |         0.1356 |
| AMD      |             0.01  |                 0.02 |         0.1728 |
| META     |             0.01  |                 0.06 |         0.6924 |

## Why This Project Was Created
This project serves as an automated framework to backtest and optimize a hybrid trading strategy. By combining **Mean Reversion** (buying oversold assets) and **Momentum** (following established trends), the goal was to identify if algorithmic rules could outperform a standard Buy & Hold approach in highly volatile tech stocks while managing significant drawdowns.

## How to Use This in Your Trading
1. **Environment Setup**: Install dependencies via `pip install -r requirements.txt`.
2. **Parameter Selection**: Use the `Final Optimized Parameter Summary` table above as a starting point for specific tickers.
3. **Execution**: Run `trading_strategy.py` to fetch real-time data and generate current signals (Buy, Sell, or Hold).
4. **Refinement**: Use the optimization logic in the provided notebook cells to re-calibrate thresholds as market regimes change (e.g., shifting from a bull to a bear market).

## Critical Points to Remember
* **Risk Warning**: Past performance (like the 30.57% CAGR for NFLX) does not guarantee future results. High-growth tech stocks are subject to sudden shifts in sentiment.
* **Look-ahead Bias**: This backtest uses adjusted closing prices; real-world execution may vary due to slippage and transaction costs.
* **Diversification**: While individual strategies show 'Alpha', combining them into the 'Equal-Weighted Portfolio' helps smooth out the volatility of single-asset failure (e.g., the high drawdowns seen in TSLA or AMD).
* **Signal Priority**: In this model, strong momentum overrides mean reversion. Always verify if a stock is trending before betting on a reversal.
