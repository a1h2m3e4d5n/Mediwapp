import requests
from django.conf import settings
from django.utils import timezone


def _result(status, message_id='', error=''):
    return {
        'status': status,
        'provider_message_id': message_id,
        'error': error,
        'sent_at': timezone.now() if status in ('sent', 'simulated') else None,
    }


def _post(payload):
    if not settings.WHATSAPP_ENABLED:
        return _result('simulated', error='وضع المحاكاة مفعّل: لم يتم الاتصال بـ Meta.')
    if not settings.META_WHATSAPP_TOKEN or not settings.META_PHONE_NUMBER_ID:
        return _result('failed', error='بيانات Meta غير مكتملة: META_WHATSAPP_TOKEN و META_PHONE_NUMBER_ID مطلوبة.')
    url = f'https://graph.facebook.com/{settings.META_API_VERSION}/{settings.META_PHONE_NUMBER_ID}/messages'
    try:
        response = requests.post(
            url,
            json=payload,
            headers={'Authorization': f'Bearer {settings.META_WHATSAPP_TOKEN}'},
            timeout=30,
        )
        data = response.json()
        if response.ok:
            return _result('sent', (data.get('messages') or [{}])[0].get('id', ''))
        return _result('failed', error=data.get('error', {}).get('message', response.text[:500]))
    except (requests.RequestException, ValueError) as exc:
        return _result('failed', error=str(exc))


def _template(name, body_parameters=None, header_document=None):
    components = []
    if header_document:
        components.append({
            'type': 'header',
            'parameters': [{
                'type': 'document',
                'document': {
                    'link': header_document,
                    'filename': 'exam-report.pdf',
                },
            }],
        })
    if body_parameters:
        components.append({
            'type': 'body',
            'parameters': [{'type': 'text', 'text': str(value)} for value in body_parameters],
        })
    return {
        'messaging_product': 'whatsapp',
        'to': None,
        'type': 'template',
        'template': {
            'name': name,
            'language': {'code': settings.WHATSAPP_TEMPLATE_LANGUAGE},
            **({'components': components} if components else {}),
        },
    }


def send_welcome(phone, patient_name, department_name):
    payload = _template(
        settings.WHATSAPP_WELCOME_TEMPLATE,

#داله ارسال اسم المريض و القسم
       # body_parameters=[patient_name, department_name],
    )
    payload['to'] = phone
    return _post(payload)


def send_exam_document(phone, document_url, exam_type, patient_name):
    if not settings.WHATSAPP_ENABLED:
        return _result('simulated', error='وضع المحاكاة مفعّل: لم يتم الاتصال بـ Meta.')
    if not document_url:
        return _result('failed', error='PUBLIC_BASE_URL مطلوب لإرسال ملف PDF عبر Meta.')
    payload = _template(
        settings.WHATSAPP_EXAM_TEMPLATE,
        body_parameters=[exam_type, patient_name],
        header_document=document_url,
    )
    payload['to'] = phone
    return _post(payload)


# Backwards-compatible helpers for callers outside the current views.
def send_text(phone, text):
    return _result('failed', error='الإرسال النصي المباشر متوقف؛ استخدم قالب WhatsApp معتمداً.')


def send_document(phone, document_url, caption):
    return send_exam_document(phone, document_url, caption, '')
