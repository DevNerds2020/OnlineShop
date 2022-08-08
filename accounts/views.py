from django.contrib.auth import authenticate, login, logout
from .serializers import *
import json
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


@csrf_exempt
def register_customer(request):
    if request.method != "POST":
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            username = data['username']
            password = data['password']
            first_name = data['first_name']
            last_name = data['last_name']
            email = data['email']
            phone = data['phone']
            address = data['address']
            user = {
                'username': username,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            }
            serializer = UserSerializer(data=user)
            if serializer.is_valid():
                serializer.save()
                u = User.objects.get(id=serializer.data['id'])
                u.set_password(password)
                u.save()
                customer = {
                    'user': u.id,
                    'phone': phone,
                    'address': address
                }
                customerserializer = CustomerSerializer(data=customer)
                if customerserializer.is_valid():
                    customerserializer.save()
                    response = '{"id": ' + str(customerserializer.data['id']) + '}'
                    response = json.loads(response)
                    return JsonResponse(response, status=201)
                else:
                    u.delete()
                    return JsonResponse(customerserializer.errors, status=400)
            else:
                return JsonResponse(serializer.errors, status=400)
        except:
            return JsonResponse({"message": "you are doing it wrong bro"}, status=400)


@csrf_exempt
def customer_list(request):
    if request.method != "GET":
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    c = Customer.objects.all()
    # serializer = ProductSerializer(p, many=True)
    # return JsonResponse(serializer.data, safe=False, status=200)
    if 'search' in request.GET:
        searched = request.GET['search']
        c = c.filter(Q(user__first_name__contains=searched) |
                     Q(user__last_name__contains=searched) |
                     Q(user__username__contains=searched) |
                     Q(address__contains=searched))
    # serializer = CustomerSerializer(c, many=True)

    return JsonResponse({'customers': [i.to_dict() for i in c]}, status=200)


@csrf_exempt
def customer_data(request, id):
    if request.method != "GET":
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    try:
        c = Customer.objects.get(id=id)
        return JsonResponse(c.to_dict(), status=200)

    except:
        message = '{"message": "Customer Not Found."}'
        errormsg = json.loads(message)
        return JsonResponse(errormsg, status=404)


@csrf_exempt
def customer_edit(request, id):
    if request.method != "POST":
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    try:
        data = JSONParser().parse(request)
    except:
        return JsonResponse({"you are doing it wrong bro"}, status=400)
    try:
        c = Customer.objects.get(id=id)
    except:
        return JsonResponse({"Customer not found"}, status=404)
    if 'username' in data or 'password' in data or 'id' in data:
        return JsonResponse({"message": "Cannot edit customer's identity or credentials"}, status=403)

    try:
        if 'first_name' in data:
            c.user.first_name = data['first_name']
        if 'last_name' in data:
            c.user.last_name = data['last_name']
        if 'phone' in data:
            c.phone = data['phone']
        if 'balance' in data:
            c.balance = data['balance']
        if 'address' in data:
            c.address = data['address']
        if 'email' in data:
            c.user.email = data['email']
        c.user.save()
        c.save()
        return JsonResponse(c.to_dict(), status=200)
    except:
        return JsonResponse({'message': 'you are doing something wrong dude'}, status=400)


@csrf_exempt
def customer_login(request):
    if request.method != "POST":
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    try:
        data = JSONParser().parse(request)
        if request.user.is_authenticated:
            return JsonResponse({"message": "you are already in dude"}, status=200)
        user = authenticate(request, username=data['username'], password=data['password'])
        if user is not None:
            login(request, user)
            return JsonResponse({"message": "You are logged in successfully."}, status=200)
        else:
            return JsonResponse({"message": "Username or Password is incorrect."}, status=404)
    except:
        return JsonResponse({'message': 'you are doing something wrong dude'}, status=400)


@csrf_exempt
def customer_logout(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    try:
        data = JSONParser().parse(request)
        if len(data) > 0:
            raise Exception("")
        if request.user.is_authenticated:
            logout(request)
            return JsonResponse({"message": "hooray you are out of my system"}, status=200)
        else:
            return JsonResponse({"message": "dude you are not logged in why are you trying to log out :)"}, status=403)
    except:
        return JsonResponse({"message": "i hate to say this but something is wrong"}, status=400)


@csrf_exempt
def customer_profile(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    if request.user.is_authenticated:
        c = Customer.objects.get(user_id=request.user.id)
        return JsonResponse(c.to_dict(), status=200)

    return JsonResponse({"message": "You are not logged in."}, status=403)
