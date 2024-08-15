from django.db import models
from django.contrib.auth.models import User


class Parent(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=13) # 9665555555555 
    Work_number = models.CharField(max_length=13)

    def __str__(self):
        return f"{self.user.username} profile"
    

class Child(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class GenderChoices(models.TextChoices):
        
        FEMALE = "F", "انثى"
        MALE = "M", "ذكر"

    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
    )

    birth_date = models.DateField()
    national_id = models.CharField(max_length=10)
    about = models.TextField(default= None)
    parent = models.ForeignKey(Parent,on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="images/", default="images/default.jpg")
