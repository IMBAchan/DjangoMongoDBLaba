# views.py
import os
import re
import sqlite3
import json
from django.shortcuts import render
from django.shortcuts import reverse
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.apps import apps
from django.db.models import Prefetch, Sum
from django.templatetags.static import static
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Product, PickupPoint, Client, Order, DiscountCard, Supplier
from django.http import HttpResponse
from django.templatetags.static import static
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt  # Імпортуємо для обходу CSRF
from django.shortcuts import redirect
from decimal import Decimal

# Підключення до MongoDB
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "laba6store"

from pymongo import MongoClient
from bson import ObjectId, Decimal128

def all_records_view(request):
    # Отримуємо всі моделі
    app_models = apps.get_app_config('laba6').get_models()
    
    # Словник для зберігання даних
    tables_data = {}

    for model in app_models:
        if model._meta.db_table.startswith('laba6_'):
            # Отримуємо назву таблиці без префіксу
            table_name = model._meta.db_table[len('laba6'):]

            # Отримуємо всі записи з моделі
            records = model.objects.all()

            # Додаємо назву таблиці та записи до словника
            tables_data[table_name] = records

    # Генеруємо HTML-контент
    html_content = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <title>All tables</title>
            <link rel="stylesheet" type="text/css" href="{static('laba6/styles/styles.css')}">
        </head>
        <body>
    """

    for table_name, records in tables_data.items():
        # Замінюємо "_" на " " і робимо перші букви великими
        formatted_table_name = table_name.replace('_', ' ').title()
        html_content += f"<h2>Table: {formatted_table_name}</h2>"
        html_content += "<table border='1'><tr>"

        # Отримуємо заголовки стовпців
        columns = [field.name for field in records.model._meta.fields]
        for column in columns:
            formatted_column_name = column.replace('_', ' ').title()  # Форматуємо назву стовпця
            html_content += f"<th>{formatted_column_name}</th>"
        html_content += "</tr>"

        # Виводимо записи
        for record in records:
            html_content += "<tr>"
            for column in columns:
                value = getattr(record, column, 'N/A')  # Отримуємо значення або 'N/A'
                html_content += f"<td>{value}</td>"
            html_content += "</tr>"
        html_content += "</table>"

    html_content += """
        </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')

def upload_sql_file_view(request):
    if request.method == 'POST':
        sql_file = request.FILES.get('sql_file')

        if sql_file:
            # Зберігаємо файл у тимчасовому місці
            temp_file_path = os.path.join(settings.MEDIA_ROOT, sql_file.name)

            # Переконайтесь, що директорія існує
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            with open(temp_file_path, 'wb+') as destination:
                for chunk in sql_file.chunks():
                    destination.write(chunk)

            # Виконуємо SQL запити
            connection = sqlite3.connect(settings.DATABASES['default']['NAME'])  # Ваша база даних
            cursor = connection.cursor()

            with open(temp_file_path, 'r') as f:
                sql_script = f.read()

                # Додаємо префікс laba6_ до назв таблиць
                sql_script = re.sub(r'\b(DiscountCard|Director|Client|Employee|Warehouse|Supplier|Product|Store|DeliveryService|PickupPoint|Manufacturer|Order)\b', r'laba6_\1', sql_script)

                # Розділяємо запити та обробляємо їх
                for statement in sql_script.split(';'):
                    statement = statement.strip()
                    if statement:  # Перевірка на пусті рядки
                        try:
                            # Замінюємо записи у таблицях
                            if statement.startswith('INSERT INTO'):
                                # Отримуємо назву таблиці
                                table_name = re.search(r'INSERT INTO (.+?) ', statement).group(1).strip()
                                table_name = f"{table_name}"

                                # Видаляємо всі записи з таблиці
                                cursor.execute(f'DELETE FROM {table_name};')

                            cursor.execute(statement)  # Виконуємо запит
                        except sqlite3.OperationalError as e:
                            print(f'Error executing statement: {statement} - {str(e)}')  # Виводимо помилку
                            continue  # Продовжуємо до наступного запиту
                        except sqlite3.IntegrityError as e:
                            print(f'Error executing statement: {statement} - {str(e)}')  # Виводимо помилку при конфлікті

                connection.commit()

            # Видаляємо тимчасовий файл
            os.remove(temp_file_path)
            return HttpResponse('SQL file processed successfully.')

    return render(request, 'laba6/upload_sql.html')

def home_view(request):
    return render(request, 'laba6/home.html')

def all_products_view(request):
    # Отримуємо всі продукти
    products = Product.objects.all()
    # Передаємо продукти в шаблон
    return render(request, 'laba6/all_products.html', {'products': products})


def place_order(request):
    article = request.GET.get('article', None)

    if article:
        try:
            product = Product.objects.get(article=article)
            pickup_points = PickupPoint.objects.all()

            html_content = f"""
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Деталі Продукту</title>
                    <link rel="stylesheet" type="text/css" href="{static('laba6/styles/styles.css')}">
                    <link rel="stylesheet" type="text/css" href="{static('laba6/styles/place_order.css')}">
                </head>
                <body>
                    <h1>Product details</h1>
                    <h2>Your order</h2>
                    <div class="product-order">
                        <div class="product">
                            <div class="image-placeholder">Image Placeholder</div>
                            <h2 class="name">{product.name}</h2>
                            <p class="supplier">Supplier: {product.supplier}</p>
                            <p class="price">Price: ${product.price}</p>
                            <p class="description">{product.description}</p>
                        </div>
                        <div class="order-info">
                            <form action="/confirm-order/{product.article}/" method="post">
                                <input type="hidden" name="article" value="{product.article}">
                                <div>
                                    <label for="client-name">Client:</label>
                                    <input type="text" id="client-name" name="client_name" required>
                                </div>
                                <div>
                                    <label for="phone_number">Phone:</label>
                                    <input type="text" id="phone_number" name="phone_number">
                                </div>
                                <div>
                                    <label for="email">Email:</label>
                                    <input type="email" id="email" name="email">
                                </div>
                                <div>
                                    <label for="email">Delivery method:</label>
                                    <input type="text" id="delivery_method" name="delivery_method">
                                </div>
                                <div>
                                    <label for="payment-method">Payment Method:</label>
                                    <select id="payment-method" name="payment_method" required>
                                        <option value="Cash">Cash</option>
                                        <option value="Credit Card">Credit Card</option>
                                        <option value="PayPal">PayPal</option>
                                    </select>
                                </div>
                                <div>
                                    <label for="pickup-checkbox">Pickup?</label>
                                    <input type="checkbox" id="pickup-checkbox" name="pickup_checkbox">
                                </div>
                                <div>
                                    <label for="pickup-point">Pickup Point:</label>
                                    <select id="pickup-point" name="pickup_point">
                                        <option value="">Select a pickup point</option>
            """
            for point in pickup_points:
                html_content += f'<option value="{point.pickup_point_id}">{point.address}</option>'

            html_content += f"""
                                    </select>
                                </div>
                                <button type="submit" class="buy-button">Confirm order</button>
                            </form>
                        </div>
                    </div>
                </body>
            </html>
            """
            return HttpResponse(html_content, content_type='text/html')

        except Product.DoesNotExist:
            return HttpResponse("Товар не знайдено", status=404)
    else:
        return HttpResponse("Не вказано article", status=400)

@csrf_exempt  # Для тестування без CSRF токена
def confirm_order(request, article):
    if request.method == "POST":
        try:
            product = Product.objects.get(article=article)
        except Product.DoesNotExist:
            return HttpResponse("Товар не знайдено", status=404)

        client_name = request.POST.get('client_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        payment_method = request.POST.get('payment_method')
        delivery_method = request.POST.get('delivery_method')
        pickup_checkbox = request.POST.get('pickup_checkbox')
        pickup_point = request.POST.get('pickup_point')

        # Знайти або створити клієнта за ім'ям
        client, created = Client.objects.get_or_create(
            full_name=client_name,
            defaults={
                'phone_number': phone_number,
                'email': email
            }
        )

        # Застосування знижки з картки
        discount = 0
        if client.discount_card_number:  # Якщо у клієнта є картка зі знижкою
            discount = client.discount_card_number.discount_amount

        # Логіка доставки
        if pickup_checkbox and pickup_point:
            delivery_method = "Pickup"
        elif not pickup_checkbox and not delivery_method:
            return HttpResponse("It is necessary to specify the method of delivery", status=400)

        # Розрахунок фінальної ціни з урахуванням знижки
        if isinstance(discount, Decimal128):
            discount_decimal = discount.to_decimal()
        else:
            discount_decimal = Decimal(discount)  # Якщо discount звичайне число, просто конвертуємо

        # Конвертуємо product.price з Decimal128 до decimal.Decimal
        price_decimal = product.price.to_decimal()

        # Обчислення фінальної ціни
        final_price = price_decimal * (Decimal(1) - discount_decimal / Decimal(100))

        # Генеруємо замовлення
        order = Order(
            order_date=timezone.now(),
            order_amount=final_price,  # Ціна продукту з урахуванням знижки
            payment_method=payment_method,
            client=client,
            delivery_method=delivery_method,
            responsible_employee_id=1,
            product=product
        )
        order.save()

        return redirect('order_confirmation', order_id=order.order_id)

    return HttpResponse("The method is not supported", status=405)

def order_confirmation(request, order_id):
    order = Order.objects.get(order_id=order_id)
    return HttpResponse(f"Thank you for your order! Your order ID: {order.order_id}")

@require_http_methods(["GET", "DELETE"])
def list_and_delete_suppliers(request):
    suppliers = Supplier.objects.all()

    if request.method == "DELETE":
        body = json.loads(request.body)
        supplier_id = body.get('supplier_id')

        if supplier_id:
            supplier = get_object_or_404(Supplier, supplier_id=supplier_id)
            supplier.delete()
            return JsonResponse({'status': 'success'})

    return render(request, 'laba6/supplier_list.html', {'suppliers': suppliers})


@csrf_exempt
def update_client(request):
    clients = Client.objects.all()
    discount_cards = DiscountCard.objects.all()

    html_content = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <title>Update Client Details</title>
            <link rel="stylesheet" type="text/css" href="{static('laba6/styles/styles.css')}">
        </head>
        <body>
            <h1>Update Client</h1>
            <form action="{reverse('perform_update_client')}" method="post">
                <div>
                    <label for="client-id">Select Client:</label>
                    <select id="client-id" name="client_id" required>
                        <option value="">Select a client</option>
    """
    for client in clients:
        html_content += f'<option value="{client.client_id}">{client.full_name}</option>'

    html_content += """
                    </select>
                </div>
                <div>
                    <label for="client-name">Client Name:</label>
                    <input type="text" id="client-name" name="client_name" required>
                </div>
                <div>
                    <label for="phone_number">Phone:</label>
                    <input type="text" id="phone_number" name="phone_number">
                </div>
                <div>
                    <label for="email">Email:</label>
                    <input type="email" id="email" name="email">
                </div>
                <div>
                    <label for="discount-card">Discount Card:</label>
                    <select id="discount-card" name="discount_card">
                        <option value="">No discount card</option>
    """
    for card in discount_cards:
        html_content += f'<option value="{card.discount_card_number}">Card {card.discount_card_number}: {card.discount_amount}%</option>'

    html_content += """
                    </select>
                </div>
                <button type="submit" class="update-button">Update Client</button>
            </form>
        </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')

@csrf_exempt
def perform_update_client(request):
    if request.method == "POST":
        client_id = request.POST.get('client_id')
        client_name = request.POST.get('client_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        discount_card_id = request.POST.get('discount_card')

        client = Client.objects.get(client_id=client_id)
        client.full_name = client_name
        client.phone_number = phone_number
        client.email = email
        client.discount_card_number_id = discount_card_id if discount_card_id else None
        client.save()

        return HttpResponse("Client updated successfully!")
    return HttpResponse("Method not allowed", status=405)

def load_records_view(request):
    method = int(request.GET.get('method', 1))
    html_content = f"""
    <html>
        <head>
            <meta charset="UTF-8">
            <title>Loading Strategies</title>
            <link rel="stylesheet" type="text/css" href="{static('laba6/styles/styles.css')}">
        </head>
        <body>
    """

    # Lazy Loading (method=1)
    if method == 1:
        orders = Order.objects.all()
        html_content += "<h2>Lazy Loading</h2>"
        html_content += "<table border='1'><tr><th>Order ID</th><th>Order Date</th><th>Order Amount</th><th>Client</th><th>Product</th></tr>"
        for order in orders:
            client_name = order.client.full_name if order.client else "No client"
            product_name = order.product.name if order.product else "No product"
            html_content += f"<tr><td>{order.order_id}</td><td>{order.order_date}</td><td>{order.order_amount}</td><td>{client_name}</td><td>{product_name}</td></tr>"
        html_content += "</table>"

    # Eager Loading (method=2)
    elif method == 2:
        orders = Order.objects.select_related('client', 'product')
        html_content += "<h2>Eager Loading</h2>"
        html_content += "<table border='1'><tr><th>Order ID</th><th>Order Date</th><th>Order Amount</th><th>Client</th><th>Product</th></tr>"
        for order in orders:
            client_name = order.client.full_name if order.client else "No client"
            product_name = order.product.name if order.product else "No product"
            html_content += f"<tr><td>{order.order_id}</td><td>{order.order_date}</td><td>{order.order_amount}</td><td>{client_name}</td><td>{product_name}</td></tr>"


    # Explicit Loading (method=3)
    elif method == 3:
        orders = Order.objects.all()

        products = Product.objects.filter(order__in=orders)

        html_content += "<h2>Explicit Loading</h2>"
        html_content += "<table border='1'><tr><th>Order ID</th><th>Order Date</th><th>Order Amount</th><th>Client</th><th>Product</th></tr>"
        for order in orders:
            client_name = order.client.full_name if order.client else "No client"
            order_products = products.filter(order=order)
            for product in order_products:
                html_content += f"<tr><td>{order.order_id}</td><td>{order.order_date}</td><td>{order.order_amount}</td><td>{client_name}</td><td>{product.name}</td></tr>"
        html_content += "</table>"

    # Aggregation / Sorting / Filtering Query (method=4)
    elif method == 4:
        clients = Client.objects.annotate(total_spent=Sum('order__order_amount')).order_by('-total_spent')
        html_content += "<h2>Client Spend Summary</h2>"
        html_content += "<table border='1'><tr><th>Client</th><th>Total Spent</th></tr>"
        for client in clients:
            html_content += f"<tr><td>{client.full_name}</td><td>{client.total_spent or 0}</td></tr>"
        html_content += "</table>"

    # Closing HTML tags
    html_content += """
        </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')



def load_records_dif(request):
    return render(request, 'laba6/load_records_dif.html')


def serialize_mongo_objects(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, Decimal128):
        return float(obj.to_decimal())
    elif isinstance(obj, dict):
        return {k: serialize_mongo_objects(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_mongo_objects(item) for item in obj]
    return obj

@csrf_exempt
def get_clients(request):
    if request.method == "GET":
        try:
            # Підключення
            client = MongoClient(MONGO_URI)
            db = client[DATABASE_NAME]
            collection = db.laba6_client  

            # Виконання запиту
            pipeline = [
                {
                    "$lookup": {
                        "from": "laba6_discountcard",
                        "localField": "discount_card_number_id",
                        "foreignField": "discount_card_number",
                        "as": "discount_card" 
                    }
                },
                {
                    "$unwind": {
                        "path": "$discount_card", 
                        "preserveNullAndEmptyArrays": True 
                    }
                },
                {
                    "$project": {
                        "client_id": 1,
                        "full_name": 1,
                        "phone_number": 1,
                        "email": 1,
                        "discount_card.discount_amount": 1,
                        "discount_card_number_id": 1
                    }
                }
            ]

            result = list(collection.aggregate(pipeline))
            serialized_result = serialize_mongo_objects(result)
            return JsonResponse(serialized_result, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only GET method is allowed"}, status=405)

def get_products(request):
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db.laba6_product

        # Виконання запиту
        pipeline = [
            {
                "$lookup": {
                    "from": "laba6_supplier",
                    "localField": "supplier_id",
                    "foreignField": "supplier_id",
                    "as": "supplier_info"
                }
            },
            {
                "$lookup": {
                    "from": "laba6_warehouse",
                    "localField": "warehouse_id",
                    "foreignField": "warehouse_id",
                    "as": "warehouse_info"
                }
            },
            {
                "$unwind": {
                    "path": "$supplier_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$unwind": {
                    "path": "$warehouse_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "article": 1,
                    "name": 1,
                    "price": 1,
                    "description": 1,
                    "supplier_info.supplier_id": 1,  
                    "supplier_info.name": 1, 
                    "warehouse_info.warehouse_id": 1,
                    "warehouse_info.address": 1
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        serialized_result = serialize_mongo_objects(result)
        return JsonResponse(serialized_result, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def get_orders(request):
    try:
        # Підключення до MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db.laba6_order

        pipeline = [
            {
                "$lookup": {
                    "from": "laba6_client",
                    "localField": "client_id",  
                    "foreignField": "client_id",
                    "as": "client_info"
                }
            },
            {
                "$lookup": {
                    "from": "laba6_employee",
                    "localField": "responsible_employee_id", 
                    "foreignField": "employee_id",  
                    "as": "employee_info"
                }
            },
            {
                "$lookup": {
                    "from": "laba6_product",
                    "localField": "product_id",
                    "foreignField": "article",
                    "as": "product_info"
                }
            },
            {
                "$unwind": {
                    "path": "$client_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$unwind": {
                    "path": "$employee_info",
                    "preserveNullAndEmptyArrays": True 
                }
            },
            {
                "$unwind": {
                    "path": "$product_info",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "order_id": 1,
                    "order_date": 1,  
                    "order_amount": 1,
                    "payment_method": 1,
                    "delivery_method": 1,
                    "client_info.client_id": 1,
                    "client_info.full_name": 1,
                    "client_info.phone_number": 1,
                    "employee_info.employee_id": 1,
                    "employee_info.full_name": 1,
                    "employee_info.position": 1,
                    "product_info.article": 1,
                    "product_info.name": 1,
                    "product_info.price": 1
                }
            }
        ]

        result = list(collection.aggregate(pipeline))
        serialized_result = serialize_mongo_objects(result)
        return JsonResponse(serialized_result, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)