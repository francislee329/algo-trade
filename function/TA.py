import numpy as np
import pandas as pd



def stoch(df, n):
    high = df["High"].rolling(n).max()
    low = df["Low"].rolling(n).min()
    K = NormalizeData((df["Close"] - low) * 100 / (high - low))
    D = NormalizeData(K.rolling(3).mean())
    return K, D


# calculation of rate of change
def ROC(df, n):
    M = df["Close"].diff(n - 1)
    N = df["Close"].shift(n - 1)
    ROC = pd.Series(((M / N) * 100), name="ROC_" + str(n))
    return ROC


def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data)) *100
