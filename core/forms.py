from django import forms
from .models import Department, Exam, Patient, Visit


class PatientRegistrationForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.none(), label='القسم', empty_label='اختر القسم')
    notes = forms.CharField(label='ملاحظات الزيارة', required=False, widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}))

    class Meta:
        model = Patient
        fields = ['full_name', 'medical_record_number', 'phone_number', 'national_id', 'date_of_birth', 'gender', 'department', 'notes']
        labels = {'full_name': 'اسم المريض', 'medical_record_number': 'رقم الملف الطبي', 'phone_number': 'رقم WhatsApp', 'national_id': 'رقم الهوية', 'date_of_birth': 'تاريخ الميلاد', 'gender': 'الجنس'}
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'medical_record_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr', 'placeholder': '9665xxxxxxxx'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(is_active=True)
        self.fields['department'].widget.attrs['class'] = 'form-select'


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['patient', 'visit', 'exam_type', 'physician_name', 'status', 'result_summary', 'detailed_results']
        labels = {'patient': 'المريض', 'visit': 'الزيارة المرتبطة', 'exam_type': 'نوع الفحص', 'physician_name': 'الطبيب', 'status': 'حالة الفحص', 'result_summary': 'ملخص النتيجة', 'detailed_results': 'تفاصيل النتيجة'}
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}), 'visit': forms.Select(attrs={'class': 'form-select'}),
            'exam_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: تحليل دم شامل'}),
            'physician_name': forms.TextInput(attrs={'class': 'form-control'}), 'status': forms.Select(attrs={'class': 'form-select'}),
            'result_summary': forms.TextInput(attrs={'class': 'form-control'}), 'detailed_results': forms.Textarea(attrs={'rows': 8, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.order_by('full_name')
        self.fields['visit'].queryset = Visit.objects.select_related(
            'patient', 'department'
        ).order_by('-registered_at')
        self.fields['visit'].label_from_instance = lambda visit: f'{visit.patient.full_name} — {visit.department.name} — {visit.registered_at:%Y-%m-%d %H:%M}'
        self.fields['visit'].required = True

    def clean(self):
        cleaned = super().clean()
        patient = cleaned.get('patient')
        visit = cleaned.get('visit')
        if patient and visit and visit.patient_id != patient.pk:
            self.add_error('visit', 'يجب أن تكون الزيارة تابعة للمريض المحدد.')
        return cleaned


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'is_active']
        labels = {'name': 'اسم القسم', 'is_active': 'نشط'}
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'}), 'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})}
