import trading_strategy
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# Configuration
PORTFOLIO = [
    {'ticker': 'NFLX', 'trade_t': 0.005, 'priority_t': 0.02},
    {'ticker': 'META', 'trade_t': 0.010, 'priority_t': 0.06},
    {'ticker': 'NVDA', 'trade_t': 0.010, 'priority_t': 0.02},
    {'ticker': 'AMD',  'trade_t': 0.010, 'priority_t': 0.02},
    {'ticker': 'TSLA', 'trade_t': 0.010, 'priority_t': 0.04}
]

ACCOUNT_VALUE = 10000
RISK_PER_TRADE = 0.01

def calculate_risk(ticker, price):
    data = yf.download(ticker, period='1mo', interval='1d', progress=False)
    high_low = data['High'] - data['Low']
    high_cp = np.abs(data['High'] - data['Close'].shift(1))
    low_cp = np.abs(data['Low'] - data['Close'].shift(1))
    tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
    atr = tr.rolling(14).mean().iloc[-1]
    
    stop_loss = price - (2 * atr)
    risk_amt = ACCOUNT_VALUE * RISK_PER_TRADE
    risk_per_share = price - stop_loss
    shares = int(risk_amt / risk_per_share) if risk_per_share > 0 else 0
    return shares, stop_loss, price + (2 * risk_per_share)

def run_daily_automation():
    print(f"--- Automated Risk Report: {datetime.now().strftime('%Y-%m-%d')} ---")
    final_report = []
    
    for config in PORTFOLIO:
        start = (pd.Timestamp.today() - pd.DateOffset(months=6)).strftime('%Y-%m-%d')
        _, _, data, _, _ = trading_strategy.main(
            ticker=config['ticker'], 
            start_date=start, 
            momentum_trade_threshold=config['trade_t'],
            momentum_priority_threshold=config['priority_t']
        )
        
        last = data.iloc[-1]
        signal = last['combined_position']
        price = float(last['Close'])
        
        if signal == 1: # BUY Signal
            shares, sl, tp = calculate_risk(config['ticker'], price)
            final_report.append({
                'Ticker': config['ticker'],
                'Action': 'BUY',
                'Price': round(price, 2),
                'Shares': shares,
                'Stop Loss': round(sl, 2),
                'Take Profit': round(tp, 2)
            })
        else:
            final_report.append({'Ticker': config['ticker'], 'Action': 'HOLD/SELL', 'Price': round(price, 2), 'Shares': 0, 'Stop Loss': '-', 'Take Profit': '-'})

    df = pd.DataFrame(final_report)
    print(df.to_string(index=False))
    df.to_csv('daily_risk_report.csv', index=False)

if __name__ == '__main__':
    run_daily_automation()
