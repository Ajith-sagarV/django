from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import Menu_items_view,Category_view,Menu_items_single_view,Manager_assignment,Delivery_assignment,Cart_viewer,Order_viewer,Order_item_viewer
urlpatterns = [
    path("auth/",include("djoser.urls")),
    path("auth/",include("djoser.urls.authtoken")),
    path("token/login",view=TokenObtainPairView.as_view(),name="token-generation"),
    path("menu-items/",view=Menu_items_view.as_view(),name="Menu-items"),
    path("menu-items/<int:pk>",view=Menu_items_single_view.as_view(),name="Menu-items"),
    path("category/",view=Category_view.as_view(),name="Category"),
    path("groups/manager/users/",view=Manager_assignment.as_view(),name="Manager-list-create"),
    path("groups/manager/users/<str:username>/",view=Manager_assignment.as_view(),name="Manager-remove"),
    path("groups/delivery-crew/users/",view=Delivery_assignment.as_view(),name="delivery-list-create"),
    path("groups/delivery-crew/users/<str:username>/",view=Delivery_assignment.as_view(),name="delivery-list-create"),
    path("cart/menu-items/",Cart_viewer.as_view(),name="delivery-list-create"),
    path("orders/",Order_viewer.as_view(),name="orders"),
    path("orders/<int:pk>/",Order_item_viewer.as_view(),name="orders"),
]
