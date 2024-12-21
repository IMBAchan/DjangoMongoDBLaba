import os
import django

# Вказуємо налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dbproj.settings')
django.setup()

import json
from laba6.models import Director, Client, Employee, Warehouse, Supplier, Product, Order, Store, DeliveryService, PickupPoint, Manufacturer
from django.db import IntegrityError

def load_data():
    # Шлях до вашої папки з JSON файлами
    json_folder_path = fr'C:/Users/Acer/Desktop/laba6mongo/dbproj/exports/'

    # Список моделей у порядку завантаження
    models_list = [
        ('director', Director),
        ('client', Client),
        ('employee', Employee),
        ('warehouse', Warehouse),
        ('supplier', Supplier),
        ('product', Product),
        ('order', Order),
        ('store', Store),
        ('deliveryservice', DeliveryService),
        ('pickuppoint', PickupPoint),
        ('manufacturer', Manufacturer)
    ]
    
    # Проходимо через кожну модель і завантажуємо її дані
    for model_name, model_class in models_list:
        json_file_path = f'{json_folder_path}{model_name}.json'
        
        try:
            # Відкриваємо і завантажуємо дані з JSON файлу
            with open(json_file_path, 'r') as file:
                data = json.load(file)
            
            for entry in data:
                model_data = entry['fields']
                # Спробуємо створити або оновити запис
                try:
                    model_class.objects.update_or_create(
                        pk=entry['pk'], 
                        defaults=model_data
                    )
                    print(f"{model_class.__name__}: {entry['pk']} додано або оновлено.")
                except IntegrityError as e:
                    print(f"Помилка при збереженні {model_class.__name__} з pk {entry['pk']}: {e}")
        except FileNotFoundError:
            print(f"Файл {model_name}.json не знайдено.")
        except json.JSONDecodeError:
            print(f"Помилка при декодуванні JSON у файлі {model_name}.json.")

# Викликаємо функцію для завантаження даних
load_data()
