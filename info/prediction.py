import pandas as pd
import xgboost as xgb
import yfinance as yf
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg
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

    # Debugging prints
    print("Delta:", delta.head())
    print("Gain:", gain.head())
    print("Loss:", loss.head())
    print("RS:", rs.head())
    print("RSI:", rsi.head())

    # Ensure 'rsi' column is numeric
    rsi = pd.to_numeric(rsi, errors='coerce')  # Convert to numeric, coerce non-numeric values to NaN
    
    return rsi


def fetch_stock_data(stock_symbol, start_date):
    data = yf.Ticker(stock_symbol)
    data = data.history(period="max")
    data = data.loc[start_date:].copy()
    print("Fetched data:", data.head())  # Debugging print
    return data


def engineer_features(data):
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    print("SMA_50 Data:\n", data['SMA_50'].head())  # Print SMA_50 data
    data['SMA_200'] = data['Close'].rolling(window=200).mean()
    print("SMA_200 Data:\n", data['SMA_200'].head())  # Print SMA_200 data
    data['RSI'] = calculate_rsi(data['Close'], window=14)
    print("RSI Data:\n", data['RSI'].head())  # Print RSI data
    
    # Replace infinite values in RSI with NaN
    data['RSI'] = data['RSI'].replace([np.inf, -np.inf], np.nan)
    
    # Drop rows with NaN values only in the 'RSI' column
    data.dropna(subset=['RSI'], inplace=True)
    
    print("Processed data:\n", data.head())  # Print the processed data
    return data

# Call the function with your data
# processed_data = engineer_features(your_data)

def train_model(data, features, target):
    trainData = data.copy()
    model = xgb.XGBRegressor(reg_alpha=0.1, reg_lambda=0.1)
    model.fit(trainData[features], trainData[target])
    return model

# def predict_stock_api(request):
#     if request.method == 'POST':
#         try:
#             stock_symbol = request.POST.get('stock_symbol', '')
#             start_date = request.POST.get('start_date', '2000-01-01')

#             # Fetch data
#             data = fetch_stock_data(stock_symbol, start_date)

#             # Feature engineering
#             data = engineer_features(data)

#             features = ['Open', 'Volume', 'SMA_50', 'SMA_200', 'RSI']
#             target = 'Close'

#             historical_data = get_historical_data(stock_symbol)
#             historical_data_json = json.dumps(historical_data)


#             # Split data based on the input start_date
#             train_data = data.loc[data.index < start_date]  # Data before start_date for training
#             test_data = data.loc[data.index >= start_date]  # Data from start_date onwards for testing

#             # Train model
#             model = train_model(train_data, features, target)

#             # Predictions
#             predictions = model.predict(test_data[features])
#             accuracy = model.score(test_data[features], test_data[target])

#             # Plotting (assuming you have plt.plot() for predictions)

#             # Return prediction data with the image URL and historical data
#             response_data = {
#                 'accuracy': accuracy,
#                 'predictions': predictions.tolist(),
#                 'historical_data': historical_data_json,  # Convert the historical data to JSON
#             }

#             return JsonResponse(response_data)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
#     elif request.method == 'GET':
#         try:
#             img_path = os.path.join(settings.MEDIA_ROOT, 'plots', 'plot.png')
#             with open(img_path, 'rb') as img_file:
#                 response = HttpResponse(img_file.read(), content_type="image/png")
#                 return response
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=400)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=405)