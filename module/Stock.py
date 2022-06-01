import yfinance as yf
from datetime import datetime
import pandas as pd
import numpy as np
import talib as ta
from module import TA


class Stock:
    def __init__(self, tick, start_date, end_date):
        self.tick, self.start_date, self.end_date = tick, start_date, end_date
        self.download_data()

    def download_data(self):
        self.data = yf.download(self.tick, start=self.start_date, end=self.end_date, progress=False,)
        self.data = self.data.rename(columns={"Adj Close": "Adj_Close"})
        self.data = self.data.dropna()

    def preprocessing_data(self, period: int):
        if len(self.data) == 0:
            raise ("DOWNLOAD DATA ERROR")
        else:
            self.data["date"] = self.data.index
            self.data["K"], self.data["D"] = TA.stoch(self.data, period)
            self.data["RSI"] = TA.NormalizeData(ta.RSI(self.data["Close"], period))
            self.data["ROC"] = ta.ROC(self.data["Close"], period)
            self.data["MA5"] = ta.SMA(self.data["Close"], 5)
            self.data["MA10"] = ta.SMA(self.data["Close"], 10)
            self.data["MA20"] = ta.SMA(self.data["Close"], 20)
            self.data["MA60"] = ta.SMA(self.data["Close"], 60)
            # stock_data["OBV"] = ta.OBV(stock_data["Close"], stock_data["Volume"])
            # OBV_slope = ta.LINEARREG_SLOPE(stock_data["OBV"], 5)
            # stock_data["OBV_slope"] = TA.NormalizeData(OBV_slope)
            # stock_data["MA10_slope"] = ta.LINEARREG_SLOPE(stock_data["MA10"])
            # stock_data["MA20_slope"] = ta.LINEARREG_SLOPE(stock_data["MA20"], 5)
            # stock_data["MA120_slope"] = ta.LINEARREG_SLOPE(stock_data["MA120"], 5)

    def VPC(df:pd.DataFrame):
        max = 0
        vpc = pd.DataFrame()
        prices, index_list = [], []
        for idx, price in df["Close"].iteritems():
            if price > max:
                max = price
                prices.append(price)
                index_list.append(idx)
        vpc["price"] = prices
        vpc["date"] = index_list
        return vpc

    def plan_strategy_UpTrend(self):
        vpc = VCP(self.data)
        prices, index_list = [], []
        ma5_slope = ta.LINEARREG_SLOPE(self.data["MA5"], 3)
        ma5_peak = df[(ma5_slope <= 0) & (ma5_slope.shift(1) >= 0)]
        for idx, price in self.data["Close"].iteritems():
            peak_signals = ma5_peak[ma5_peak.index < idx]
            if len(peak_signals) >= 2 and price >= peak_signals[-1] and price >= peak_signals[-2]:
                prices.append(price)
                index_list.append(idx)

    def strategy_LowBuy(self, lower_threshold: int, upper_threshold: int) -> pd.DataFrame:
        _buy_RSI = self.data["RSI"] < lower_threshold
        _buy_SO = (
            (self.data["K"] < lower_threshold) & (self.data["D"] < lower_threshold) & (self.data["K"] < self.data["D"])
        )
        _buy_ROC = self.data["ROC"] <= 0
        _buy_MA = self.data["MA10"] <= self.data["MA20"]

        _sell_RSI = self.data["RSI"] >= upper_threshold
        _sell_SO = (
            (self.data["K"] > upper_threshold) & (self.data["D"] > upper_threshold) & (self.data["K"] > self.data["D"])
        )
        _sell_MA = (self.data["MA10"] >= self.data["MA20"]) & (self.data["MA20"] >= self.data["MA60"])
        _sell_ROC = self.data["ROC"] >= 0

        # combine to BUY and SELL
        buy_SIGNAL = _buy_RSI & _buy_SO & _buy_ROC & _buy_MA
        sell_SIGNAL = _sell_RSI & _sell_SO & _sell_MA & _sell_ROC

        _buy = self.data[buy_SIGNAL == True]
        _buy = _buy[["Close", "Adj_Close"]]
        _buy["signal"] = "BUY"
        _buy["buy_price"] = _buy["Close"]

        _sell = self.data[sell_SIGNAL == True]
        _sell = _sell[["Close", "Adj_Close"]]
        _sell["signal"] = "SELL"
        _sell["sell_price"] = _sell["Close"]

        _plan = pd.concat([_buy, _sell])
        _plan = _plan.sort_index()
        return _plan

    def strategy_lowBuy(self, period: int, lower_threshold: int, upper_threshold: int)-> pd.DataFrame:
        self.preprocessing_data(period)
        trade_plan = self.strategy_LowBuy(lower_threshold, upper_threshold)
        return trade_plan

    def get_data(self):
        return self.data
    
    def get_start_date(self): 
        return self.start_date

    def get_end_date(self): 
        return self.end_date

