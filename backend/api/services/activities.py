"""Activity recording service."""

from django.utils import timezone
from django.contrib.auth.models import User
from api.models import Activity, VendorProfile


class ActivityRecordingService:
    """Record immutable activity events for vendors."""

    @staticmethod
    def record_activity(
        profile,
        activity_type,
        description='',
        actor=None,
        related_object_id=None,
        related_object_type='',
        metadata=None
    ):
        """Record an activity event for a vendor profile.

        Args:
            profile: VendorProfile instance
            activity_type: One of ACTIVITY_TYPES choices
            description: Human-readable description
            actor: User who triggered the activity
            related_object_id: ID of related object (e.g., invoice ID)
            related_object_type: Type of related object (e.g., 'invoice')
            metadata: Dict of additional structured data

        Returns:
            Activity instance
        """
        activity = Activity.objects.create(
            profile=profile,
            activity_type=activity_type,
            description=description,
            actor=actor,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            metadata=metadata or {}
        )

        # Update profile's last activity timestamp
        profile.last_activity_at = timezone.now()
        profile.save(update_fields=['last_activity_at'])

        return activity

    @staticmethod
    def record_lead_registered(profile, actor=None):
        """Record that a vendor lead was registered."""
        return ActivityRecordingService.record_activity(
            profile,
            'lead_registered',
            f'Vendor lead registered: {profile.lead.business_name}',
            actor
        )

    @staticmethod
    def record_lead_imported(profile, actor=None):
        """Record that a lead was imported from CSV."""
        return ActivityRecordingService.record_activity(
            profile,
            'lead_imported',
            f'Lead imported from CSV: {profile.lead.business_name}',
            actor
        )

    @staticmethod
    def record_application_submitted(profile, actor=None):
        """Record application submission."""
        return ActivityRecordingService.record_activity(
            profile,
            'application_submitted',
            f'Application submitted for {profile.lead.business_name}',
            actor
        )

    @staticmethod
    def record_call_attempted(profile, description='', actor=None):
        """Record a call attempt."""
        return ActivityRecordingService.record_activity(
            profile,
            'call_attempted',
            description or f'Call attempted to {profile.lead.business_name}',
            actor
        )

    @staticmethod
    def record_call_completed(profile, description='', actor=None):
        """Record a completed call."""
        return ActivityRecordingService.record_activity(
            profile,
            'call_completed',
            description or f'Call completed with {profile.lead.business_name}',
            actor
        )

    @staticmethod
    def record_qualification_changed(profile, old_status, new_status, actor=None):
        """Record a qualification status change."""
        return ActivityRecordingService.record_activity(
            profile,
            'qualification_changed',
            f'Qualification changed from {old_status} to {new_status}',
            actor,
            metadata={'old_status': old_status, 'new_status': new_status}
        )

    @staticmethod
    def record_application_reviewed(profile, decision, actor=None):
        """Record application review."""
        return ActivityRecordingService.record_activity(
            profile,
            'application_reviewed',
            f'Application reviewed: {decision}',
            actor,
            metadata={'decision': decision}
        )

    @staticmethod
    def record_invoice_created(profile, invoice, actor=None):
        """Record invoice creation."""
        return ActivityRecordingService.record_activity(
            profile,
            'invoice_created',
            f'Invoice created: {invoice.invoice_number}',
            actor,
            related_object_id=invoice.id,
            related_object_type='invoice'
        )

    @staticmethod
    def record_invoice_sent(profile, invoice, actor=None):
        """Record invoice sent."""
        return ActivityRecordingService.record_activity(
            profile,
            'invoice_sent',
            f'Invoice sent: {invoice.invoice_number}',
            actor,
            related_object_id=invoice.id,
            related_object_type='invoice'
        )

    @staticmethod
    def record_payment_recorded(profile, payment, actor=None):
        """Record payment received."""
        return ActivityRecordingService.record_activity(
            profile,
            'payment_recorded',
            f'Payment received: ${payment.amount} via {payment.payment_method}',
            actor,
            related_object_id=payment.id,
            related_object_type='payment',
            metadata={'amount': str(payment.amount), 'method': payment.payment_method}
        )

    @staticmethod
    def record_booking_confirmed(profile, booking, actor=None):
        """Record booking confirmation."""
        return ActivityRecordingService.record_activity(
            profile,
            'booking_confirmed',
            f'Booking confirmed for {booking.market.name}',
            actor,
            related_object_id=booking.id,
            related_object_type='booking'
        )

    @staticmethod
    def record_attendance(profile, booking, saturday_status, sunday_status, actor=None):
        """Record attendance."""
        return ActivityRecordingService.record_activity(
            profile,
            'attendance_recorded',
            f'Attendance recorded: Saturday {saturday_status}, Sunday {sunday_status}',
            actor,
            related_object_id=booking.id,
            related_object_type='booking',
            metadata={'saturday': saturday_status, 'sunday': sunday_status}
        )
