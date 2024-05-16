from django.contrib import admin
from .models import User,WorkSpace,Uploadfiles
# Register your models here.
admin.site.register(User)
admin.site.register(WorkSpace)
admin.site.register(Uploadfiles)