from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    loyalty_points = models.IntegerField(default=0)

    def __str__(self):
        return self.name
