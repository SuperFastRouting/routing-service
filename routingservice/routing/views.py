from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

from routing.app import routing

# Create your views here.
def index(request):
    return JsonResponse({"test": "content"}, status=200)