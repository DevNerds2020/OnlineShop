import json
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

# Create your views here.
from .serializers import ProductSerializer, OrderSerializer


@csrf_exempt
def get_products(request):
    if request.method != "GET":
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    p = Product.objects.all()
    # serializer = ProductSerializer(p, many=True)
    # return JsonResponse(serializer.data, safe=False, status=200)
    if 'search' in request.GET:
        p = p.filter(name__contains=request.GET['search'])
    serializer = ProductSerializer(p, many=True)
    return JsonResponse({"products": serializer.data}, safe=False, status=200)


@csrf_exempt
def get_product(request, id):
    if request.method != "GET":
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    try:
        p = Product.objects.get(id=id)
        serializer = ProductSerializer(p)
        return JsonResponse(serializer.data, safe=False, status=200)
    except:
        message = '{"message": "Product Not Found."}'
        errormsg = json.loads(message)
        return JsonResponse(errormsg, status=404)


@csrf_exempt
def add_product(request):
    if request.method != "POST":
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response = '{"id": ' + str(serializer.data['id']) + '}'
            response = json.loads(response)
            return JsonResponse(response, status=201)

        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def edit_inventory(request, id):
    if request.method != "POST":
        return JsonResponse({'message': 'Wrong method.'}, status=400)

    try:
        p = Product.objects.get(id=id)
        data = JSONParser().parse(request)
        number = data['amount']
        print(number)
        if number >= 0:
            p.increase_inventory(amount=number)
        if number < 0:
            number = number * -1
            try:
                p.decrease_inventory(amount=number)
            except:
                message = '{"message": "Not enough inventory"}'
                errormsg = json.loads(message)
                return JsonResponse(errormsg, status=400)

        p = Product.objects.get(id=id)
        serializer = ProductSerializer(p)
        return JsonResponse(serializer.data, safe=False, status=200)
    except:
        message = '{"message": "Product Not Found."}'
        errormsg = json.loads(message)
        return JsonResponse(errormsg, status=404)


@csrf_exempt
def watch_orders(request):
    if request.method != 'GET':
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    if not request.user.is_authenticated or not request.user.is_active:
        return JsonResponse({'message': 'you have to login'}, status=403)
    try:
        order = Order.initiate(request.user.customer)
    except:
        order = Order.objects.get(customer_id=request.user.customer.id, status=1)

    orderrow = OrderRow.objects.filter(order_id=order.id)
    items = []
    for i in orderrow:
        cart = {
            "code": i.product.code,
            "name": i.product.name,
            "price": i.product.price,
            "amount": i.amount
        }
        items.append(cart)
    return JsonResponse({"total_price": order.total_price, "items": items}, status=200)


@csrf_exempt
def add_items(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    if not request.user.is_authenticated or not request.user.is_active:
        return JsonResponse({'message': 'you have to login'}, status=403)
    try:
        data = JSONParser().parse(request)
    except:
        return JsonResponse({"message": "wrong format"}, status=404)
    try:
        order = Order.initiate(request.user.customer)
    except:
        order = Order.objects.get(customer_id=request.user.customer.id, status=1)
    orderrow = OrderRow.objects.filter(order_id=order.id)
    errors = []
    for i in data:
        if 'code' in i and 'amount' not in i:
            errors.append({'code': i['code'],
                           'message': 'Item has no "amount" property.'})
            continue
        if 'code' not in i:
            errors.append({'code': '?',
                           'message': 'Item has no "code" property.'})
            continue
        try:
            if Product.objects.filter(code=i['code']).exists():
                order.add_product(Product.objects.get(code=i['code']), i['amount'])
            else:
                raise Exception('we dont have this product dude')
        except Exception as e:
            errors.append({'code': i['code'], 'message': str(e)})
    items = []
    for i in orderrow:
        cart = {
            "code": i.product.code,
            "name": i.product.name,
            "price": i.product.price,
            "amount": i.amount
        }
        items.append(cart)
    if errors:
        return JsonResponse({"total price": order.total_price, "errors": errors, "items": items}, status=400)
    else:
        return JsonResponse({"total price": order.total_price, "items": items}, status=200)


@csrf_exempt
def remove_items(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    if not request.user.is_authenticated or not request.user.is_active:
        return JsonResponse({'message': 'you have to login'}, status=403)
    try:
        data = JSONParser().parse(request)
    except:
        return JsonResponse({"message": "wrong format"}, status=404)
    try:
        order = Order.initiate(request.user.customer)
    except:
        order = Order.objects.get(customer_id=request.user.customer.id, status=1)
    orderrow = OrderRow.objects.filter(order_id=order.id)
    errors = []
    for i in data:
        if 'code' in i and 'amount' not in i:
            amount = None
        if 'code' in i and 'amount' in i:
            amount = i['amount']
        if 'code' not in i:
            errors.append({'code': '?',
                           'message': 'Item has no "code" property.'})
            continue
        try:
            if Product.objects.filter(code=i['code']).exists():
                order.remove_product(Product.objects.get(code=i['code']), amount=amount)
            else:
                raise Exception('we dont have this product dude')
        except Exception as e:
            errors.append({'code': i['code'], 'message': str(e)})
    items = []
    for i in orderrow:
        cart = {
            "code": i.product.code,
            "name": i.product.name,
            "price": i.product.price,
            "amount": i.amount
        }
        items.append(cart)
    if errors:
        return JsonResponse({"total price": order.total_price, "errors": errors, "items": items}, status=400)
    else:
        return JsonResponse({"total price": order.total_price, "items": items}, status=200)


@csrf_exempt
def submit(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Wrong method.'}, status=400)
    if not request.user.is_authenticated or not request.user.is_active:
        return JsonResponse({'message': 'you have to login'}, status=403)
    try:
        data = JSONParser().parse(request)
    except:
        return JsonResponse({"message": "wrong format"}, status=404)
    if len(data) > 0:
        raise Exception("")
    else:
        try:
            order = Order.objects.get(customer_id=request.user.customer.id, status=1)
            orderrow = OrderRow.objects.filter(order_id=order.id)
            items = []
            for i in orderrow:
                cart = {
                    "code": i.product.code,
                    "name": i.product.name,
                    "price": i.product.price,
                    "amount": i.amount
                }
                items.append(cart)
            order.submit()
            return JsonResponse({"id": order.id, "order_time": order.order_time, "status": "submitted"
                                    , "total_price": order.total_price, "rows": items})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)
