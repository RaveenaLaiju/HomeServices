from django.contrib import admin
from . models import *
# Register your models here.



class Service_Display(admin.ModelAdmin):
    list_display=['service_name','image','price']
admin.site.register(Service,Service_Display)

