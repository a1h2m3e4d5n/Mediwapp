from django.http import JsonResponse


def health(request):
    return JsonResponse({'status': 'ok', 'service': 'mediwapp'})


def routes_manifest(request):
    return JsonResponse({'routes': [
        {'path': '/', 'title': 'لوحة المتابعة'}, {'path': '/patients/', 'title': 'المرضى والاستقبال'},
        {'path': '/patients/new/', 'title': 'تسجيل مريض'}, {'path': '/patients/:id/', 'title': 'ملف المريض'},
        {'path': '/exams/', 'title': 'الفحوصات'}, {'path': '/exams/new/', 'title': 'تسجيل فحص'},
        {'path': '/exams/:id/', 'title': 'تفاصيل الفحص'}, {'path': '/messages/', 'title': 'سجل الرسائل'},
        {'path': '/settings/', 'title': 'الإعدادات'},
    ]})
