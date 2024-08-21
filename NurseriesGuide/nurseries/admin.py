from django.contrib import admin
from .models import Nursery ,Staff,Gallery,Activity ,City,Neighborhood
from registrations.models import Subscription ,Review
# Register your models here.
admin.site.register(Nursery)
admin.site.register(Staff)
admin.site.register(Gallery)
admin.site.register(Activity)
admin.site.register(City)
admin.site.register(Neighborhood)
admin.site.register(Subscription)
admin.site.register(Review)
