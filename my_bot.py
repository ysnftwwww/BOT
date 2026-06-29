import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import requests

# إعدادات التليجرام الخاصة بك
TELEGRAM_TOKEN = '8810137643:AAHmPL3qSAIlIgNC6c9JV7jHjR8H6TDpsFow'
CHAT_ID = '8377483931'

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}"
    requests.get(url)

class SupertrendStrategy(Strategy):
    def init(self):
        st = self.I(ta.supertrend, self.data.High, self.data.Low, self.data.Close, length=10, multiplier=3.0)
        self.st_dir = st[:, 1]

    def next(self):
        if crossover(self.st_dir, 0):
            send_msg("🚀 إشارة شراء (Long) من البوت!")
        elif crossover(0, self.st_dir):
            send_msg("🔻 إشارة بيع (Short) من البوت!")

if __name__ == "__main__":
    data = yf.download("BTC-USD", period="1mo", interval="1h")
    bt = Backtest(data, SupertrendStrategy, cash=10000, commission=.001)
    bt.run()
