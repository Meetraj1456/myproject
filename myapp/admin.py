from django.contrib import admin
from . models import *
# Register your models here.


class CategoriesAdmin(admin.ModelAdmin):
    list_display = ['name', 'image']
    fields = ['name', 'image']


admin.site.register(User)
admin.site.register(Contact)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Add_product)
admin.site.register(Add_to_cart)
admin.site.register(Wishlist)
admin.site.register(Address)
admin.site.register(Order)
