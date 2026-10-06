"""Inventory management service."""

from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from api.models import InventoryHold, InventoryHoldAddOn, Invoice, Booking, Attendance


class InventoryManagementService:
    """Manage booth and add-on inventory holds and confirmations."""

    @staticmethod
    def create_hold(invoice, booth_variant, add_ons=None, hold_duration_hours=24, actor=None):
        """Create a temporary inventory hold.

        Args:
            invoice: Invoice instance
            booth_variant: BoothVariant to hold
            add_ons: List of AddOn instances (optional)
            hold_duration_hours: How long to hold (default 24)
            actor: User creating the hold

        Returns:
            InventoryHold instance
        """
        expires_at = timezone.now() + timedelta(hours=hold_duration_hours)

        with transaction.atomic():
            hold = InventoryHold.objects.create(
                invoice=invoice,
                booth_variant=booth_variant,
                expires_at=expires_at,
                created_by=actor
            )

            # Add add-ons to hold if provided
            if add_ons:
                for add_on in add_ons:
                    quantity = 1  # Default quantity
                    InventoryHoldAddOn.objects.create(hold=hold, add_on=add_on, quantity=quantity)

        return hold

    @staticmethod
    def check_booth_availability(booth_variant, exclude_hold_id=None):
        """Check if a booth is available.

        Returns:
            (is_available, reason)
        """
        available = booth_variant.available_quantity()

        if available <= 0:
            return False, f'Booth {booth_variant.name} has no available capacity'

        return True, 'Available'

    @staticmethod
    def check_add_on_availability(add_on, quantity=1, exclude_hold_id=None):
        """Check if an add-on is available.

        Returns:
            (is_available, reason)
        """
        if not add_on.has_inventory:
            return True, 'Add-on has unlimited inventory'

        available = add_on.available_inventory()

        if available is not None and available < quantity:
            return False, f'{add_on.name} has {available} units available, but {quantity} were requested'

        return True, 'Available'

    @staticmethod
    def confirm_hold(hold, actor=None):
        """Convert a hold to a confirmed booking.

        This is called when payment is fully received.
        """
        with transaction.atomic():
            # Mark hold as expired (so it's no longer counted as held)
            hold.is_expired = True
            hold.save(update_fields=['is_expired'])

            # Create booking with confirmed status
            booking = Booking.objects.create(
                profile=hold.invoice.profile,
                invoice=hold.invoice,
                market=hold.invoice.market,
                booth_variant=hold.booth_variant,
                status='confirmed',
                confirmed_at=timezone.now()
            )

            # Add add-ons to booking
            for hold_add_on in hold.add_ons.through.objects.filter(hold=hold):
                booking.add_ons.add(hold_add_on.add_on)

            # Create attendance record
            Attendance.objects.create(booking=booking)

        return booking

    @staticmethod
    def expire_holds():
        """Expire all holds that have passed their expiry time.

        Called by background job or management command.
        """
        now = timezone.now()
        expired = InventoryHold.objects.filter(expires_at__lte=now, is_expired=False)
        count = expired.update(is_expired=True)
        return count

    @staticmethod
    def extend_hold(hold, hours=24, actor=None):
        """Extend a hold expiration time.

        Requires authorization.
        """
        old_expires = hold.expires_at
        hold.expires_at = timezone.now() + timedelta(hours=hours)
        hold.save(update_fields=['expires_at'])

        return hold

    @staticmethod
    def release_inventory(hold, actor=None):
        """Manually release a hold's inventory."""
        hold.is_expired = True
        hold.save(update_fields=['is_expired'])
