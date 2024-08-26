from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Parent(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=13) # 9665555555555 
    Work_number = models.CharField(max_length=13)

    def __str__(self):
        return f"{self.user.username} profile"
    

class Child(models.Model):

    class GenderChoices(models.TextChoices):
        
        FEMALE = "F", "انثى"
        MALE = "M", "ذكر"

    gender = models.CharField(
        max_length=1,
        choices=GenderChoices.choices,
    )

    first_name = models.CharField(max_length=124,default=None)
    last_name = models.CharField(max_length=124,default=None)
    birth_date = models.DateField()
    national_id = models.CharField(max_length=10)
    about = models.TextField(default= None)
    Disease = models.TextField(default= None)
    Allergy = models.TextField(default= None)
    parent = models.ForeignKey(Parent,on_delete=models.CASCADE)
    photo = models.ImageField(upload_to="images/", default="images/default.jpg")

    def age(self):
        today = date.today()
        years = today.year - self.birth_date.year
        months = today.month - self.birth_date.month

        # التحقق مما إذا كان اليوم الحالي أقل من يوم الميلاد
        if today.day < self.birth_date.day:
            months -= 1

        # إذا كانت الأشهر سالبة، قم بتصحيح السنة والشهر
        if months < 0:
            years -= 1
            months += 12

        # إذا كان العمر أقل من سنة، أرجع عدد الأشهر فقط
        if years == 0:
            return f"{months} أشهر"
        else:
            return f"{years} سنة"
