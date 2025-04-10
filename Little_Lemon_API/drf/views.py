from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.views import APIView
from rest_framework import generics,status,permissions,response,filters
from django.contrib.auth.models import Group,User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Menuitem,Category,Cart,Order,Orderitem
from django.http import HttpRequest
from .serializers import Menuitem_serializers,Category_serializers,User_serializers,cart_serializers,Order_serializers,Orderitem_serializers
from django.utils import timezone
from django.db import transaction,IntegrityError
from decimal import Decimal

class Menu_items_view(generics.ListCreateAPIView,generics.DestroyAPIView):
    
    request = HttpRequest
    queryset = Menuitem.objects.all()
    serializer_class = Menuitem_serializers
    search_fields = ['title', 'category__title']
    ordering_fields = ['price', 'title'] 
    
    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            if self.request.user.groups.filter(name="Manager").exists():
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You don't have permission to view content.",status.HTTP_403_FORBIDDEN)
        if self.request.method == 'GET':
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if (set(user_groups) & {"Manager", "Delivery crew"} or not user_groups):
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You don't have permission to view content.")
        if self.request.method ==  "DELETE":
            if not self.request.user.groups.filter(name  = 'Manager').exists():
                raise PermissionDenied("You don't have permission to delete.",status.HTTP_403_FORBIDDEN)
            else:
                return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
        
class Menu_items_single_view(generics.RetrieveDestroyAPIView,generics.RetrieveUpdateAPIView):
    
    request = HttpRequest
    queryset = Menuitem
    serializer_class = Menuitem_serializers

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            if self.request.user.groups.filter(name="Manager").exists():
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You don't have permission to view content.",status.HTTP_403_FORBIDDEN)
        if self.request.method == 'GET':
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if (set(user_groups) & {"Manager", "Delivery crew"} or not user_groups):
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You don't have permission to view content.")
        if self.request.method ==  "DELETE":
            if not self.request.user.groups.filter(name  = 'Manager').exists():
                raise PermissionDenied("You don't have permission to delete.",status.HTTP_403_FORBIDDEN)
            else:
                return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
class Category_view(generics.ListCreateAPIView):
    
    request = HttpRequest
    queryset = Category.objects.all()
    serializer_class = Category_serializers
    
    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            if self.request.user.groups.filter(name="Manager").exists():
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You don't have permission to view content.",status.HTTP_403_FORBIDDEN)
        if self.request.method == 'GET':
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if (set(user_groups) & {"Manager", "Delivery crew"} or not user_groups):
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You don't have permission to view content.")
        if self.request.method ==  "DELETE":
            if not self.request.user.groups.filter(name  = 'Manager').exists():
                raise PermissionDenied("You don't have permission to delete.",status.HTTP_403_FORBIDDEN)
            else:
                return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

class Category_single_view(generics.RetrieveDestroyAPIView,generics.RetrieveUpdateAPIView):
    
    request = HttpRequest
    queryset = Category.objects.all()
    serializer_class = Category_serializers
    
    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            if self.request.user.groups.filter(name="Manager").exists():
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You do not have permission to modify menu items.",status.HTTP_403_FORBIDDEN)
        if self.request.method  == 'GET':
            user_groups = self.request.user.groups.values_list('name', flat=True)
            if (set(user_groups) & {"Manager", "Delivery crew"} or not user_groups):
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You do not have permission to modify menu items.")
        if self.request.method ==  "DELETE":
            if not self.request.user.groups.filter(name  = 'Manager').exists():
                raise PermissionDenied("You don't have permission to delete.",status.HTTP_403_FORBIDDEN)
            else:
                return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
class Manager_assignment(generics.ListCreateAPIView,generics.DestroyAPIView):
    
    request = HttpRequest
    queryset = User.objects.all()
    serializer_class = User_serializers
    
    def get_permissions(self):
        if self.request.method in ['GET','POST','DELETE']:
            if not self.request.user.groups.filter(name = 'Manager').exists():
                raise PermissionDenied("You are not authorized to view the content",403)
            return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        return User.objects.filter(groups__name = 'Manager')
    
    def post(self,request, *args, **kwargs):
        
        username = request.data.get("username",None)
        manager_group  = get_object_or_404(Group,name='Manager')
        
        if username:
            username  =  get_object_or_404(User,username=username)
            
            if manager_group.user_set.filter(username=username).exists():
                return Response({"message":f"{username} is already part of Manager group"})
            
            manager_group.user_set.add(username)
            managers = User.objects.filter(groups__name="Manager").values("id","username","email")
            return Response({"message":f"{username} added to admin group",
                            "managers":managers},201)
        
        else:
            return Response({"message":"Missing 'username' in the payload"})
        
    def delete(self,request,username, *args, **kwargs):
        
        manager_group  = get_object_or_404(Group,name='Manager')
        if username:
            if username.isdigit():
                username = get_object_or_404(User, id=int(username))
            else:
                username = get_object_or_404(User, username=username)
            
            if not manager_group.user_set.filter(username=username).exists():
                return Response({"message":f"{username} is not part of Manager group"})
            else:
                manager_group.user_set.remove(username)
                return Response({"message":f"{username} has been removed from manager group"},200)
        else:
            return Response({"message":"provide username/id in the path"})
            
class Delivery_assignment(generics.ListAPIView,generics.DestroyAPIView):
    
    request =  HttpRequest
    queryset = User.objects.all()
    serializer_class = User_serializers
    
    def get_permissions(self):
        if self.request.method in ["GET","POST","DELETE"]:
            if not self.request.user.groups.filter(name = 'Manager').exists():
                raise PermissionDenied("You are not authorized to view the content")
            return [permissions.IsAuthenticated()]
        
    def get_queryset(self):
        return User.objects.filter(groups__name = 'Delivery crew')
    
    def post(self,request):
        
        username  = request.data.get("username")
        delivery_group = get_object_or_404(Group,name = 'Delivery crew')
        
        if username:
            username = get_object_or_404(User,username=username)
            
            if delivery_group.user_set.filter(username=username).exists():
                return Response({'message':f"{username} is already part of Delivery crew"})
            else:
                delivery_group.user_set.add(username)
                delivery_crew = User.objects.filter(groups__name = 'Delivery crew').values('id','username','email')
                return Response({
                    "message":f"{username} has been added to Delivery crew",
                    "Delivery crew":delivery_crew
                },201)
                
    def delete(self,request,username):
        
        delivery_crew =  get_object_or_404(Group,name='Delivery crew')
        
        if username:
            if username.isdigit():
                username =  get_object_or_404(User,pk=int(username))
            else:
                username =  get_object_or_404(User,username=username)
                
            if not delivery_crew.user_set.filter(username=username).exists():
                return Response({"message":f"{username} is not part of delivery crew group"})
            else:
                delivery_crew.user_set.remove(username)
                delivery_crew_obj = User.objects.filter(groups__name  = 'Delivery crew').values('id','username','email')
                return Response({
                    "message":f"{username} has been removed from the delivery crew group",
                    "Delivery crew":delivery_crew_obj
                },200)
        else:
            return response({"error":"provide username/id in the body or in the path"})
        
class Cart_viewer(generics.ListCreateAPIView,generics.DestroyAPIView):
    
    queryset = Cart.objects.all()
    serializer_class = cart_serializers
    
    def get_permissions(self):
        user_groups = self.request.user.groups.values_list('name', flat=True)
        if self.request.method in ['GET','POST','PATCH']:
            if "Manager" in user_groups or not user_groups:
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You are not authorized to delete this content.")
        if self.request.method == 'DELETE':
            if 'Manager' in user_groups:
                return [permissions.IsAuthenticated()]
            else:
                raise PermissionDenied("You are not authorized to delete this content.")   
        raise PermissionDenied("You are not authorized to delete this content.")
        
    def get_queryset(self):
        return Cart.objects.filter(user = self.request.user )
    
    def delete(self, request, *args, **kwargs):
        user =  request.user
        
        if not Cart.objects.filter(user = user).exists():
            return Response({"message": "your Cart is empty"}, status=status.HTTP_204_NO_CONTENT)
        else:
            user =  request.user
            Cart.objects.filter(user = user).delete()
            return Response({"message": "Cart cleared successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class Order_viewer(generics.ListCreateAPIView,generics.RetrieveUpdateAPIView):
    
    request = HttpRequest
    queryset = Order.objects.all()
    serializer_class = Order_serializers
    
    def get_permissions(self):
        user_groups = set(self.request.user.groups.values_list('name', flat=True))
        if self.request.method in ['GET','PATCH','PUT']:
            if set(user_groups) & {"Manager", "Delivery crew"} or not user_groups:
                return [permissions.IsAuthenticated()]
        if self.request.method == 'DELETE':
            if 'Manager' in user_groups:
                return [permissions.IsAuthenticated()]
            raise PermissionDenied("You are not authorized to view the content")
        if self.request.method == 'POST':
            if "Manager" in user_groups or not user_groups:
                return [permissions.IsAuthenticated()]
            raise PermissionDenied("You are not authorized to view the content")
        
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        user = self.request.user
        user_groups = set(user.groups.values_list('name', flat=True))

        if pk:
            order = get_object_or_404(Order, pk=pk)
            if not user_groups:
                if order.user == user:
                    return Orderitem.objects.filter(order=order)
                return Orderitem.objects.none()
            if "Manager" in user_groups:
                return Orderitem.objects.filter(order=order)
            if "Delivery Crew" in user_groups and order.delivery_crew == user:
                return Orderitem.objects.filter(order=order)
            return Orderitem.objects.none()

        if not user_groups:
            return Order.objects.filter(user=user)
        if "Manager" in user_groups:
            return Order.objects.all()
        if "Delivery Crew" in user_groups:
            return Order.objects.filter(delivery_crew__username=user)
        return Order.objects.none()
        
    def delete(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        get_object_or_404(Order,pk=pk)
        Order.objects.filter(pk = pk).delete()
        return Response({"message":"Order deleted"})
    



    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        total = sum(Decimal(item.price) for item in cart_items)
        order = Order.objects.create(
            user=user,
            total=total,
            date=timezone.now().date(),
            delivery_crew=None  # assuming it's optional
        )
        try:
            with transaction.atomic():
                for item in cart_items:
                    print(f"order : {order} \n menu item :{item.menuitem} \n quantity : {item.quantity} \n price : {item.unit_price} \n total : {item.price}")
                    Orderitem.objects.create(
                        order=order,
                        menuitem=item.menuitem,
                        quantity=item.quantity,
                        unitprice=item.unit_price,
                        price=item.price
                    )
                cart_items.delete()

        except IntegrityError as e:
            return Response({"error": f"Database Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def patch(self, request, *args, **kwargs):
        
        user = request.user
        pk = kwargs.get("pk")
        status = request.data.get('status')
        crew = request.data.get('delivery_crew')
        user_groups = set(user.groups.values_list('name', flat=True))
        if not user_groups:
            return Response({"message":f"provide field 'status' or 'delivery_crew'"})
        
        if pk:
            order = get_object_or_404(Order, pk=pk)
        else:
            return Response({"error":"add the id of the order as a path"})
        if crew:
            delivery_crew = get_object_or_404(User, pk=crew)
        
        if request.user.groups.filter(name = 'Manager').exists():
            
            if not status and not crew:
                return Response({"error":f"provide field 'status' or 'delivery_crew' "},400)
            
            if status and crew:
                order.status = status
                order.delivery_crew = delivery_crew
                order.save()
                return Response({"message":f"Order {pk} has been updated"},200)
            
            if status or delivery_crew:
                if status:
                    order.status = status
                if crew:
                    order.delivery_crew = delivery_crew
                order.save()
                return Response({"message":f"Order {pk} has been updated"},200)
        
        if request.user.groups.filter(name = 'DeliveryCrew').exists():
            
            if status:
                order.status = status
                order.save()
                return Response({"message":f"Order {pk} has been updated"},200)
            else:
                return Response({"error":f"payload should field 'status'"},400)
            
        raise PermissionDenied({"message":f"You are not authorized to make the action"})
    
class Order_item_viewer(generics.ListAPIView):
    
    request = HttpRequest
    queryset = Orderitem.objects.all()
    serializer_class = Orderitem_serializers
    
    def get_permissions(self):
        user_groups = set(self.request.user.groups.values_list('name', flat=True))
        if self.request.method in ['GET','PATCH','PUT']:
            if set(user_groups) & {"Manager", "Delivery crew"} or not user_groups:
                return [permissions.IsAuthenticated()]
        
    def get_queryset(self):
        pk = self.kwargs.get('pk')
        user = self.request.user
        user_groups = set(user.groups.values_list('name', flat=True))

        if pk:
            order = get_object_or_404(Order, pk=pk)
            if not user_groups:
                if order.user == user:
                    return Orderitem.objects.filter(order=order)
                return Orderitem.objects.none()
            if "Manager" in user_groups:
                return Orderitem.objects.filter(order=order)
            if "Delivery Crew" in user_groups and order.delivery_crew == user:
                return Orderitem.objects.filter(order=order)
            return Orderitem.objects.none()