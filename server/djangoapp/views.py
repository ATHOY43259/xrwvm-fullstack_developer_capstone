import os
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

NODE_URL = os.environ.get("NODE_SERVICE_URL", "http://localhost:3030")

@csrf_exempt
def login_user(request):
    try:
        body = request.body
        if not body:
            return JsonResponse({"error": "Empty body", "method": request.method, "ct": request.content_type}, status=400)
        data = json.loads(body)
        username = data.get("userName", "")
        password = data.get("password", "")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        return JsonResponse({"userName": username, "status": "Failed"})
    except Exception as e:
        return JsonResponse({"error": str(e), "body_len": len(request.body)}, status=400)

@csrf_exempt
def logout_request(request):
    username = request.GET.get("userName")
    logout(request)
    return JsonResponse({"userName": username})

@csrf_exempt
def registration(request):
    try:
        data = json.loads(request.body)
        username = data["userName"]
        password = data["password"]
        first_name = data["firstName"]
        last_name = data["lastName"]
        email = data["email"]
        if User.objects.filter(username=username).exists():
            return JsonResponse({"userName": username, "error": "Already Registered"})
        user = User.objects.create_user(
            username=username, first_name=first_name,
            last_name=last_name, password=password, email=email
        )
        login(request, user)
        return JsonResponse({"userName": username, "status": "Authenticated"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def get_dealerships(request, state="All"):
    try:
        if state == "All":
            endpoint = f"{NODE_URL}/fetchDealers"
        else:
            endpoint = f"{NODE_URL}/fetchDealers/{state}"
        dealerships = requests.get(endpoint).json()
        return JsonResponse({"status": 200, "dealers": dealerships})
    except Exception as e:
        return JsonResponse({"status": 200, "dealers": []})

def get_dealer_reviews(request, dealer_id):
    try:
        endpoint = f"{NODE_URL}/fetchReviews/dealer/{dealer_id}"
        reviews = requests.get(endpoint).json()
        return JsonResponse({"status": 200, "reviews": reviews})
    except Exception as e:
        return JsonResponse({"status": 200, "reviews": []})

def get_dealer_details(request, dealer_id):
    try:
        endpoint = f"{NODE_URL}/fetchDealer/{dealer_id}"
        dealer = requests.get(endpoint).json()
        return JsonResponse({"status": 200, "dealer": [dealer]})
    except Exception as e:
        return JsonResponse({"status": 200, "dealer": []})

@csrf_exempt
def add_review(request):
    if not request.user.is_anonymous:
        try:
            data = json.loads(request.body)
            response = requests.post(f"{NODE_URL}/insert_review", json=data)
            return JsonResponse({"status": 200})
        except Exception as e:
            return JsonResponse({"status": 401, "message": str(e)})
    return JsonResponse({"status": 403, "message": "Unauthorized"})

def get_cars(request):
    from .models import CarMake, CarModel
    car_models = CarModel.objects.select_related("car_make")
    cars = [{"CarModel": c.name, "CarMake": c.car_make.name, "CarYear": c.year} for c in car_models]
    return JsonResponse({"CarModels": cars})


