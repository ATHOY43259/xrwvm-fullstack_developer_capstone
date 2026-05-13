from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import logging
import json
import requests

logger = logging.getLogger(__name__)

@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    response_data = {"userName": username}
    if user is not None:
        login(request, user)
        response_data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(response_data)

@csrf_exempt
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})

@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except:
        pass
    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    else:
        return JsonResponse({"userName": username, "error": "Already Registered"})

def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "http://localhost:3030/fetchDealers"
    else:
        endpoint = f"http://localhost:3030/fetchDealers/{state}"
    dealerships = requests.get(endpoint).json()
    return JsonResponse({"status": 200, "dealers": dealerships})

def get_dealer_reviews(request, dealer_id):
    endpoint = f"http://localhost:3030/fetchReviews/dealer/{dealer_id}"
    reviews = requests.get(endpoint).json()
    return JsonResponse({"status": 200, "reviews": reviews})

def get_dealer_details(request, dealer_id):
    endpoint = f"http://localhost:3030/fetchDealer/{dealer_id}"
    dealer = requests.get(endpoint).json()
    return JsonResponse({"status": 200, "dealer": [dealer]})

@csrf_exempt
def add_review(request):
    if request.user.is_anonymous is False:
        data = json.loads(request.body)
        try:
            response = requests.post(
                "http://localhost:3030/insert_review",
                json=data
            )
            return JsonResponse({"status": 200})
        except Exception as e:
            return JsonResponse({"status": 401, "message": str(e)})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})

def get_cars(request):
    from .models import CarMake, CarModel
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name,
            "CarYear": car_model.year
        })
    return JsonResponse({"CarModels": cars})
