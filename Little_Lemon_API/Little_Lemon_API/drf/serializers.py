from rest_framework import serializers
from .models import Menuitem,Order,Orderitem,Cart,Category
from django.contrib.auth.models import User,Group
from decimal import Decimal
class Category_serializers(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = '__all__' 
        
class Menuitem_serializers(serializers.ModelSerializer):
    
    category = Category_serializers(read_only = True)
    category_id = serializers.IntegerField(write_only = True)
    class Meta:
        model = Menuitem
        fields = ['id',"title","price","featured",'category_id','category' ]

class Menuitem_serializers_readonly(serializers.ModelSerializer):
    
    class Meta:
        model = Menuitem
        fields = ['id',"title" ]

class User_serializers(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only = True)
    
    class Meta:
        model = User
        fields = ["id","username","email","password"]

class cart_serializers(serializers.ModelSerializer):
    
    price = serializers.SerializerMethodField(method_name='price_cal')
    unit_price = serializers.ReadOnlyField(source='menuitem.price')
    menuitem_view = Menuitem_serializers_readonly(source="menuitem", read_only=True)
    menuitem = serializers.PrimaryKeyRelatedField(queryset=Menuitem.objects.all()) 
    
    class Meta:
        model = Cart
        fields  = ['user','menuitem','menuitem_view','quantity','unit_price','price']
        read_only_fields = ['unit_price', 'price','menuitem','user']
    
    def price_cal(self,product:Cart):
        return product.quantity * Decimal(product.menuitem.price)
    
    def create(self, validated_data):
        menuitem = validated_data['menuitem']
        validated_data['unit_price'] = menuitem.price  
        validated_data['price'] = validated_data['quantity'] * menuitem.price
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user 
        return super().create(validated_data)

class Order_serializers(serializers.ModelSerializer):
    
    # delivery_crew = serializers.IntegerField(write_only = True)
    delivery_crew = User_serializers(read_only=True)
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    date = serializers.DateField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id','user','delivery_crew','status','total','date']
        read_only_fileds = ['id', 'user', 'total', 'date']
        
class Orderitem_serializers(serializers.ModelSerializer):
    
    class Meta:
        model = Orderitem
        fields = "__all__"
        