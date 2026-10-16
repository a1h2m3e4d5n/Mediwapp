from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver



class Department(models.Model):
    name = models.CharField('اسم القسم', max_length=120, unique=True)
    is_active = models.BooleanField('نشط', default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'قسم'
        verbose_name_plural = 'الأقسام'

    def __str__(self):
        return self.name


class Patient(models.Model):
    GENDERS = [('male', 'ذكر'), ('female', 'أنثى')]
    full_name = models.CharField('اسم المريض', max_length=160)
    medical_record_number = models.CharField('رقم الملف الطبي', max_length=40, unique=True)
    phone_number = models.CharField('رقم WhatsApp', max_length=30)
    national_id = models.CharField('رقم الهوية', max_length=40, blank=True)
    date_of_birth = models.DateField('تاريخ الميلاد', null=True, blank=True)
    gender = models.CharField('الجنس', max_length=10, choices=GENDERS, blank=True)
    created_at = models.DateTimeField('تاريخ الإضافة', auto_now_add=True)
    updated_at = models.DateTimeField('آخر تحديث', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'مريض'
        verbose_name_plural = 'المرضى'

    def __str__(self):
        return f'{self.full_name} — {self.medical_record_number}'


class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits', verbose_name='المريض')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='visits', verbose_name='القسم')
    notes = models.TextField('ملاحظات', blank=True)
    registered_at = models.DateTimeField('وقت التسجيل', default=timezone.now)
    welcome_sent = models.BooleanField('تم إرسال الترحيب', default=False)

    class Meta:
        ordering = ['-registered_at']
        verbose_name = 'زيارة'
        verbose_name_plural = 'الزيارات'

    def __str__(self):
        return f'{self.patient.full_name} — {self.department.name}'


class Exam(models.Model):
    STATUSES = [('draft', 'مسودة'), ('final', 'نهائي معتمد')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='exams', verbose_name='المريض')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True, related_name='exams', verbose_name='الزيارة')
    exam_type = models.CharField('نوع الفحص', max_length=160)
    physician_name = models.CharField('الطبيب', max_length=160, blank=True)
    status = models.CharField('حالة الفحص', max_length=10, choices=STATUSES, default='final')
    result_summary = models.CharField('ملخص النتيجة', max_length=500)
    detailed_results = models.TextField('تفاصيل النتيجة')
    created_at = models.DateTimeField('وقت التسجيل', auto_now_add=True)
    approved_at = models.DateTimeField('وقت الاعتماد', null=True, blank=True)
    pdf_file = models.FileField('ملف PDF', upload_to='exam_pdfs/', blank=True)
    pdf_generated_at = models.DateTimeField('وقت إنشاء PDF', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'فحص'
        verbose_name_plural = 'الفحوصات'

    def __str__(self):
        return f'{self.exam_type} — {self.patient.full_name}'


class MessageLog(models.Model):
    CHANNELS = [('whatsapp', 'WhatsApp')]
    TYPES = [('welcome', 'ترحيب'), ('exam_pdf', 'ملف فحص')]
    STATUSES = [('queued', 'قيد المعالجة'), ('sent', 'تم الإرسال'), ('failed', 'فشل'), ('simulated', 'محاكاة تجريبية')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='message_logs', verbose_name='المريض')
    visit = models.ForeignKey(Visit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='الزيارة')
    exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='الفحص')
    channel = models.CharField('القناة', max_length=20, choices=CHANNELS, default='whatsapp')
    message_type = models.CharField('نوع الرسالة', max_length=20, choices=TYPES)
    status = models.CharField('الحالة', max_length=20, choices=STATUSES, default='queued')
    recipient = models.CharField('المستلم', max_length=40)
    provider_message_id = models.CharField('معرف المزود', max_length=160, blank=True)
    error_message = models.TextField('تفاصيل الخطأ', blank=True)
    sent_at = models.DateTimeField('وقت الإرسال', null=True, blank=True)
    created_at = models.DateTimeField('وقت الإنشاء', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'سجل رسالة'
        verbose_name_plural = 'سجل الرسائل'


class ActivityLog(models.Model):
    action = models.CharField('الإجراء', max_length=80)
    description = models.TextField('الوصف')
    actor_name = models.CharField('المستخدم', max_length=120, default='موظف الاستقبال')
    created_at = models.DateTimeField('التاريخ', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'سجل عملية'
        verbose_name_plural = 'سجل العمليات'




# ----------- أضف هذا الكود في نهاية الملف -----------
class SMSQueue(models.Model):
    phone_number = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    message = models.TextField(verbose_name="نص الرسالة")
    is_sent = models.BooleanField(default=False, verbose_name="تم الإرسال؟")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone_number} - {'تم' if self.is_sent else 'في الانتظار'}"

# يتم استدعاء هذا الحدث تلقائياً عند إضافة مريض جديد
# (تأكد أن اسم نموذج المريض لديك هو Patient وحقل الهاتف هو phone)
@receiver(post_save, sender='core.Patient')
def create_welcome_sms(sender, instance, created, **kwargs):
    if created:
        # جلب رقم الهاتف (يدعم إذا كان اسم الحقل phone أو phone_number)
        phone = getattr(instance, 'phone', None) or getattr(instance, 'phone_number', None)
        if phone:
            patient_name = instance.full_name
            welcome_text = f"أهلاً بك {patient_name} في عيادتنا. نتمنى لك دوام الصحة والعافية."
            SMSQueue.objects.create(
                phone_number=phone,
                message=welcome_text
            )
