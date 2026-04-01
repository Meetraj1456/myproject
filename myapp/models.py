from django.db import models

# Create your models here.


class User(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=50, unique=True)
    phone_no = models.IntegerField()
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Contact(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=10)
    phno = models.IntegerField()
    sub = models.CharField(max_length=30)
    msg = models.CharField(max_length=100)


class Categories(models.Model):
    name = models.CharField(max_length=15)
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return self.name


class Add_product(models.Model):
    categories_id = models.ForeignKey(Categories, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=1000)
    price = models.IntegerField()
    qty = models.IntegerField()
    img = models.ImageField(upload_to='pictures/')

    def __str__(self):
        return self.name


class Add_to_cart(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    pid = models.ForeignKey(Add_product, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    qty = models.IntegerField()
    img = models.ImageField(upload_to='pictures/')
    total_price = models.IntegerField()


class Wishlist(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    pid = models.ForeignKey(Add_product, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=50)
    img = models.ImageField(upload_to='pictures/')
    price = models.IntegerField()


class Address(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    address = models.CharField(max_length=50)
    country = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zip_code = models.IntegerField()


class Order(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    sub_total = models.IntegerField(default=0)
    shipping = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)
    payment_id = models.CharField(max_length=100, blank=True)
    payment_order_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='paid')
    items_json = models.JSONField(default=list)

    def __str__(self):
        return f"Order #{self.id}"

    @property
    def order_number(self):
        """Generate formatted order number like ORD-2026-00016"""
        year = self.created_at.year
        return f"ORD-{year}-{str(self.id).zfill(5)}"
