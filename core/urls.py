from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/new/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/new/', views.exam_create, name='exam_create'),
    path('exams/<int:pk>/', views.exam_detail, name='exam_detail'),
    path('exams/<int:pk>/pdf/', views.exam_pdf, name='exam_pdf'),
    path('messages/', views.message_logs, name='message_logs'),
    path('messages/<int:pk>/resend/', views.resend_message, name='resend_message'),
    path('settings/', views.settings_page, name='settings'),
    path('settings/departments/new/', views.department_settings, name='department_create'),
    # أضف هذه الأسطر داخل قائمة urlpatterns
    path('api/pending-sms/', views.get_pending_sms, name='pending-sms'),
    path('api/sms-sent/<int:sms_id>/', views.mark_sms_sent, name='sms-sent'),
]
