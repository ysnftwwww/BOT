import yfinance as yf
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import requests

# 1. إعدادات التليجرام
TELEGRAM_TOKEN = 'توكن_البوت_متاعك'
CHAT_ID = 'الايدي_متاعك'

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}"
    requests.get(url)

# 2. الاستراتيجية
class SupertrendStrategy(Strategy):
    def init(self):
        st = self.I(ta.supertrend, self.data.High, self.data.Low, self.data.Close, length=10, multiplier=3.0)
        self.st_dir = st[:, 1]
        self.atr = self.I(ta.atr, self.data.High, self.data.Low, self.data.Close, length=14)

    def next(self):
        # حساب الأداء الحالي
        stats = self.stats
        summary = f"📈 Win Rate: {stats['Win Rate [%]']:.1f}% | Trades: {stats['# Trades']}"
        
        if crossover(self.st_dir, 0):
            send_msg(f"🚀 إشارة شراء (Long)\n{summary}")
        elif crossover(0, self.st_dir):
            send_msg(f"🔻 إشارة بيع (Short)\n{summary}")

# 3. التشغيل الرئيسي
if __name__ == "__main__":
    data = yf.download("BTC-USD", period="1mo", interval="1h")
    bt = Backtest(data, SupertrendStrategy, cash=10000, commission=.001)
    stats = bt.run()
    
    # تشغيل الاستراتيجية مرة واحدة فقط لآخر شمعة
    SupertrendStrategy.stats = stats # نمرر النتائج للكلاس
    bt.run()
