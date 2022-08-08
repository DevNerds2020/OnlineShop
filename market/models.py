import datetime
from django.db import models
from django.contrib.auth.models import User
from accounts.models import Customer


class Product(models.Model):
    code = models.CharField(max_length=10, unique=True, primary_key=False)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    inventory = models.PositiveIntegerField(default=0)

    def increase_inventory(self, amount):
        self.inventory += amount
        self.save()

    def decrease_inventory(self, amount):
        self.inventory -= amount
        if self.inventory < 0:
            raise ValueError("موجودی منفی قابل قبول نیست")
        else:
            self.save()


class OrderRow(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey('Order', on_delete=models.PROTECT)
    amount = models.IntegerField()


class Order(models.Model):
    # Status values. DO NOT EDIT
    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4
    status_choices = (
        (STATUS_SHOPPING, 'در حال خرید'),
        (STATUS_SUBMITTED, 'ثبت‌شده'),
        (STATUS_CANCELED, 'لغوشده'),
        (STATUS_SENT, 'ارسال‌شده'),
    )
    customer = models.ForeignKey('accounts.Customer', on_delete=models.PROTECT)
    order_time = models.DateTimeField()
    total_price = models.IntegerField(default=0)
    status = models.IntegerField(choices=status_choices)

    @staticmethod
    def initiate(customer):
        v = Order.objects.filter(customer=customer)
        sit = 0
        for i in v:
            if i.status == 1:
                sit = 1
        if sit == 0:
            o = Order(customer=customer, order_time=datetime.datetime.now(), status=1)
            o.save()
            return o
        else:
            raise OverflowError('a customer can only have one order in status 1')

    def add_product(self, product, amount):
        try:
            o = OrderRow.objects.get(product=product, order=self)
        except:
            o = OrderRow(product=product, order=self, amount=0)
        o.amount += amount
        if 0 < o.amount <= o.product.inventory:
            self.total_price += o.product.price * amount
            self.save()
            o.save()
        else:
            raise ValueError('we dont have enough')

    def remove_product(self, product, amount=None):
        oramount = OrderRow.objects.get(product=product, order=self).amount
        if amount is None:
            OrderRow.objects.filter(product=product, order=self).delete()
            self.total_price = self.total_price - (product.price * oramount)
        else:
            namount = amount
            amount = oramount - amount
            if amount == 0:
                OrderRow.objects.filter(product=product, order=self).delete()
            else:
                OrderRow.objects.filter(product=product, order=self).update(amount=amount)
            self.total_price = self.total_price - (product.price * namount)
        self.save()

    def submit(self):
        if self.total_price == 0:
            raise ValueError('cant submit empty orders')

        if self.customer.balance > self.total_price and self.status == 1:
            self.total_price = 0
            o = OrderRow.objects.filter(order_id=self.id)
            for i in o:
                p = Product.objects.get(id=i.product_id)
                p.inventory = p.inventory - i.amount
                p.save()
                self.total_price += (i.amount * p.price)
            self.customer.spend(self.total_price)
            self.status = 2
            self.save()
        else:
            raise ValueError('you dont have enough money')

    def cancel(self):
        if self.status == 2 and self.status != 4:
            o = OrderRow.objects.filter(order_id=self.id)
            for i in o:
                p = Product.objects.get(id=i.product_id)
                p.inventory = p.inventory + i.amount
                p.save()
            self.customer.deposit(self.total_price)
            self.status = 3
            self.save()
        else:
            raise ValueError('when send cant be canceld')

    def send(self):
        if self.status == 2:
            self.status = 4
            self.save()
        else:
            raise ValueError('must be submitted')
