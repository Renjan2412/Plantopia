from django.db import models

# Create your models here.

class Coupon(models.Model):
    code            = models.CharField(max_length=100, unique=True)
    valid_from      = models.DateTimeField()
    valid_to        = models.DateTimeField()
    min_amount      = models.FloatField(default=0.0)
    discount_amount = models.FloatField(default=0.0)
    active          = models.BooleanField(default=True)
    
    def _str_(self):
        return self.code
