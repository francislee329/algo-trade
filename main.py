from module import TA
from module import Stock
from module import Utility
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
from joblib import Parallel, delayed

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("main")


def main():
    # config
    IS_OPTIMIZE = False
    CAPITAL = 10000
    STOP_LOST_RATE = 0.9  # 0.1 = 10% stop loss
    stock_tick = "TQQQ"
    start_date = "2012-05-01"
    # end_date = "2017-03-26"
    # start_date = "2017-03-26"
    end_date = datetime.now().strftime("%Y-%m-%d")
    stock = Stock.Stock(stock_tick, start_date, end_date,)  # init

    if IS_OPTIMIZE:
        upper_thresholds = [i for i in range(80, 100, 2)]  # in percent
        lower_thresholds = [i for i in range(10, 30, 2)]  # in percent
        periods = [i for i in range(7, 23, 2)]  # in days
    else:
        # Optimal parameters
        periods, lower_thresholds, upper_thresholds = get_stock_config(stock_tick)

    # Add all combination to the queue
    delayed_funcs = []
    for period in periods:
        for lower_threshold in lower_thresholds:
            for upper_threshold in upper_thresholds:
                logging.info(
                    f"Period: {period}; Lower Threshold: {lower_threshold}; Upper Threshold: {upper_threshold}"
                )
                delayed_funcs.append(
                    delayed(training)(
                        stock, period, lower_threshold, upper_threshold, CAPITAL, STOP_LOST_RATE, IS_OPTIMIZE
                    )
                )

    # Multi processing
    q = Parallel(n_jobs=-1, verbose=5, prefer="processes")(delayed_funcs)

    # Evaluate the performance
    performance = pd.DataFrame(q)
    evaluate_performance(performance)


def training(
    stock: Stock,
    period: int,
    lower_threshold: int,
    upper_threshold: int,
    CAPITAL: int,
    STOP_LOST_RATE: float,
    IS_OPTIMIZE: bool,
):
    start_date = stock.get_start_date()
    end_date = stock.get_end_date()
    # Run strategy
    trade_plan, transaction, profit_loss = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    trade_plan = stock.strategy_lowBuy(period, lower_threshold, upper_threshold)
    # transaction
    transaction, profit_loss = Utility.build_transaction(trade_plan, STOP_LOST_RATE)

    if len(transaction) > 0:
        all_profit_rate = 1 + profit_loss / CAPITAL
        yearly_profit = cal_yearly_return(start_date, end_date, all_profit_rate)
        logging.info(f"PL: {profit_loss}. PL Rate: {all_profit_rate}. Yearly PL Rate: {yearly_profit}")

        new_dict = {
            "lower_threshold": lower_threshold,
            "upper_threshold": upper_threshold,
            "period": period,
            "PL": profit_loss,
            "PL_rate": all_profit_rate,
            "PL_rate_yearly": yearly_profit,
        }
    else:
        new_dict = {
            "lower_threshold": lower_threshold,
            "upper_threshold": upper_threshold,
            "period": period,
            "PL": 0,
            "PL_rate": 0,
            "PL_rate_yearly": 0,
        }
    if not IS_OPTIMIZE:
        visualization(stock.get_tick(), stock.get_data(), upper_threshold, lower_threshold, trade_plan, transaction)

    return new_dict


def evaluation(transaction: pd.DataFrame, performance: pd.DataFrame):
    transaction.to_csv("./output/transaction.csv")
    performance = performance.sort_values(by=["PL"])
    performance.to_csv("./output/performance.csv")


def evaluate_performance(performance: pd.DataFrame):
    performance = performance.sort_values(by=["PL"], ascending=False)
    performance.to_csv("./output/performance.csv")


# stock_data = stock.get_data()
def visualization(
    stock_tick: str,
    stock_data: pd.DataFrame,
    upper_threshold: int,
    lower_threshold: int,
    trade_plan: pd.DataFrame,
    transaction: pd.DataFrame,
):
    from module import Plot

    Plot.strategy(stock_tick, stock_data, transaction)
    Plot.indicators_signals(
        stock_tick, stock_data, trade_plan, upper_threshold, lower_threshold,
    )


def cal_yearly_return(start_date, end_date, all_profit_percent):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    years = int((end - start).days / 365)
    yearly_return = (pow(all_profit_percent, 1 / years) - 1) * 100
    return yearly_return


def get_stock_config(stock_tick):
    try:
        config = configparser.ConfigParser()
        config.read("parameters.ini")
        period = json.loads(config[stock_tick]["period"])
        lower_threshold = json.loads(config[stock_tick]["lower_threshold"])
        upper_threshold = json.loads(config[stock_tick]["upper_threshold"])
    except:
        raise ("NO OPTIMAL CONFIGURATION IS FOUND!!!")

    return period, lower_threshold, upper_threshold


if __name__ == "__main__":
    start = datetime.now()
    print("Start Time =", start.strftime("%H:%M:%S"))
    main()
    end = datetime.now()
    print("end Time =", end.strftime("%H:%M:%S"))
    print(f"--- {(end-start).seconds/60} m ---")

