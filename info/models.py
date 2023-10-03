from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liked_stock_1 = models.CharField(max_length=10, blank=True)  # Field for the first liked stock
    liked_stock_2 = models.CharField(max_length=10, blank=True)  # Field for the second liked stock
    graph_image = models.ImageField(upload_to='user_graphs/', null=True, blank=True)

    def __str__(self):
        return self.user.username
