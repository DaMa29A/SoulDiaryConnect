from django.contrib import admin
from .models import Doctor, Patient, DiaryEntry, Parameter

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(DiaryEntry)
admin.site.register(Parameter)