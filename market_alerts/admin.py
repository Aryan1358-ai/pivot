from django.contrib import admin
from .models  import AlertRule,TriggeredAlert
# Register your models here.

admin.site.register(AlertRule)

admin.site.register(TriggeredAlert)
