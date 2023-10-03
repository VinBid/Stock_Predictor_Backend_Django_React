from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer
from .prediction import fetch_stock_data, engineer_features, train_model, calculate_rsi, get_historical_data
import os
import tempfile
import json
import matplotlib.pyplot as plt
from django.conf import settings
from datetime import datetime


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
            print("this is request data", request_data)

            # Fetch data
            data = fetch_stock_data(stock_symbol, start_date)
            print(data)

            # Feature engineering
            data = engineer_features(data)

            features = ['Open', 'Volume', 'SMA_50', 'SMA_200', 'RSI']
            target = 'Close'

            # Train model
            model = train_model(data, features, target)

            # Split data into test set for predictions
            test_data = data.copy()

            # Predictions
            predictions = model.predict(test_data[features])
            accuracy = model.score(test_data[features], test_data[target])

            # # Plotting
            # plot_url = generate_plot(data['Close'], test_data.index, predictions)

            # Get historical data
            historical_data = get_historical_data(stock_symbol)
            historical_data_json = json.dumps(historical_data)

            # Return prediction data with the image URL and historical data
            response_data = {
                'accuracy': accuracy,
                'predictions': predictions.tolist(),
                'historical_data': historical_data_json,
            }
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)