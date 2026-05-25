"""
Notification service for multi-channel patient and stakeholder communications.
Supports SMS (Twilio), Email (SendGrid), and in-app notifications.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class NotificationService:
    """Multi-channel notification service with fallback mechanisms."""

    def __init__(self, twilio_sid: Optional[str] = None,
                 twilio_token: Optional[str] = None,
                 twilio_phone: Optional[str] = None,
                 sendgrid_key: Optional[str] = None,
                 from_email: Optional[str] = None):
        self.twilio_sid = twilio_sid
        self.twilio_token = twilio_token
        self.twilio_phone = twilio_phone
        self.sendgrid_key = sendgrid_key
        self.from_email = from_email
        self._init_clients()

    def _init_clients(self):
        self.twilio_client = None
        self.sendgrid_client = None

        if self.twilio_sid and self.twilio_token:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(self.twilio_sid, self.twilio_token)
                logger.info("Twilio client initialized")
            except Exception as e:
                logger.warning(f"Twilio init failed: {e}")

        if self.sendgrid_key:
            try:
                import sendgrid
                self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=self.sendgrid_key)
                logger.info("SendGrid client initialized")
            except Exception as e:
                logger.warning(f"SendGrid init failed: {e}")

    async def send_sms(self, to: str, message: str) -> Dict[str, Any]:
        """Send SMS notification with fallback logging."""
        result = {"to": to, "status": "sent", "channel": "sms", "timestamp": datetime.utcnow().isoformat()}
        if self.twilio_client:
            try:
                msg = self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_phone,
                    to=to
                )
                result["message_sid"] = msg.sid
                logger.info(f"SMS sent to {to}: {msg.sid}")
            except Exception as e:
                logger.error(f"Twilio SMS failed: {e}")
                result["status"] = "failed"
                result["error"] = str(e)
        else:
            logger.info(f"[MOCK SMS] To: {to} | Message: {message[:50]}...")
        return result

    async def send_email(self, to: str, subject: str, html_content: str) -> Dict[str, Any]:
        """Send email notification with fallback logging."""
        result = {"to": to, "status": "sent", "channel": "email", "timestamp": datetime.utcnow().isoformat()}
        if self.sendgrid_client:
            try:
                from sendgrid.helpers.mail import Mail
                message = Mail(
                    from_email=self.from_email,
                    to_emails=to,
                    subject=subject,
                    html_content=html_content
                )
                response = self.sendgrid_client.send(message)
                result["status_code"] = response.status_code
                logger.info(f"Email sent to {to}: {response.status_code}")
            except Exception as e:
                logger.error(f"SendGrid email failed: {e}")
                result["status"] = "failed"
                result["error"] = str(e)
        else:
            logger.info(f"[MOCK EMAIL] To: {to} | Subject: {subject}")
        return result

    async def send_in_app_notification(self, user_id: str,
                                        title: str,
                                        message: str,
                                        notification_type: str = "info") -> Dict[str, Any]:
        """Create in-app notification."""
        from app.models.alert import Alert
        alert = Alert(
            alert_id=f"NOTIF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(user_id) % 10000:04d}",
            patient_id=user_id,
            patient_name="",
            alert_type=notification_type,
            severity="info",
            message=message,
        )
        try:
            await alert.insert()
            logger.info(f"In-app notification created for {user_id}")
        except Exception as e:
            logger.error(f"In-app notification failed: {e}")
        return {"user_id": user_id, "title": title, "status": "created"}

    async def send_appointment_reminder(self, patient_phone: Optional[str],
                                         patient_email: Optional[str],
                                         appointment_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send multi-channel appointment reminders."""
        results = []
        patient_name = appointment_data.get("patient_name", "Patient")
        appt_type = appointment_data.get("appointment_type", "appointment")
        facility = appointment_data.get("facility_name", "facility")
        scheduled = appointment_data.get("scheduled_date", "")

        message = f"Dear {patient_name}, reminder: {appt_type} at {facility} on {scheduled}."
        subject = f"Appointment Reminder - {appt_type}"

        if patient_phone:
            results.append(await self.send_sms(patient_phone, message))
        if patient_email:
            html = f"<h2>Appointment Reminder</h2><p>{message}</p>"
            results.append(await self.send_email(patient_email, subject, html))
        results.append(await self.send_in_app_notification(
            appointment_data.get("patient_id", ""), subject, message, "reminder"
        ))
        return results

    async def send_emergency_alert(self, notify_list: List[Dict[str, str]],
                                    patient_name: str,
                                    severity: str,
                                    details: str) -> List[Dict[str, Any]]:
        """Send emergency alerts to stakeholders via appropriate channels."""
        results = []
        for contact in notify_list:
            role = contact.get("role", "staff")
            phone = contact.get("phone")
            email = contact.get("email")
            message = f"EMERGENCY ALERT ({severity.upper()}): Patient {patient_name} - {details}"

            if phone:
                results.append(await self.send_sms(phone, message))
            if email:
                html = f"<h1>🚨 Emergency Alert</h1><p><strong>Severity:</strong> {severity}</p><p><strong>Patient:</strong> {patient_name}</p><p><strong>Details:</strong> {details}</p>"
                results.append(await self.send_email(email, f"EMERGENCY - {patient_name}", html))
        return results
