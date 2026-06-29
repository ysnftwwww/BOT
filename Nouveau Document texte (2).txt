import yfinance as yf
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# --- 1. جلب البيانات ---
# نستخدم البيانات التاريخية للبيتكوين (يمكنك تغيير "BTC-USD" لأي عملة أخرى)
data = yf.download("BTC-USD", period="1mo", interval="1h")

# تنظيف البيانات: التأكد من عدم وجود قيم فارغة (NaN)
data.dropna(inplace=True)

# --- 2. تعريف الاستراتيجية ---
class SupertrendStrategy(Strategy):
    # الإعدادات (نفس قيمك في Pine Script)
    st_period = 10
    st_factor = 3.0
    atr_period = 14
    atr_mult = 1.5
    rr = 1.5

    def init(self):
        # حساب السوبر تريند باستخدام pandas_ta
        # المخرجات تكون: [SUPERT, SUPERTd, SUPERTl, SUPERTs]
        # نحن نهتم بالعمود الثاني [SUPERTd] الذي يمثل الاتجاه
        st = self.I(ta.supertrend, self.data.High, self.data.Low, self.data.Close, 
                    length=self.st_period, multiplier=self.st_factor)
        
        self.st_dir = st[:, 1]  # اتجاه التريند
        self.atr = self.I(ta.atr, self.data.High, self.data.Low, self.data.Close, length=self.atr_period)

    def next(self):
        # منطق الدخول (شراء/بيع)
        # crossover تعني تقاطع القيمة مع الصفر
        if crossover(self.st_dir, 0): 
            # حساب مستويات الصفقة
            sl = self.data.Close[-1] - (self.atr[-1] * self.atr_mult)
            tp = self.data.Close[-1] + ((self.data.Close[-1] - sl) * self.rr)
            # تنفيذ الشراء
            self.buy(sl=sl, tp=tp)
            
        elif crossover(0, self.st_dir):
            # حساب مستويات الصفقة
            sl = self.data.Close[-1] + (self.atr[-1] * self.atr_mult)
            tp = self.data.Close[-1] - ((sl - self.data.Close[-1]) * self.rr)
            # تنفيذ البيع
            self.sell(sl=sl, tp=tp)

# --- 3. تشغيل الباك تست ---
# cash: رأس المال الابتدائي
# commission: عمولة المنصة (0.1% مثلاً هي 0.001)
bt = Backtest(data, SupertrendStrategy, cash=10000, commission=.001, exclusive_orders=True)

# --- 4. استخراج النتائج ---
stats = bt.run()

# طباعة التقرير الكامل
print("--- تقرير أداء الاستراتيجية ---")
print(stats)

# رسم النتائج (سيفتح صفحة ويب بها الشارت والصفقات)
bt.plot()