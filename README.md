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
