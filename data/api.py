"""
Data should contain headers: Date | Open | High | Low | Close | Adj Close | Volume
"""
import requests
import pandas as pd
import numpy as np

# API call
api_key = 'VHOI1ERJ34C0FKHZ'
stock = "IBM"
url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={stock}&outputsize=full&apikey={api_key}"
data = requests.get(url).json()

# Put data into dataframe
dataframe = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'])

for key in data["Time Series (Daily)"].keys():
#     print(key, "open:",  data["Time Series (Daily)"][key]["1. open"], "high:", data["Time Series (Daily)"][key]["2. high"], "low:",  data["Time Series (Daily)"][key]["3. low"], "close:",  data["Time Series (Daily)"][key]["4. close"], "adj close:",  data["Time Series (Daily)"][key]["5. adjusted close"], "volume:",  data["Time Series (Daily)"][key]["6. volume"])
    dataframe = dataframe.append(
        pd.Series(
            [key,
            data["Time Series (Daily)"][key]["1. open"],
            data["Time Series (Daily)"][key]["2. high"],
            data["Time Series (Daily)"][key]["3. low"],
            data["Time Series (Daily)"][key]["4. close"],
            data["Time Series (Daily)"][key]["5. adjusted close"],
            data["Time Series (Daily)"][key]["6. volume"]], index=dataframe.columns
        ), ignore_index=True
    )

# Clean up dataframe and save to csv
dataframe.sort_values("Date", ascending=True, inplace=True, ignore_index=True)
dataframe.to_csv(f"./data/{stock}.csv", index=False)

### Run this on multiple stocks ###

stock_list = [
    'SPY', 'QQQ', 'RUT', 'DIA', 'AAPL',
    'BAC', 'DE', 'EWZ', 'FXE', 'IBB',
    'IWM', 'SLV', 'GLD', 'T', 'TSLA',
    'WFC', 'FSLR', 'IBM', 'MSFT', 'GOOG']


