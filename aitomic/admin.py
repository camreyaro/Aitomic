from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(AIModel)
admin.site.register(Vote)
admin.site.register(Payment)
admin.site.register(ApiCall)
admin.site.register(Measure)
admin.site.register(ModelBought)