from django.db import models
from nurseries.models import Nursery
from parents.models import Child, Parent




class Subscription(models.Model):
    DURATION_CHOICES = [
        ('day', 'Daily'),
        ('week', 'Weekly'),
        ('month', 'Monthly'),
        ('year', 'Yearly'),
    ]

    nursery = models.ForeignKey(Nursery, on_delete=models.CASCADE, related_name='subscriptions')
    duration_unit = models.CharField(max_length=10, choices=DURATION_CHOICES)
    duration_number = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    age_min = models.IntegerField(default=0)
    age_max = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.duration_number} {self.get_duration_unit_display()}"




class Registration(models.Model):
    STATUS_CHOICES = [
        ('reviewing', 'Reviewing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='registrations')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='reviewing')
    rejection_reason = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.status != 'rejected':
            self.rejection_reason = None  # Clear the rejection reason if not rejected
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Registration of {self.child} - {self.status}"





class Review(models.Model):
    nursery = models.ForeignKey(Nursery, on_delete=models.CASCADE, related_name='reviews')
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(blank=True)