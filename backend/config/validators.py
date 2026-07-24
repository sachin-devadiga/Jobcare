import re
import os
import magic
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import filesizeformat


ALLOWED_IMAGE_TYPES = {
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
}

ALLOWED_DOCUMENT_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'text/csv',
}

ALLOWED_VIDEO_TYPES = {
    'video/mp4', 'video/webm', 'video/ogg', 'video/x-msvideo',
}

ALLOWED_AUDIO_TYPES = {
    'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/webm', 'audio/x-m4a',
}


def validate_file_extension(allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx',
            '.txt', '.csv', '.mp4', '.webm', '.mp3', '.wav',
        ]

    def validator(value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                _('Unsupported file extension "%(ext)s". Allowed: %(allowed)s'),
                params={'ext': ext, 'allowed': ', '.join(allowed_extensions)},
            )

    return validator


def validate_file_size(max_size_mb=10):
    max_bytes = max_size_mb * 1024 * 1024

    def validator(value):
        if value.size > max_bytes:
            raise ValidationError(
                _('File size %(size)s exceeds maximum allowed size of %(max_size)s'),
                params={
                    'size': filesizeformat(value.size),
                    'max_size': filesizeformat(max_bytes),
                },
            )

    return validator


def validate_file_content_type(allowed_types=None):
    if allowed_types is None:
        allowed_types = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES | ALLOWED_VIDEO_TYPES | ALLOWED_AUDIO_TYPES

    def validator(value):
        try:
            mime_type = magic.from_buffer(value.read(2048), mime=True)
            value.seek(0)
        except Exception:
            mime_type = ''
            value.seek(0)

        if mime_type and mime_type not in allowed_types:
            raise ValidationError(
                _('File type "%(type)s" is not allowed.'),
                params={'type': mime_type},
            )

    return validator


def sanitize_html(value):
    if not isinstance(value, str):
        return value
    import bleach
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li', 'span']
    allowed_attrs = {}
    cleaned = bleach.clean(value, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    return cleaned


def sanitize_text_input(value):
    if not isinstance(value, str):
        return value
    cleaned = re.sub(r'<[^>]*>', '', value)
    cleaned = cleaned.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    cleaned = cleaned.replace('"', '&quot;').replace("'", '&#x27;')
    return cleaned


def validate_phone_number(value):
    cleaned = re.sub(r'[\s\-\(\)]', '', value)
    pattern = r'^\+?[1-9]\d{9,14}$'
    if not re.match(pattern, cleaned):
        raise ValidationError(
            _('Enter a valid phone number (10-15 digits with optional + prefix).'),
        )
    return cleaned


def validate_aadhaar_number(value):
    cleaned = re.sub(r'\s', '', value)
    if not re.match(r'^\d{12}$', cleaned):
        raise ValidationError(
            _('Aadhaar number must be exactly 12 digits.'),
        )
    if cleaned in ['000000000000', '111111111111', '222222222222', '333333333333',
                   '444444444444', '555555555555', '666666666666', '777777777777',
                   '888888888888', '999999999999', '123456789012']:
        raise ValidationError(
            _('Invalid Aadhaar number.'),
        )
    weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    checksum = sum(int(d) * w for d, w in zip(cleaned, weights))
    if checksum % 10 != 0:
        raise ValidationError(
            _('Invalid Aadhaar number checksum.'),
        )
    return cleaned


def validate_password_complexity(value):
    if len(value) < 8:
        raise ValidationError(_('Password must be at least 8 characters long.'))
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('Password must contain at least one uppercase letter.'))
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('Password must contain at least one lowercase letter.'))
    if not re.search(r'\d', value):
        raise ValidationError(_('Password must contain at least one digit.'))
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]', value):
        raise ValidationError(_('Password must contain at least one special character.'))
    common_patterns = [
        r'password', r'123456', r'qwerty', r'abc123', r'letmein',
        r'admin', r'welcome', r'monkey', r'dragon', r'master',
    ]
    for pattern in common_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            raise ValidationError(_('Password contains a common pattern and is too weak.'))
    return value


def validate_pincode(value):
    cleaned = re.sub(r'\s', '', value)
    if not re.match(r'^\d{6}$', cleaned):
        raise ValidationError(_('Pincode must be exactly 6 digits.'))
    return cleaned


def validate_pan_number(value):
    cleaned = value.upper().strip()
    if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', cleaned):
        raise ValidationError(_('Enter a valid PAN number (e.g., ABCDE1234F).'))
    return cleaned


def validate_gst_number(value):
    cleaned = value.upper().strip()
    if not re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z]\d$', cleaned):
        raise ValidationError(_('Enter a valid GST number.'))
    return cleaned
