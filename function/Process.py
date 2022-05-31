import yfinance as yf
from datetime import datetime
import pandas as pd
import numpy as np
import talib as ta
from function import TA


class Stock:
    def __init__(self, tick, start_date, end_date):
        self.tick = tick
        self.start_date = start_date
        self.end_date = end_date

    def download_preprocessing_data(self):
        print(
            f"Period: {self.period}, Lower Threshold: {self.lower_threshold}, Upper Threshold: {self.upper_threshold}"
        )
        self.data = yf.download(self.tick, start=self.start_date, end=self.end_date, progress=False,)
        if len(self.data) == 0:
            raise ("DOWNLOAD DATA ERROR")
        else:
            self.data["date"] = self.data.index
            self.data["K"], self.data["D"] = TA.stoch(self.data, self.period)
            self.data["RSI"] = TA.NormalizeData(ta.RSI(self.data["Close"], self.period))
            self.data["ROC"] = ta.ROC(self.data["Close"], self.period)
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
            self.data = self.data.rename(columns={"Adj Close": "Adj_Close"})
            self.data = self.data.dropna()

    def VPC(df):
        max = 0
        vpc = pd.DataFrame()
        prices = []
        index_list = []
        for idx, price in df["Close"].iteritems():
            if price > max:
                max = price
                prices.append(price)
                index_list.append(idx)
        vpc["price"] = prices
        vpc["date"] = index_list
        return vpc

    def plan_strategy_UpTrend():
        vpc = VCP(self.data)
        prices = []
        index_list = []
        MA5_slope = ta.LINEARREG_SLOPE(self.data["MA5"], 3)
        MA5_peak = df[(MA5_slope <= 0) & (MA5_slope.shift(1) >= 0)]
        for idx, price in self.data["Close"].iteritems():
            peak_signals = MA5_peak[MA5_peak.index < idx]
            if len(peak_signals) >= 2 and price >= peak_signals[-1] and price >= peak_signals[-2]:
                prices.append(price)
                index_list.append(idx)

    def plan_strategy_LowBuy(self):
        buy_price = []
        sell_price = []
        signals = []

        self.data['BUY_RSI'] = (self.data["RSI"] < self.lower_threshold)
        self.data['BUY_SO'] = (self.data["K"] < self.lower_threshold) & (self.data["D"] < self.lower_threshold) & (self.data["K"] < self.data["D"])
        self.data['BUY_ROC'] = (self.data["ROC"] <= 0)
        self.data['BUY_MA'] = (self.data["MA10"] <= self.data["MA20"])
        
        self.data['SELL_RSI'] = (self.data["RSI"] >= self.upper_threshold)
        self.data['SELL_SO'] = (self.data["K"] > self.upper_threshold) & (self.data["D"] > self.upper_threshold) & (self.data["K"] > self.data["D"])
        self.data['SELL_MA'] = (self.data["MA10"] >= self.data["MA20"]) & (self.data["MA20"] >= self.data["MA60"])
        self.data['SELL_ROC'] = (self.data["ROC"] >= 0)
        
        # combine to BUY and SELL 
        self.data['BUY_SIGNAL'] = self.data['BUY_RSI'] & self.data['BUY_SO'] & self.data['BUY_ROC'] & self.data['BUY_MA']
        self.data['SELL_SIGNAL'] = self.data['SELL_RSI'] & self.data['SELL_SO'] & self.data['SELL_MA'] & self.data['SELL_ROC']
            
        BUY = self.data[self.data['BUY_SIGNAL'] == True ] 
        BUY = BUY [["Close", "Adj_Close"]]
        BUY["signal"] = "BUY"
        BUY["buy_price"] = BUY["Close"]
        
        SELL = self.data[self.data['SELL_SIGNAL'] == True ] 
        SELL = SELL [["Close", "Adj_Close"]]
        SELL["signal"] = "SELL"
        SELL["sell_price"] = SELL["Close"]
        
        self.plan = pd.concat([BUY, SELL])
        self.plan = self.plan.sort_index()
        print(self.plan)


    def run_LowBuy(self):
        self.download_preprocessing_data()
        self.plan_strategy_LowBuy()

    def run_UpTrend(self):
        self.download_preprocessing_data()
        self.plan_strategy_UpTrend()

    def get_tradeing_plan(self):
        return self.plan

    def get_data(self):
        return self.data

    def set_period(self, period):
        self.period = period

    def set_lower_threshold(self, lower_threshold):
        self.lower_threshold = lower_threshold

    def set_upper_threshold(self, upper_threshold):
        self.upper_threshold = upper_threshold

