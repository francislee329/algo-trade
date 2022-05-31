import pandas as pd
import logging

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("strategy")


def is_stop_lost(transaction, current_price, stop_lost_rate):
    """
    transaction : input is the transaction dataframe 
    """
    if len(transaction) != 0:
        buy_transaction = transaction[(transaction["action"] == "BUY") & (transaction["status"] == "ACTIVE")]
        if len(buy_transaction) != 0:
            _stop_lost = buy_transaction[
                buy_transaction["price"] > current_price / (1 - stop_lost_rate)
            ]  # stop lost at 10%
            if len(_stop_lost) > 0:
                return True
    return False


def buy_the_dip(data, stop_lost_rate):
    """
    data : input data is indicators signals 
    stop_lost_rate : stop lost rate. eg: 0.1 = stop loss if the stock drop 10%
    """
    transaction = pd.DataFrame()
    capital = 10000
    bet_size = 0.25

    PL = 0
    profit_rate = 0
    total_shares = 0
    n = len(data["signal"])
    for row in data.itertuples():
        signal = row.signal
        index = row.Index
        current_price = row.Adj_Close
        bet = capital * bet_size
        trade_shares = int(bet / current_price)

        if signal == "BUY" and (capital - trade_shares * current_price) > 0:

            trade_money = trade_shares * current_price
            capital -= trade_money

            action = "BUY"
            total_shares += trade_shares
            new_row = pd.DataFrame(
                {
                    "index": [index],
                    "price": [current_price],
                    "trade_shares": [trade_shares],
                    "trade_money": [trade_money],
                    "action": [action],
                    "total_shares": [total_shares],
                    "capital": [capital],
                    "PL": [PL],
                    "status": ["ACTIVE"],
                }
            )
            transaction = pd.concat((transaction, new_row), axis=0).reset_index(drop=True)
        elif (signal == "SELL" and total_shares != 0) or (row.index == data.index[-1]):  # Force to sell by the end of day
            # elif signal == -1 and total_shares != 0:
            if len(transaction) > 0:
                action = "SELL"
                buy_transaction = transaction[(transaction["action"] == "BUY") & (transaction["status"] == "ACTIVE")]
                trade_money = total_shares * current_price
                capital += trade_money
                PL += current_price * total_shares - sum(buy_transaction["trade_money"])
                new_row = pd.DataFrame(
                    {
                        "index": [index],
                        "price": [current_price],
                        "trade_shares": [total_shares],
                        "trade_money": [trade_money],
                        "action": [action],
                        "total_shares": [total_shares],
                        "capital": [capital],
                        "PL": [PL],
                    }
                )

                transaction.loc[transaction["status"] == "ACTIVE", "status"] = "SOLD"
                transaction = pd.concat((transaction, new_row), axis=0).reset_index(drop=True)
                total_shares = 0
        elif is_stop_lost(transaction, current_price, stop_lost_rate):
            # filter buy transaction
            buy_transaction = transaction[(transaction["action"] == "BUY") & (transaction["status"] == "ACTIVE")]
            # filter hit stop lost transaction
            stop_lost = buy_transaction[buy_transaction["price"] > current_price / (1 - stop_lost_rate)]
            logger.info(f"There are {len(stop_lost)} stop loss transactions")
            for index_lost, row_lost in stop_lost.iterrows():
                trade_money = current_price * row_lost["trade_shares"]
                total_shares -= row_lost["trade_shares"]
                PL += trade_money - row_lost["trade_money"]
                capital += trade_money
                action = "STOP LOSS"
                new_row = pd.DataFrame(
                    {
                        "index": [index],
                        "price": [current_price],
                        "trade_shares": [row_lost["trade_shares"]],
                        "trade_money": [trade_money],
                        "action": [action],
                        "total_shares": [total_shares],
                        "capital": [capital],
                        "PL": [PL],
                        "status": row_lost["index"],
                    }
                )
                transaction = pd.concat((transaction, new_row), axis=0).reset_index(drop=True)
                transaction.loc[transaction["index"] == row_lost["index"], "status"] = "CLOSE"

    if len(transaction) > 0:
        transaction = transaction.set_index("index", drop=True)

    return transaction, PL

