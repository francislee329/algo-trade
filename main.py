from module import TA
from module import Stock
from module import Utility
from module import Plot
import talib as ta
import pandas as pd
import numpy as np
import requests
import math
from math import floor
from datetime import datetime
import logging
import time
import sys
import configparser
import json 
from multiprocessing import Pool
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("main")

def main():
    # config
    IS_OPTIMIZE = False
    CAPITAL = 10000
    STOP_LOST_RATE = 0.9  # 0.1 = 10% stop loss
    stock_tick = "7200.HK"
    start_date = "2021-01-01"
    # end_date = "2017-03-26"
    # start_date = "2017-03-26"
    end_date = datetime.now().strftime("%Y-%m-%d")

    if IS_OPTIMIZE:
        upper_thresholds = [i for i in range(80, 100, 2)] # in percent 
        lower_thresholds = [i for i in range(10, 30, 2)] # in percent 
        periods = [i for i in range(7, 23, 2)] # in days 
    else:
        # Optimal parameters
        periods, lower_thresholds, upper_thresholds = get_stock_config(stock_tick)

    # Process
    MAX_PL = 0
    COUNT = 0
    
    stock = Stock.Stock(stock_tick, start_date, end_date,)  # init
    # Loop all combination 
    for period in periods:
        for lower_threshold in lower_thresholds:
            for upper_threshold in upper_thresholds:
                
                print(f"Period: {period}; Lower Threshold: {lower_threshold}; Upper Threshold: {upper_threshold}")
                # Run strategy 
                trade_plan = stock.strategy_lowBuy(period,lower_threshold,upper_threshold)
                # transaction 
                transaction, profit_loss = Utility.build_transaction(trade_plan, STOP_LOST_RATE)
                
                stock_data = stock.get_data()
                COUNT += 1

                if len(transaction) > 0:
                    all_profit_rate = 1 + profit_loss / CAPITAL
                    yearly_profit = cal_yearly_return(start_date, end_date, all_profit_rate)
                    print(f"PL: {profit_loss}. PL Rate: {all_profit_rate}. Yearly PL Rate: {yearly_profit}")
                    if profit_loss > MAX_PL:
                        MAX_PL = profit_loss
                        best_period = period
                        best_upper = upper_threshold
                        best_lower = lower_threshold
                        print(f"max PL: {profit_loss}")

                    if not IS_OPTIMIZE:
                        transaction.to_csv("./output/transaction.csv")
                        Plot.strategy(stock_tick, stock_data, transaction)
                        Plot.indicators_signals(
                            stock_tick, stock_data, trade_plan, upper_threshold, lower_threshold,
                        )

    if IS_OPTIMIZE:
        all_profit_rate = 1 + profit_loss / CAPITAL
        yearly_profit = cal_yearly_return(start_date, end_date, all_profit_rate)
        print(f"The optimal parameters: ")
        print(f"---Return: {MAX_PL}. Profit Rate: {all_profit_rate}%. Yearly profit: {yearly_profit}")
        print(f"---Period: {best_period}, lower_threshold: {best_lower}, upper_threshold:{best_upper}")

    return COUNT


def cal_yearly_return(start_date, end_date, all_profit_percent):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    years = int((end - start).days / 365)
    yearly_return = (pow(all_profit_percent, 1 / years) - 1) * 100
    return yearly_return


def get_stock_config(stock_tick):
    try: 
        config = configparser.ConfigParser()
        config.read('parameters.ini')
        period = json.loads(config[stock_tick]["period"])
        lower_threshold = json.loads(config[stock_tick]["lower_threshold"])
        upper_threshold = json.loads(config[stock_tick]["upper_threshold"])
    except:
        raise ("NO OPTIMAL CONFIGURATION IS FOUND!!!")

    return period, lower_threshold, upper_threshold


if __name__ == "__main__":
    start = datetime.now()
    print("Start Time =", start.strftime("%H:%M:%S"))
    count = main()
    end = datetime.now()
    print("end Time =", end.strftime("%H:%M:%S"))
    print(f"--- {(end-start).seconds/60} min ---")
    print(f"--- {((end-start).seconds)/count} seconds ---")

