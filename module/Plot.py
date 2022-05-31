import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

plt.rcParams["figure.figsize"] = (20, 10)
plt.style.use("fivethirtyeight")


def strategy(stock_tick, data, transaction):
    config = {"scrollZoom": True}
    buy = transaction[transaction["action"] == "BUY"]
    sell = transaction[transaction["action"] == "SELL"]
    stop_lost = transaction[transaction["action"] == "STOP LOSS"]
    trace1 = go.Line(x=data["date"], y=data["Close"], line=dict(color="#345ceb", width=3), name="Price", yaxis="y1",)

    trace2 = go.Scattergl(
        x=buy.index,
        y=buy["price"],
        mode="markers",
        marker_symbol="triangle-up",
        marker_color="#7deb34",
        marker_size=20,
        name="BUY",
        yaxis="y1",
    )

    trace3 = go.Scatter(
        x=sell.index,
        y=sell["price"],
        mode="markers",
        marker_symbol="triangle-down",
        marker_color="red",
        marker_size=20,
        name="SELL",
        yaxis="y1",
    )

    trace4 = go.Scatter(
        x=stop_lost.index,
        y=stop_lost["price"],
        mode="markers",
        marker_symbol="triangle-down",
        marker_color="#ebb134",
        marker_size=20,
        name="STOP LOSS",
        yaxis="y1",
    )
    fig = make_subplots()
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.add_trace(trace3)
    fig.add_trace(trace4)
    fig.show(config=config)


def indicators_signals(stock_tick, stock_data, indicator, upper_threshold, lower_threshold):
    ax1 = plt.subplot2grid((12, 1), (0, 0), rowspan=3, colspan=1)
    ax1.plot(indicator["Adj_Close"], color="skyblue", label=stock_tick)
    ax1.plot(
        indicator.index,
        indicator["buy_price"],
        marker="^",
        color="green",
        markersize=10,
        label="BUY SIGNAL",
        linewidth=0,
    )
    ax1.plot(
        indicator.index,
        indicator["sell_price"],
        marker="v",
        color="r",
        markersize=10,
        label="SELL SIGNAL",
        linewidth=0,
    )
    ax1.legend(loc="upper left")
    ax1.set_title(stock_tick + " all signals")
    # 2nd graph
    ax2 = plt.subplot2grid((12, 1), (4, 0), rowspan=3, colspan=1)
    ax2.plot(stock_data["K"], color="deepskyblue", linewidth=1.5, label="K")
    ax2.plot(stock_data["D"], color="orange", linewidth=1.5, label="D")
    ax2.axhline(upper_threshold, color="black", linewidth=1, linestyle="--")
    ax2.axhline(lower_threshold, color="black", linewidth=1, linestyle="--")
    ax2.set_title(f"{stock_tick} STOCH")
    ax2.legend()
    # 3rd graph
    ax2 = plt.subplot2grid((12, 1), (8, 0), rowspan=3, colspan=1)
    ax2.plot(stock_data["RSI"], color="deepskyblue", linewidth=1.5, label="K")
    ax2.axhline(upper_threshold, color="black", linewidth=1, linestyle="--")
    ax2.axhline(lower_threshold, color="black", linewidth=1, linestyle="--")
    ax2.set_title(f"{stock_tick} RSI")
    ax2.legend()
    plt.savefig("./output/signal.jpg")
    plt.show()


def indicator_compare(df, col1, col2):
    trace1 = go.Line(x=df["date"], y=df[col1], yaxis="y1", name=col1, line=dict(color="royalblue", width=3),)
    trace2 = go.Line(x=df["date"], y=df[col2], yaxis="y2", name=col2, line=dict(color="#eb9234", width=3),)
    fig = make_subplots(specs=[[{"secondary_y": True}]], subplot_titles=[f"Comparison between ({col1}) and ({col2})"],)
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.show()


def price_compare(df, col1):
    trace1 = go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], yaxis="y1", name="Price",
    )

    trace2 = go.Line(x=df["date"], y=df[col1], yaxis="y2", line=dict(color="#eb9234", width=3), name=col1,)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2)
    fig.show()
