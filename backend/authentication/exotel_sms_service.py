import logging

import requests

from django.conf import settings

logger = logging.getLogger('jobcare')


class ExotelSMSError(Exception):
    pass


class ExotelSMSNotConfiguredError(ExotelSMSError):
    pass


class ExotelSMSUnavailableError(ExotelSMSError):
    pass


def send_sms(phone_number: str, message: str) -> dict:
    """Send an SMS through Exotel's REST API (HTTP Basic auth, same
    credentials as their Voice API, reused by the IVR feature).

    Returns {'success': True, 'sid': <sid>} on acceptance (HTTP 200 means
    queued, not delivered). Mapped errors raise ExotelSMSError subclasses.
    """
    api_key = settings.EXOTEL_API_KEY
    api_token = settings.EXOTEL_API_TOKEN
    account_sid = settings.EXOTEL_SID
    sender_id = settings.EXOTEL_SMS_SENDER_ID
    subdomain = (settings.EXOTEL_SUBDOMAIN or 'api.exotel.com').strip().rstrip('/')

    if not (api_key and api_token and account_sid and sender_id):
        raise ExotelSMSNotConfiguredError('Exotel SMS is not configured')

    url = f'https://{subdomain}/v1/Accounts/{account_sid}/Sms/send'
    payload = {
        'From': sender_id,
        'To': phone_number,
        'Body': message,
    }
    # DLT params are mandatory for delivery to Indian numbers (TRAI).
    if settings.EXOTEL_DLT_ENTITY_ID:
        payload['DltEntityId'] = settings.EXOTEL_DLT_ENTITY_ID
    if settings.EXOTEL_DLT_TEMPLATE_ID:
        payload['DltTemplateId'] = settings.EXOTEL_DLT_TEMPLATE_ID
    if settings.EXOTEL_SMS_TYPE:
        payload['SmsType'] = settings.EXOTEL_SMS_TYPE

    try:
        response = requests.post(
            url,
            data=payload,
            auth=(api_key, api_token),
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        logger.error(f'Exotel SMS request failed: {e}')
        raise ExotelSMSUnavailableError(
            'Failed to send SMS. Please try again.'
        ) from e

    if response.status_code == 200:
        data = response.json()
        sms_message = data.get('SMSMessage', {})
        sid = sms_message.get('Sid')
        logger.info(f'Exotel SMS queued to {phone_number} sid={sid}')
        return {'success': True, 'sid': sid}

    error_message = 'Failed to send SMS. Please try again.'
    try:
        error_message = response.json().get('RestException', {}).get('Message') or error_message
    except ValueError:
        pass
    logger.error(f'Exotel SMS error {response.status_code} for {phone_number}: {response.text[:200]}')
    if response.status_code == 429:
        raise ExotelSMSUnavailableError('Too many SMS requests. Please try again later.')
    raise ExotelSMSUnavailableError(error_message)