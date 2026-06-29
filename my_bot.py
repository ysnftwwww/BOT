import yfinance as yf
import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
import requests

# إعدادات التليجرام
TELEGRAM_TOKEN = '8810137643:AAHmPL3qSAIIgNC6c9JV7jHjR8H6TDpsFow'
CHAT_ID = '8377483931'

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}"
    try:
        requests.get(url)
    except Exception as e:
        print(f"Error sending msg: {e}")

# دالة حساب السوبرتريند يدوياً (بدون مكتبات خارجية)
def calculate_supertrend(df, period=10, multiplier=3):
    atr = (df['High'] - df['Low']).rolling(period).mean()
    upper = ((df['High'] + df['Low']) / 2) + (multiplier * atr)
    lower = ((df['High'] + df['Low']) / 2) - (multiplier * atr)
    return upper, lower

class SupertrendStrategy(Strategy):
    def init(self):
        upper, lower = calculate_supertrend(pd.DataFrame({'High': self.data.High, 'Low': self.data.Low}))
        self.upper = self.I(lambda: upper)
        self.lower = self.I(lambda: lower)

    def next(self):
        # منطق التداول
        if self.data.Close[-1] > self.upper[-1] and self.data.Close[-2] <= self.upper[-2]:
            send_msg("🚀 إشارة شراء (Long) من البوت!")
        elif self.data.Close[-1] < self.lower[-1] and self.data.Close[-2] >= self.lower[-2]:
            send_msg("🔻 إشارة بيع (Short) من البوت!")

if __name__ == "__main__":
    data = yf.download("BTC-USD", period="1mo", interval="1h")
    # التأكد من التنسيق الصحيح للبيانات
    data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    bt = Backtest(data, SupertrendStrategy, cash=10000, commission=.001)
    bt.run()
