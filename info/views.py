from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer
from .prediction import fetch_stock_data, engineer_features, train_model, get_historical_data, calculate_rsi
import os
import tempfile
import json
import matplotlib.pyplot as plt
from django.conf import settings
import yfinance as yf
import xgboost as xgb
from django.shortcuts import render, redirect
from .forms import SignInForm

def sign_in(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the home page or wherever you want to go after sign-in
    else:
        form = SignInForm()
    
    return render(request, 'sign_in.html', {'form': form})

def home(request):
    # Retrieve the user's information from the database (you may need to implement user authentication)
    user = UserProfile.objects.first()  # For demonstration purposes, this gets the first user in the database
    return render(request, 'home.html', {'user': user})

@api_view(['GET'])
def get_customer_info(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response({'customers': serializer.data})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@api_view(['POST'])
def predict_stock_api(request):
    if request.method == 'POST':
        try:
            request_data = json.loads(request.body)
            stock_symbol = request_data.get('stock_symbol', '')
            start_date = request_data.get('start_date', '2000-01-01')

            # Fetch data
            data = yf.Ticker(stock_symbol)
            data = data.history(period="max")
            data = data.loc["2000-01-01":].copy()

            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['SMA_200'] = data['Close'].rolling(window=200).mean()
            data['RSI'] = calculate_rsi(data['Close'], window=14)
            data.dropna(inplace=True)
            # Split data into training and testing sets
            train_data = data[data.index < start_date]
            test_data = data[data.index >= start_date]

            features = ['Open', 'Volume', 'SMA_50', 'SMA_200', 'RSI']
            target = 'Close'

            # Train model
            model = xgb.XGBRegressor(reg_alpha=0.1, reg_lambda=0.1)
            model.fit(train_data[features], train_data[target])
            # Predictions
            predictions = model.predict(test_data[features])
            accuracy = model.score(test_data[features], test_data[target])

            # Get historical data
            historical_data = get_historical_data(stock_symbol)
            

            # Return prediction data with historical data
            response_data = {
                'accuracy': accuracy,
                'predictions': predictions.tolist(),
                'historical_data': historical_data,
            }
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)