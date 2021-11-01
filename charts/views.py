# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

import requests
import csv
import pandas as pd
import time
import datetime

headers = {
    'Content-Type': 'application/json'
}

nasdaq_smallcap_list = []
nasdaq_mediumcap_list = []
nasdaq_microcap_list = []
nasdaq_largecap_list = []

def get_52_weeks_high(price_data):
  df = pd.DataFrame(price_data)
  df = df.head(253)
  df_price = df[["close"]]
  max = 0 
  for i, row in enumerate(df_price):
    max = df_price["close"].iloc[i] if df_price["close"].iloc[i] > max else max 

  return max

def get_rsi_from_price_data(price_data, date):
  df = pd.DataFrame(price_data)
  df_price = df[["close"]]
  df_price["diff"] = df_price.diff(1)
  df_price["gain"] = df_price["diff"].clip(lower=0).round(2)
  df_price["loss"] = df_price["diff"].clip(upper=0).abs().round(2)

  #get average at 14th period
  df_price["avg_gain"] = df_price["gain"].rolling(window=14, min_periods=14).mean()[:15]
  df_price["avg_loss"] = df_price["loss"].rolling(window=14, min_periods=14).mean()[:15]

  for i, row in enumerate(df_price["avg_gain"].iloc[15:]):
    df_price["avg_gain"].iloc[i + 14 + 1] = (df_price["avg_gain"].iloc[i + 14] * (14 - 1) + df_price["gain"].iloc[i + 14 + 1]) / 14

  for i, row in enumerate(df_price["avg_loss"].iloc[15:]):
    df_price["avg_loss"].iloc[i + 14 + 1] = (df_price["avg_loss"].iloc[i + 14] * (14 - 1) + df_price["loss"].iloc[i + 14 + 1]) / 14

  #calculate rsi
  df_price["rs"] = df_price["avg_gain"] / df_price["avg_loss"]
  df_price["rsi"] = 100 - (100 / (1.0 + df_price["rs"]))
  return df_price.tail()["rsi"]


#micro cap list
with open('stock_symbols/NASDAQ/micro.csv', 'r') as file:
    next(file)
    reader = csv.reader(file, delimiter=",")
    for row in reader:
      nasdaq_microcap_list.append(row[0])
# #small cap list
with open('stock_symbols/NASDAQ/smallcap.csv', 'r') as file:
    next(file)
    reader = csv.reader(file, delimiter=",")
    for row in reader:
      nasdaq_smallcap_list.append(row[0])


# for symbolKey in nasdaq_smallcap_list: 

request_url_xela = "https://api.tiingo.com/tiingo/daily/{0}/prices?startDate=2019-01-02&token=06cad27a78088449bc2e4417afc3404447576d7d".format("XELA")
xela_response = requests.get(request_url_xela, headers=headers)

# #medium cap list
# with open('stock_symbols/NASDAQ/medium.csv', 'r') as file:
#     reader = csv.reader(file, delimiter=",")
#     for row in reader:
#         print(row[0], row[1])

# #large cap list
# with open('stock_symbols/NASDAQ/largecap.csv', 'r') as file:
#     reader = csv.reader(file, delimiter=",")
#     for row in reader:
#         print(row[0], row[1])

def find_52_weeks_high_tickers():
  return ["XELA"]

# Create your views here.
def home(request):
  xela_json = xela_response.json()
  df = pd.DataFrame(xela_json)
  df["date"] = df["date"].apply(lambda x: time.mktime(datetime.datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())) * 1000

  # time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())
  args = {}
  print(df.to_json(orient = "records"))
  args["xela"] = df.to_json(orient = "records")
  args["high52weeks"] = find_52_weeks_high_tickers()
  return render(request, 'charts/home.html', args)

def about(request):
  return HttpResponse('<h1> Chart about </h>') 
