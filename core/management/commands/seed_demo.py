from django.core.management.base import BaseCommand
from core.models import Department, Exam, Patient, Visit
from django.utils import timezone


class Command(BaseCommand):
    help = 'تهيئة بيانات العرض التجريبي'

    def handle(self, *args, **options):
        departments = ['الباطنية', 'الطوارئ', 'الأطفال', 'المختبر', 'الأشعة']
        for name in departments:
            Department.objects.get_or_create(name=name)
        patient, created = Patient.objects.get_or_create(
            medical_record_number='DEMO-1001',
            defaults={'full_name': 'أحمد محمد علي', 'phone_number': '966500000000', 'gender': 'male'},
        )
        medicine = Department.objects.get(name='الباطنية')
        visit, _ = Visit.objects.get_or_create(patient=patient, department=medicine, defaults={'welcome_sent': True})
        if not Exam.objects.filter(patient=patient).exists():
            Exam.objects.create(patient=patient, visit=visit, exam_type='تحليل دم شامل', physician_name='د. سارة عبدالله', status='final', result_summary='النتيجة ضمن الحدود الطبيعية', detailed_results='الهيموغلوبين: 14.2\nكريات الدم البيضاء: 6.8\nالصفائح الدموية: 250')
        self.stdout.write(self.style.SUCCESS('تم تجهيز بيانات العرض التجريبي بنجاح.'))
