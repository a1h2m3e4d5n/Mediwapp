from unittest.mock import Mock, patch

from django.test import Client, TestCase, override_settings

from .models import Department, Exam, MessageLog, Patient, Visit
from .services.whatsapp import send_exam_document, send_welcome


class MediWappFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(name='الباطنية')
        self.patient = Patient.objects.create(
            full_name='مريض اختبار',
            medical_record_number='TEST-001',
            phone_number='966500000000',
            gender='male',
        )
        self.visit = Visit.objects.create(patient=self.patient, department=self.department)

    def test_patient_registration_creates_visit_and_simulated_welcome(self):
        response = self.client.post('/patients/new/', {
            'full_name': 'مريض جديد',
            'medical_record_number': 'TEST-002',
            'phone_number': '966511111111',
            'national_id': '',
            'date_of_birth': '',
            'gender': 'male',
            'department': self.department.pk,
            'notes': 'ملاحظة',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/patients/'))
        new_patient = Patient.objects.get(medical_record_number='TEST-002')
        self.assertEqual(new_patient.visits.count(), 1)
        self.assertEqual(MessageLog.objects.get(patient=new_patient).status, 'simulated')

    def test_exam_requires_visit_from_same_patient_and_generates_pdf(self):
        response = self.client.post('/exams/new/', {
            'patient': self.patient.pk,
            'visit': self.visit.pk,
            'exam_type': 'تحليل دم',
            'physician_name': 'د. اختبار',
            'status': 'final',
            'result_summary': 'طبيعي',
            'detailed_results': 'الهيموغلوبين طبيعي',
        })
        self.assertEqual(response.status_code, 302)
        exam = Exam.objects.get(patient=self.patient)
        self.assertTrue(exam.pdf_file.name.startswith('exam_pdfs/'))
        self.assertGreater(exam.pdf_file.size, 0)
        self.assertEqual(MessageLog.objects.get(exam=exam).status, 'simulated')

    def test_exam_cannot_use_another_patient_visit(self):
        other = Patient.objects.create(
            full_name='مريض آخر', medical_record_number='TEST-003', phone_number='966522222222'
        )
        other_visit = Visit.objects.create(patient=other, department=self.department)
        response = self.client.post('/exams/new/', {
            'patient': self.patient.pk,
            'visit': other_visit.pk,
            'exam_type': 'فحص',
            'physician_name': '',
            'status': 'draft',
            'result_summary': 'ملخص',
            'detailed_results': 'تفاصيل',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Exam.objects.exists())
        self.assertContains(response, 'الزيارة تابعة للمريض المحدد')

    def test_settings_page_displays_departments(self):
        response = self.client.get('/settings/')
        self.assertContains(response, 'الباطنية')
        self.assertNotContains(response, 'لا توجد أقسام')


class WhatsAppTemplateTests(TestCase):
    @override_settings(
        WHATSAPP_ENABLED=True,
        META_WHATSAPP_TOKEN='token',
        META_PHONE_NUMBER_ID='phone-id',
        WHATSAPP_TEMPLATE_LANGUAGE='ar',
        WHATSAPP_WELCOME_TEMPLATE='welcome_ar',
        WHATSAPP_EXAM_TEMPLATE='exam_ar',
        PUBLIC_BASE_URL='https://example.com',
    )
    @patch('core.services.whatsapp.requests.post')
    def test_welcome_uses_meta_template(self, post):
        post.return_value = Mock(ok=True, json=lambda: {'messages': [{'id': 'wamid.1'}]})
        result = send_welcome('966500000000', 'أحمد', 'الباطنية')
        self.assertEqual(result['status'], 'sent')
        payload = post.call_args.kwargs['json']
        self.assertEqual(payload['type'], 'template')
        self.assertEqual(payload['template']['name'], 'welcome_ar')
        self.assertEqual(payload['template']['language']['code'], 'ar')
        self.assertEqual(payload['template']['components'][0]['parameters'][0]['text'], 'أحمد')

    @override_settings(WHATSAPP_ENABLED=False)
    def test_exam_simulation_does_not_require_public_url(self):
        result = send_exam_document('966500000000', '', 'تحليل دم', 'أحمد')
        self.assertEqual(result['status'], 'simulated')
