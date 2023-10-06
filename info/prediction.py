import pandas as pd
import xgboost as xgb
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from django.http import JsonResponse
import os
from django.conf import settings
from flask import Flask, request, jsonify
import logging
import numpy as np

def get_historical_data(stock_symbol):
    try:
        # Fetch historical data from 2000 to present
        historical_data = yf.Ticker(stock_symbol).history(period="max")
        historical_data = historical_data[['Open', 'High', 'Low', 'Close', 'Volume']]  # Select relevant columns
        historical_data.reset_index(inplace=True)  # Reset index to have Date as a column

        historical_data['Date'] = historical_data['Date'].dt.strftime('%Y-%m-%d')  # Format date to string
        historical_data_dict = historical_data.to_dict(orient='records')  # Convert DataFrame to list of dictionaries

        return historical_data_dict
    except Exception as e:
        raise ValueError(f"Failed to fetch historical data: {str(e)}")

def calculate_rsi(data, window=14):
    delta = data.diff(1)
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi = pd.to_numeric(rsi, errors='coerce')  
    return rsi


def fetch_stock_data(stock_symbol, start_date):
    data = yf.Ticker(stock_symbol)
    data = data.history(period="max")
    data = data.loc[start_date:].copy()
    return data


def engineer_features(data):
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    data['RSI'] = calculate_rsi(data['Close'], window=14)
    data['RSI'] = data['RSI'].replace([np.inf, -np.inf], np.nan)
    data.dropna(subset=['RSI'], inplace=True)
    return data

def train_model(data, features, target):
    print(data)
    trainData = data.copy()
    model = xgb.XGBRegressor(reg_alpha=0.1, reg_lambda=0.1)
    model.fit(trainData[features], trainData[target])
    return model
