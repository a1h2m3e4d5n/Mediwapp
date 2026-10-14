from django.contrib import admin
from .models import ActivityLog, Department, Exam, MessageLog, Patient, Visit

admin.site.register([Department, Patient, Visit, Exam, MessageLog, ActivityLog])
