from django.db import models

class DiscountCard(models.Model):
    discount_card_number = models.AutoField(primary_key=True)  # Change to AutoField
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Card {self.discount_card_number}: {self.discount_amount}%"

class Director(models.Model):
    director_id = models.AutoField(primary_key=True)  # Change to AutoField
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    ownership_object = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.full_name

class Client(models.Model):
    client_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    discount_card_number = models.ForeignKey(DiscountCard, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.full_name

class Employee(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    
    employee_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    passport_data = models.CharField(max_length=50, blank=True, null=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)

    def __str__(self):
        return self.full_name

class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)  # Change to AutoField
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.address

class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)  # Change to AutoField
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Product(models.Model):
    article = models.AutoField(primary_key=True)  # Change to AutoField
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    order_date = models.DateTimeField()
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    delivery_method = models.CharField(max_length=50, blank=True, null=True)
    responsible_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Order {self.order_id}"


class Store(models.Model):
    store_id = models.AutoField(primary_key=True)  # Change to AutoField
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    employee_count = models.IntegerField()

    def __str__(self):
        return self.name

class DeliveryService(models.Model):
    delivery_service_id = models.AutoField(primary_key=True)  # Change to AutoField
    name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

class PickupPoint(models.Model):
    pickup_point_id = models.AutoField(primary_key=True)  # Change to AutoField
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.address

class Manufacturer(models.Model):
    manufacturer_id = models.AutoField(primary_key=True)  # Change to AutoField
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class StoreProduct(models.Model):
    store = models.ForeignKey('Store', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('store', 'product')
        db_table = 'store_product'

class DeliveryServiceProduct(models.Model):
    delivery_service = models.ForeignKey('DeliveryService', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('delivery_service', 'product')
        db_table = 'delivery_service_product'

class PickupPointEmployee(models.Model):
    pickup_point = models.ForeignKey('PickupPoint', on_delete=models.CASCADE)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('pickup_point', 'employee')
        db_table = 'pickup_point_employee'
