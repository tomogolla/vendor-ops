"""Status transition service."""

from django.db import transaction
from api.models import VendorProfile, AuditLog
from api.services.activities import ActivityRecordingService


class StatusTransitionService:
    """Handle status changes with audit logging."""

    # Valid state transitions
    QUALIFICATION_TRANSITIONS = {
        'unreviewed': ['contact_needed', 'qualified', 'not_qualified'],
        'contact_needed': ['discovery_scheduled', 'qualified', 'not_qualified'],
        'discovery_scheduled': ['qualified', 'not_qualified'],
        'qualified': ['not_qualified'],
        'not_qualified': ['contact_needed', 'discovery_scheduled'],
    }

    APPLICATION_TRANSITIONS = {
        'new': ['under_review', 'more_information_required'],
        'under_review': ['accepted', 'waitlisted', 'declined', 'more_information_required'],
        'more_information_required': ['under_review', 'declined'],
        'accepted': ['waitlisted'],
        'waitlisted': ['accepted'],
        'declined': [],
    }

    PAYMENT_TRANSITIONS = {
        'not_invoiced': ['invoice_draft'],
        'invoice_draft': ['invoice_sent', 'cancelled'],
        'invoice_sent': ['payment_pending', 'cancelled'],
        'payment_pending': ['partially_paid', 'paid', 'overdue', 'cancelled'],
        'partially_paid': ['paid', 'overdue', 'cancelled'],
        'paid': [],
        'overdue': ['paid', 'cancelled'],
        'cancelled': [],
        'refunded': [],
    }

    BOOKING_TRANSITIONS = {
        'not_booked': ['reserved'],
        'reserved': ['confirmed', 'cancelled'],
        'confirmed': ['preparing', 'cancelled'],
        'preparing': ['attended', 'no_show'],
        'attended': [],
        'no_show': [],
        'cancelled': [],
    }

    @classmethod
    def change_qualification_status(cls, profile, new_status, reason='', actor=None):
        """Change qualification status with validation and audit."""
        current = profile.qualification_status

        # Validate transition
        if current == new_status:
            return profile  # No change needed

        if new_status not in cls.QUALIFICATION_TRANSITIONS.get(current, []):
            raise ValueError(
                f'Cannot transition from {current} to {new_status}. '
                f'Valid transitions: {cls.QUALIFICATION_TRANSITIONS.get(current, [])}'
            )

        old_status = current
        with transaction.atomic():
            profile.qualification_status = new_status
            profile.save(update_fields=['qualification_status'])

            # Record audit log
            AuditLog.objects.create(
                profile=profile,
                event_type='status_change',
                description=f'Qualification status changed from {old_status} to {new_status}. Reason: {reason}',
                actor=actor,
                changes={'from': old_status, 'to': new_status, 'reason': reason}
            )

            # Record activity
            ActivityRecordingService.record_qualification_changed(profile, old_status, new_status, actor)

        return profile

    @classmethod
    def change_application_status(cls, profile, new_status, reason='', actor=None):
        """Change application status with validation and audit."""
        current = profile.application_status

        # Validate transition
        if current == new_status:
            return profile

        if new_status not in cls.APPLICATION_TRANSITIONS.get(current, []):
            raise ValueError(
                f'Cannot transition from {current} to {new_status}. '
                f'Valid transitions: {cls.APPLICATION_TRANSITIONS.get(current, [])}'
            )

        old_status = current
        with transaction.atomic():
            profile.application_status = new_status
            profile.save(update_fields=['application_status'])

            # Record audit log
            AuditLog.objects.create(
                profile=profile,
                event_type='application_decision',
                description=f'Application status changed from {old_status} to {new_status}. Reason: {reason}',
                actor=actor,
                changes={'from': old_status, 'to': new_status, 'reason': reason}
            )

            # Record activity
            ActivityRecordingService.record_activity(
                profile,
                'application_reviewed',
                f'Application status changed to {new_status}. Reason: {reason}',
                actor,
                metadata={'new_status': new_status, 'reason': reason}
            )

        return profile

    @classmethod
    def change_payment_status(cls, profile, new_status, reason='', actor=None):
        """Change payment status with validation and audit."""
        current = profile.payment_status

        # Validate transition
        if current == new_status:
            return profile

        if new_status not in cls.PAYMENT_TRANSITIONS.get(current, []):
            raise ValueError(
                f'Cannot transition from {current} to {new_status}. '
                f'Valid transitions: {cls.PAYMENT_TRANSITIONS.get(current, [])}'
            )

        old_status = current
        with transaction.atomic():
            profile.payment_status = new_status
            profile.save(update_fields=['payment_status'])

            # Record audit log
            AuditLog.objects.create(
                profile=profile,
                event_type='status_change',
                description=f'Payment status changed from {old_status} to {new_status}. Reason: {reason}',
                actor=actor,
                changes={'from': old_status, 'to': new_status, 'reason': reason}
            )

        return profile

    @classmethod
    def change_booking_status(cls, profile, new_status, reason='', actor=None):
        """Change booking status with validation and audit."""
        current = profile.booking_status

        # Validate transition
        if current == new_status:
            return profile

        if new_status not in cls.BOOKING_TRANSITIONS.get(current, []):
            raise ValueError(
                f'Cannot transition from {current} to {new_status}. '
                f'Valid transitions: {cls.BOOKING_TRANSITIONS.get(current, [])}'
            )

        old_status = current
        with transaction.atomic():
            profile.booking_status = new_status
            profile.save(update_fields=['booking_status'])

            # Record audit log
            AuditLog.objects.create(
                profile=profile,
                event_type='status_change',
                description=f'Booking status changed from {old_status} to {new_status}. Reason: {reason}',
                actor=actor,
                changes={'from': old_status, 'to': new_status, 'reason': reason}
            )

        return profile
