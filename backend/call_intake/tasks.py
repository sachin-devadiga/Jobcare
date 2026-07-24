import logging
from celery import shared_task
from django.conf import settings
from .models import CallSession
from .utils import generate_intake_pdf
from notifications.services import EmailNotificationService

logger = logging.getLogger('jobcare')

@shared_task(name='call_intake.tasks.process_completed_intake')
def process_completed_intake(session_id):
    """
    Background task to generate PDF and notify the backend team.
    """
    try:
        session = CallSession.objects.get(id=session_id)
        
        # 1. Generate and save the PDF
        logger.info(f"Generating PDF for session {session_id}")
        generate_intake_pdf(session)
        session.save() # Update the record with the file path
        
        # 2. Notify the backend team
        email_service = EmailNotificationService()
        subject = f"New Voice Intake Completed: {session.phone_number}"
        
        # In a real app, 'backend_team_emails' would be in settings
        admin_emails = [admin[1] for admin in settings.ADMINS] if settings.ADMINS else ['admin@jobcare.voice']
        
        context = {
            'phone_number': session.phone_number,
            'language': session.get_language_display(),
            'timestamp': session.completed_at,
            'pdf_url': session.pdf_file.url if session.pdf_file else None,
        }
        
        # Simplified email body
        body = f"""
        A new voice intake session has been completed.
        
        Phone Number: {session.phone_number}
        Language: {session.get_language_display()}
        Completed At: {session.completed_at}
        
        You can review the details in the Django Admin or download the attached PDF.
        """
        
        email_service.send_email(
            subject=subject,
            recipient_list=admin_emails,
            plain_message=body
        )
        
        logger.info(f"Successfully processed intake for session {session_id}")
        
    except CallSession.DoesNotExist:
        logger.error(f"CallSession {session_id} not found")
    except Exception as e:
        logger.error(f"Error processing completed intake {session_id}: {str(e)}", exc_info=True)
