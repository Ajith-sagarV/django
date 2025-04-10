from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    
    slug = models.SlugField()
    title = models.CharField(max_length=255,db_index=True)
    
    def __str__(self):
        return self.title

class Menuitem(models.Model):
    
    title = models.CharField(max_length=255,db_index=True)
    price = models.DecimalField(decimal_places=2,max_digits=6,db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category,on_delete=models.PROTECT)
    
    def __str__(self):
        return f"{self.title} : {self.price} : {self.featured} : {self.category}"
    
class Cart(models.Model):
    
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    menuitem = models.ForeignKey(Menuitem,on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    
    class Meta:
        
        unique_together = ('menuitem','user')
        
    def __str__(self):
        return f"{self.user} : {self.menuitem} : {self.price} "
        
class Order(models.Model):
    
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='delivery_crew',null=True)
    status = models.BooleanField(db_index=True,default=0)
    total = models.DecimalField(max_digits=6,decimal_places=2)
    date = models.DateField(db_index=True)
    
    def __str__(self):
        return f"{self.user} : {self.delivery_crew} : {self.status} : {self.total} : {self.date}"
    
class Orderitem(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(Menuitem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unitprice = models.DecimalField(max_digits=6,decimal_places=2)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    
    class Meta:
        
        unique_together = ('order','menuitem')