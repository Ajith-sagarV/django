from django.contrib import admin
from .models import Menuitem,Order,Orderitem,Cart,Category
# Register your models here.

admin.site.register(Category)
admin.site.register(Menuitem)
admin.site.register(Order)
admin.site.register(Orderitem)
admin.site.register(Cart)
