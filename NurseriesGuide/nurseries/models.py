from django.db import models
from django.contrib.auth.models import User

# City Model
class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Neighborhood Model
class Neighborhood(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, related_name='neighborhoods', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.city.name},{self.name}"


# Nursery Model
class Nursery(models.Model):
    name = models.CharField(max_length=255)
    address = models.URLField(max_length=3000)  # Changed from CharField to URLField
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    description = models.TextField()
    accepts_special_needs = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='pending', choices=(
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ))
    rejection_reason = models.TextField(blank=True, null=True)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.CASCADE, related_name='nurseries')
    owner = models.ForeignKey(User, on_delete=models.CASCADE,  limit_choices_to={'is_staff': True})

    def __str__(self):
        return self.name
#Activity Model 
class Activity(models.Model):
    name = models.CharField(max_length=100)  
    description = models.TextField()
    age_min = models.IntegerField(default=2)
    age_max = models.IntegerField(default=5)
    image = models.ImageField(upload_to='images/', default="images/default.jpg")  
    nursery = models.ForeignKey(Nursery, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

#Gallery Model 

from django.db import models

class Gallery(models.Model):
    image = models.ImageField(upload_to='images/', default="images/default.jpg")
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    nursery = models.ForeignKey('Nursery', on_delete=models.CASCADE)

#Staff Model 
class Staff(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/', default="images/profile_default.jpg")
    specializations = models.TextField()
    experience=models.TextField()
    nursery = models.ForeignKey(Nursery, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
