# نشر MediWapp على PythonAnywhere

هذا المشروع لا يفرض تسجيل دخول أو صلاحيات حسب النطاق المطلوب. استخدمه داخل رابط غير معلن أو خلف الحماية التي توفرها بيئة التشغيل إذا احتجت ذلك.

## 1. رفع المشروع وتثبيت الاعتماديات

```bash
cd /home/yourusername/mediwapp
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p media staticfiles
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed_demo  # اختياري للبيانات التجريبية
```

## 2. قاعدة PostgreSQL

أنشئ قاعدة PostgreSQL، ثم اضبط المتغير التالي في إعدادات Web أو ملف البيئة:

```text
POSTGRES_URL=postgresql://USER:PASSWORD@HOST:5432/DBNAME
POSTGRES_SSL=true
```

يستخدم المشروع PostgreSQL تلقائياً عندما يبدأ `POSTGRES_URL` أو `DATABASE_URL` بـ `postgres://` أو `postgresql://`.

## 3. الملفات الدائمة

مجلدات PythonAnywhere تحت home تبقى موجودة بعد إعادة تشغيل التطبيق. استخدم:

```text
MEDIA_ROOT=/home/yourusername/mediwapp/media
STATIC_ROOT=/home/yourusername/mediwapp/staticfiles
```

في تبويب **Web → Static files** أضف:

| URL | Directory |
|---|---|
| `/static/` | `/home/yourusername/mediwapp/staticfiles` |
| `/media/` | `/home/yourusername/mediwapp/media` |

بعد أي تغيير في الملفات أو إعدادات البيئة اضغط **Reload** من تبويب Web.

## 4. إعداد WSGI

في ملف WSGI على PythonAnywhere استخدم مسار المشروع والبيئة الافتراضية:

```python
import os
import sys

path = '/home/yourusername/mediwapp'
if path not in sys.path:
    sys.path.insert(0, path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mediwapp.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 5. WhatsApp Cloud API

أنشئ قالبين معتمدين في Meta، وبنفس عدد المتغيرات الذي يتوقعه المشروع:

- قالب الترحيب `mediwapp_welcome`: متغيران في Body بالترتيب: اسم المريض، اسم القسم.
- قالب التقرير `mediwapp_exam_report`: Header من نوع Document، ومتغيران في Body بالترتيب: نوع الفحص، اسم المريض.

ثم اضبط:

```text
WHATSAPP_ENABLED=true
META_WHATSAPP_TOKEN=...
META_PHONE_NUMBER_ID=...
META_API_VERSION=v21.0
PUBLIC_BASE_URL=https://yourusername.pythonanywhere.com
WHATSAPP_TEMPLATE_LANGUAGE=ar
WHATSAPP_WELCOME_TEMPLATE=mediwapp_welcome
WHATSAPP_EXAM_TEMPLATE=mediwapp_exam_report
```

يجب أن يكون رابط PDF عاماً وقابلاً للوصول عبر HTTPS. عند ترك `WHATSAPP_ENABLED=false` يسجل المشروع العملية كمحاكاة ولا يتصل بـ Meta.

## 6. الفحص قبل إعادة التحميل

```bash
source .venv/bin/activate
python manage.py check
python manage.py test
python manage.py collectstatic --noinput
```
