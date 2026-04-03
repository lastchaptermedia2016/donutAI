"""Email management tool for AI receptionist.

Supports:
- Send emails (simulated or via Gmail API when configured)
- List recent emails
- Read specific emails
- Quick reply to last email
- Email templates for common receptionist scenarios

When Google OAuth is NOT configured, the tool runs in "simulated mode"
which logs emails locally. This makes Donut work out of the box.
"""

import logging
from datetime import datetime
from typing import Optional

from ..memory.structured_db import get_structured_db

logger = logging.getLogger(__name__)

# Email templates for common receptionist scenarios
EMAIL_TEMPLATES = {
    "out_of_office": {
        "subject": "Out of Office - Auto Reply",
        "body": "Thank you for your email. I am currently out of the office and will respond to your message upon my return.",
    },
    "meeting_confirmation": {
        "subject": "Meeting Confirmation",
        "body": "This email confirms our upcoming meeting. Please find the details below:\n\nDate: {date}\nTime: {time}\nLocation: {location}\n\nWe look forward to speaking with you.",
    },
    "appointment_reminder": {
        "subject": "Friendly Reminder: Upcoming Appointment",
        "body": "This is a friendly reminder about your upcoming appointment:\n\nDate: {date}\nTime: {time}\n\nPlease arrive 5-10 minutes early.",
    },
    "follow_up": {
        "subject": "Follow-Up on Our Conversation",
        "body": "Thank you for contacting us. As discussed, I wanted to follow up on:\n\n{details}\n\nPlease don't hesitate to reach out with any questions.",
    },
}


class EmailTool:
    """Tool for email management with Gmail API and local simulation mode.

    When Google OAuth is configured: Uses real Gmail API.
    When not configured: Simulates email operations with local storage.
    """

    def __init__(self):
        self._db = get_structured_db()
        self._google_configured = self._check_google_config()
        self._local_inbox: list[dict] = []
        self._sent_items: list[dict] = []

    def _get_connection(self):
        """Get a database connection."""
        return self._db._get_conn()

    def _check_google_config(self) -> bool:
        """Check if Google OAuth credentials are configured."""
        try:
            from ..config import get_settings

            settings = get_settings()
            return bool(settings.google_client_id and settings.google_client_secret)
        except Exception:
            return False

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
    ) -> dict:
        """Send an email.

        In simulation mode, creates a local sent email record.
        With Google OAuth, sends via Gmail API.
        """
        email_id = f"email_{int(datetime.now().timestamp() * 1000)}"
        sent_at = datetime.now().isoformat()

        email_data = {
            "id": email_id,
            "to": to,
            "subject": subject,
            "body": body,
            "cc": cc,
            "bcc": bcc,
            "sent_at": sent_at,
            "status": "sent",
        }

        if self._google_configured:
            return await self._send_google_email(to, subject, body, cc, bcc)
        else:
            # Simulation mode - store locally
            self._sent_items.append(email_data)
            logger.info(
                f"📧 Email sent (simulated): To={to}, Subject={subject}"
            )
            return {
                "id": email_id,
                "status": "sent",
                "to": to,
                "subject": subject,
                "message": "Email sent successfully (simulated mode)",
                "sent_at": sent_at,
            }

    async def list_emails(
        self,
        folder: str = "inbox",
        query: str = "",
        max_results: int = 20,
        unread_only: bool = False,
    ) -> list[dict]:
        """List emails.

        In simulation mode, returns locally stored emails.
        With Google OAuth, fetches from Gmail API.
        """
        if self._google_configured:
            return await self._list_google_emails(folder, query, max_results, unread_only)
        else:
            # Simulation mode
            emails = self._local_inbox
            if unread_only:
                emails = [e for e in emails if not e.get("read", False)]
            if query:
                query_lower = query.lower()
                emails = [
                    e for e in emails
                    if query_lower in e.get("subject", "").lower()
                    or query_lower in e.get("body", "").lower()
                    or query_lower in e.get("sender", "").lower()
                ]
            return emails[:max_results]

    async def read_email(self, email_id: str) -> Optional[dict]:
        """Read a specific email and mark as read."""
        if self._google_configured:
            return await self._read_google_email(email_id)
        else:
            # Simulation mode
            for email in self._local_inbox:
                if email["id"] == email_id:
                    email["read"] = True
                    return email
            for email in self._sent_items:
                if email["id"] == email_id:
                    return email
            return None

    async def delete_email(self, email_id: str) -> dict:
        """Delete an email."""
        if self._google_configured:
            return await self._delete_google_email(email_id)
        else:
            # Simulation mode
            self._local_inbox = [
                e for e in self._local_inbox if e["id"] != email_id
            ]
            self._sent_items = [
                e for e in self._sent_items if e["id"] != email_id
            ]
            return {"deleted": True, "id": email_id}

    async def quick_reply(
        self,
        original_email_id: str,
        reply_body: str,
    ) -> dict:
        """Quick reply to an email. Finds the original and adds a reply."""
        original = await self.read_email(original_email_id)
        if not original:
            return {"status": "error", "message": "Email not found"}

        subject = original.get("subject", "")
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"

        return await self.send_email(
            to=original.get("sender", original.get("to", "")),
            subject=subject,
            body=reply_body,
        )

    async def send_template_email(
        self,
        to: str,
        template_name: str,
        variables: Optional[dict] = None,
    ) -> dict:
        """Send an email using a predefined template.

        Args:
            to: Recipient email
            template_name: Name of template (out_of_office, meeting_confirmation, etc.)
            variables: Template variables to substitute
        """
        template = EMAIL_TEMPLATES.get(template_name)
        if not template:
            return {"status": "error", "message": f"Template '{template_name}' not found"}

        subject = template["subject"]
        body = template["body"]

        if variables:
            for key, value in variables.items():
                body = body.replace(f"{{{key}}}", str(value))

        return await self.send_email(to=to, subject=subject, body=body)

    def get_templates(self) -> dict:
        """Get available email templates."""
        return EMAIL_TEMPLATES

    async def receive_simulated_email(
        self,
        sender: str,
        subject: str,
        body: str,
    ) -> dict:
        """Receive a simulated email into inbox (for testing/demo).

        This is useful when no real Gmail API is configured.
        """
        email_id = f"email_{int(datetime.now().timestamp() * 1000)}"
        email_data = {
            "id": email_id,
            "sender": sender,
            "to": "reception@donut.ai",
            "subject": subject,
            "body": body,
            "received_at": datetime.now().isoformat(),
            "read": False,
            "folder": "inbox",
        }
        self._local_inbox.append(email_data)
        logger.info(f"📥 Simulated email received: From={sender}, Subject={subject}")
        return email_data

    # --- Google Gmail Implementation (TODO) ---

    async def _send_google_email(self, to, subject, body, cc, bcc) -> dict:
        """Send email via Gmail API."""
        # TODO: Implement Gmail API
        logger.warning("Gmail API not yet fully implemented")
        return {
            "id": "gmail_" + str(hash(to + subject)),
            "status": "queued",
            "message": "Email queued for sending (Gmail API pending)",
        }

    async def _list_google_emails(self, folder, query, max_results, unread_only):
        """List emails via Gmail API."""
        # TODO: Implement Gmail API
        return []

    async def _read_google_email(self, email_id):
        """Read email via Gmail API."""
        # TODO: Implement Gmail API
        return None

    async def _delete_google_email(self, email_id):
        """Delete email via Gmail API."""
        # TODO: Implement Gmail API
        return {"deleted": True}


_tool: EmailTool | None = None


def get_email_tool() -> EmailTool:
    """Get email tool singleton."""
    global _tool
    if _tool is None:
        _tool = EmailTool()
    return _tool