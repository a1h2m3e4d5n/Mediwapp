from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import DepartmentForm, ExamForm, PatientRegistrationForm
from .models import ActivityLog, Department, Exam, MessageLog, Patient, Visit
from .services.pdf import generate_exam_pdf
from .services.whatsapp import send_exam_document, send_welcome


def log_activity(action, description):
    ActivityLog.objects.create(action=action, description=description)


def persist_message(patient, result, message_type, visit=None, exam=None):
    return MessageLog.objects.create(
        patient=patient, visit=visit, exam=exam, message_type=message_type,
        status=result['status'], recipient=patient.phone_number,
        provider_message_id=result.get('provider_message_id', ''),
        error_message=result.get('error', ''), sent_at=result.get('sent_at'),
    )


def dashboard(request):
    context = {
        'patient_count': Patient.objects.count(), 'visit_count': Visit.objects.count(),
        'exam_count': Exam.objects.count(), 'sent_count': MessageLog.objects.filter(status='sent').count(),
        'recent_visits': Visit.objects.select_related('patient', 'department')[:6],
        'recent_exams': Exam.objects.select_related('patient')[:6],
        'recent_messages': MessageLog.objects.select_related('patient', 'exam', 'visit')[:5],
    }
    return render(request, 'core/dashboard.html', context)


def patient_list(request):
    query = request.GET.get('q', '').strip()
    patients = Patient.objects.all()
    if query:
        patients = patients.filter(Q(full_name__icontains=query) | Q(medical_record_number__icontains=query) | Q(phone_number__icontains=query))
    return render(request, 'core/patients.html', {'patients': patients, 'query': query})


@require_http_methods(['GET', 'POST'])
def patient_create(request):
    form = PatientRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        patient = form.save()
        department = form.cleaned_data['department']
        visit = Visit.objects.create(patient=patient, department=department, notes=form.cleaned_data.get('notes', ''))
        result = send_welcome(patient.phone_number, patient.full_name, department.name)
        persist_message(patient, result, 'welcome', visit=visit)
        visit.welcome_sent = result['status'] in ('sent', 'simulated')
        visit.save(update_fields=['welcome_sent'])
        log_activity('تسجيل مريض', f'تم تسجيل {patient.full_name} في قسم {department.name}. حالة الترحيب: {result["status"]}.')
        messages.success(request, f'تم تسجيل المريض وإضافة الزيارة. حالة رسالة الترحيب: {dict(MessageLog.STATUSES)[result["status"]]}.')
        return redirect('patient_detail', pk=patient.pk)
    return render(request, 'core/patient_form.html', {'form': form})


def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'core/patient_detail.html', {'patient': patient, 'visits': patient.visits.select_related('department'), 'exams': patient.exams.all()})


def exam_list(request):
    query = request.GET.get('q', '').strip()
    exams = Exam.objects.select_related('patient', 'visit')
    if query:
        exams = exams.filter(Q(patient__full_name__icontains=query) | Q(patient__medical_record_number__icontains=query) | Q(exam_type__icontains=query))
    return render(request, 'core/exams.html', {'exams': exams, 'query': query})


@require_http_methods(['GET', 'POST'])
def exam_create(request):
    form = ExamForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        exam = form.save(commit=False)
        if exam.status == 'final':
            exam.approved_at = timezone.now()
        exam.save()
        exam = generate_exam_pdf(exam)
        exam.save()
        public_url = f'{settings.PUBLIC_BASE_URL}{exam.pdf_file.url}' if settings.PUBLIC_BASE_URL and exam.pdf_file else ''
        result = send_exam_document(exam.patient.phone_number, public_url, exam.exam_type, exam.patient.full_name)
        persist_message(exam.patient, result, 'exam_pdf', exam=exam, visit=exam.visit)
        log_activity('إنشاء فحص', f'تم إنشاء فحص {exam.exam_type} للمريض {exam.patient.full_name} وتوليد ملف PDF. حالة الإرسال: {result["status"]}.')
        messages.success(request, f'تم حفظ الفحص وتوليد PDF. حالة إرسال WhatsApp: {dict(MessageLog.STATUSES)[result["status"]]}.')
        return redirect('exam_detail', pk=exam.pk)
    return render(request, 'core/exam_form.html', {'form': form})


def exam_detail(request, pk):
    exam = get_object_or_404(Exam.objects.select_related('patient', 'visit'), pk=pk)
    return render(request, 'core/exam_detail.html', {'exam': exam, 'message_logs': exam.patient.message_logs.filter(exam=exam)})


def exam_pdf(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if not exam.pdf_file:
        raise Http404('لا يوجد ملف PDF لهذا الفحص')
    return FileResponse(exam.pdf_file.open('rb'), as_attachment=False, filename=f'exam-{exam.pk}.pdf', content_type='application/pdf')


def message_logs(request):
    logs = MessageLog.objects.select_related('patient', 'exam', 'visit')
    return render(request, 'core/logs.html', {'logs': logs})


@require_http_methods(['POST'])
def resend_message(request, pk):
    log = get_object_or_404(MessageLog.objects.select_related('patient', 'exam', 'visit'), pk=pk)
    if log.message_type == 'welcome' and log.visit:
        result = send_welcome(log.patient.phone_number, log.patient.full_name, log.visit.department.name)
    elif log.message_type == 'exam_pdf' and log.exam and log.exam.pdf_file:
        url = f'{settings.PUBLIC_BASE_URL}{log.exam.pdf_file.url}' if settings.PUBLIC_BASE_URL else ''
        result = send_exam_document(log.patient.phone_number, url, log.exam.exam_type, log.patient.full_name)
    else:
        result = {'status': 'failed', 'provider_message_id': '', 'error': 'بيانات الإرسال غير مكتملة.', 'sent_at': None}
    log.status = result['status']; log.provider_message_id = result.get('provider_message_id', ''); log.error_message = result.get('error', ''); log.sent_at = result.get('sent_at'); log.save()
    log_activity('إعادة إرسال', f'إعادة إرسال {log.get_message_type_display()} للمريض {log.patient.full_name}: {result["status"]}.')
    messages.info(request, f'تمت إعادة المحاولة: {dict(MessageLog.STATUSES)[result["status"]]}.')
    return redirect(request.POST.get('next') or 'message_logs')


def settings_page(request):
    return render(request, 'core/settings.html', {
        'whatsapp_enabled': settings.WHATSAPP_ENABLED,
        'phone_id_configured': bool(settings.META_PHONE_NUMBER_ID),
        'token_configured': bool(settings.META_WHATSAPP_TOKEN),
        'public_url_configured': bool(settings.PUBLIC_BASE_URL),
        'departments': Department.objects.order_by('name'),
    })


@require_http_methods(['GET', 'POST'])
def department_settings(request):
    form = DepartmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        department = form.save()
        log_activity('إضافة قسم', f'تمت إضافة القسم {department.name}.')
        messages.success(request, 'تمت إضافة القسم بنجاح.')
        return redirect('settings')
    return render(request, 'core/department_form.html', {'form': form})
