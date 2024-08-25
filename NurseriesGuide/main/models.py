from django.db import models
from parents.models import Parent

# Create your models here.
class Contact(models.Model):
    first_name = models.CharField(max_length=1024,default=" ")
    last_name = models.CharField(max_length=1024,default=" ")

    email = models.EmailField()
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return self.name
    
class Web_Review(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],default="5")
    comment = models.TextField(blank=True)
