from function import TA
from function import Process
from function import Strategy
from function import Plot
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

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("main")


def yearly_return(start_date, end_date, all_profit_percent):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    years = int((end - start).days / 365)
    yearly_return = (pow(all_profit_percent, 1 / years) - 1) * 100
    return yearly_return


def get_parameter(stock_tick):
    if stock_tick == "O":
        period = [7]
        lower_threshold = [28]
        upper_threshold = [84]

    elif stock_tick == "BRK-B":
        period = [21]
        lower_threshold = [28]
        upper_threshold = [90]

    elif stock_tick == "TSLA":
        period = [19]
        lower_threshold = [18]
        upper_threshold = [94]

    elif stock_tick == "TQQQ":
        period = [7]
        lower_threshold = [24]
        upper_threshold = [90]

    elif stock_tick == "7200.HK":
        period = [9]
        lower_threshold = [12]
        upper_threshold = [80]

    elif stock_tick == "6823.HK":
        period = [21]
        lower_threshold = [26]
        upper_threshold = [82]
    elif stock_tick == "CARR":
        period = [7]
        lower_threshold = [28]
        upper_threshold = [92]

    else:
        raise ("NO OPTIMAL CONFIGURATION IS FOUND!!!")

    return period, lower_threshold, upper_threshold


def main():
    # config
    is_optimize = False
    capital = 10000
    stop_lost_rate = 0.9  # 0.1 = 10% stop loss
    stock_tick = "7200.HK"
    start_date = "2012-01-01"
    # end_date = "2017-03-26"
    # start_date = "2017-03-26"
    end_date = datetime.now().strftime("%Y-%m-%d")

    if is_optimize:
        upper_thresholds = [i for i in range(80, 100, 2)]
        lower_thresholds = [i for i in range(10, 30, 2)]
        periods = [i for i in range(7, 23, 2)]
    else:
        # Optimal parameters
        periods, lower_thresholds, upper_thresholds = get_parameter(stock_tick)

    # Process
    max_PL = 0
    count = 0
    stock = Process.Stock(stock_tick, start_date, end_date,)  # init
    for period in periods:
        for lower_threshold in lower_thresholds:
            for upper_threshold in upper_thresholds:

                # stock config and data pro-processing
                stock.set_period(period)
                stock.set_lower_threshold(lower_threshold)
                stock.set_upper_threshold(upper_threshold)
                stock.run_LowBuy()

                # Stock data and indicators
                stock_data = stock.get_data()
                plan = stock.get_tradeing_plan()
                transaction, PL = Strategy.buy_the_dip(plan, stop_lost_rate)
                count += 1

                if len(transaction) > 0:
                    all_profit_rate = 1 + PL / capital
                    yearly_profit = yearly_return(start_date, end_date, all_profit_rate)
                    print(f"PL: {PL}. PL Rate: {all_profit_rate}. Yearly PL Rate: {yearly_profit}")
                    if PL > max_PL:
                        max_PL = PL
                        best_period = period
                        best_upper = upper_threshold
                        best_lower = lower_threshold
                        print(f"max PL: {PL}")

                    if not is_optimize:
                        transaction.to_csv("./output/transaction.csv")
                        Plot.strategy(stock_tick, stock_data, transaction)
                        Plot.indicators_signals(
                            stock_tick, stock_data, plan, upper_threshold, lower_threshold,
                        )

    if is_optimize:
        all_profit_rate = 1 + PL / capital
        yearly_profit = yearly_return(start_date, end_date, all_profit_rate)
        print(f"The optimal parameters: ")
        print(f"---Return: {max_PL}. Profit Rate: {all_profit_rate}%. Yearly profit: {yearly_profit}")
        print(f"---Period: {best_period}, lower_threshold: {best_lower}, upper_threshold:{best_upper}")

    return count


if __name__ == "__main__":
    start = datetime.now()
    print("Start Time =", start.strftime("%H:%M:%S"))
    count = main()
    end = datetime.now()
    print("end Time =", end.strftime("%H:%M:%S"))
    print(f"--- {(end-start).seconds/60} min ---")
    print(f"--- {((end-start).seconds)/count} seconds ---")

