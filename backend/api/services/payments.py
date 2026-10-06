"""Payment processing service."""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from api.models import Invoice, Payment, VendorProfile
from api.services.inventory import InventoryManagementService
from api.services.activities import ActivityRecordingService
from api.services.status_transitions import StatusTransitionService


class PaymentProcessingService:
    """Handle payment recording and processing."""

    @staticmethod
    def record_payment(
        invoice,
        amount,
        payment_date,
        payment_method,
        transaction_reference='',
        internal_note='',
        recorded_by=None,
        receipt=None
    ):
        """Record a payment against an invoice.

        Args:
            invoice: Invoice instance
            amount: Decimal amount paid
            payment_date: Date of payment
            payment_method: Payment method (check PAYMENT_METHODS)
            transaction_reference: Reference/confirmation number
            internal_note: Internal notes about the payment
            recorded_by: User recording the payment
            receipt: Optional file upload

        Returns:
            Payment instance and updated Invoice
        """
        amount = Decimal(str(amount))

        if amount <= 0:
            raise ValueError('Payment amount must be greater than 0')

        if amount > invoice.balance_due and invoice.balance_due > 0:
            raise ValueError(f'Payment amount ${amount} exceeds balance due ${invoice.balance_due}')

        with transaction.atomic():
            # Create payment record
            payment = Payment.objects.create(
                invoice=invoice,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                transaction_reference=transaction_reference,
                internal_note=internal_note,
                recorded_by=recorded_by,
                receipt=receipt
            )

            # Update invoice amount paid
            invoice.amount_paid += amount
            new_status = invoice.status

            # Determine new invoice status
            if invoice.amount_paid >= invoice.total:
                new_status = 'paid'
            elif invoice.amount_paid > 0:
                new_status = 'partially_paid'
            else:
                new_status = 'invoice_sent'

            invoice.status = new_status
            invoice.save(update_fields=['amount_paid', 'status'])

            # If fully paid, confirm the booking
            if invoice.is_fully_paid() and hasattr(invoice, 'inventory_hold'):
                hold = invoice.inventory_hold
                booking = InventoryManagementService.confirm_hold(hold, recorded_by)

                # Update profile booking status
                profile = invoice.profile
                StatusTransitionService.change_booking_status(
                    profile,
                    'confirmed',
                    'Payment received - booking confirmed',
                    recorded_by
                )

            # Update profile payment status (direct update, not via status transitions)
            profile = invoice.profile
            if new_status == 'paid':
                profile.payment_status = 'paid'
            elif new_status == 'partially_paid':
                profile.payment_status = 'partially_paid'
            elif new_status == 'invoice_sent':
                profile.payment_status = 'invoice_sent'
            profile.save(update_fields=['payment_status'])

            # Record activity
            ActivityRecordingService.record_payment_recorded(invoice.profile, payment, recorded_by)

        return payment, invoice

    @staticmethod
    def reverse_payment(payment, actor=None):
        """Reverse a recorded payment.

        Only authorized users can reverse payments.
        """
        invoice = payment.invoice

        with transaction.atomic():
            # Subtract from invoice
            invoice.amount_paid -= payment.amount

            # Determine new status
            if invoice.amount_paid > 0:
                invoice.status = 'partially_paid'
            else:
                invoice.status = 'invoice_sent'

            invoice.save(update_fields=['amount_paid', 'status'])

            # Delete payment
            payment.delete()

            # If booking was confirmed, revert it
            if hasattr(invoice, 'booking') and invoice.booking.status == 'confirmed':
                booking = invoice.booking
                booking.status = 'reserved'
                booking.save(update_fields=['status'])

        return invoice

    @staticmethod
    def calculate_invoice_totals(invoice):
        """Calculate invoice totals from line items.

        Returns:
            (subtotal, total)
        """
        line_items = invoice.line_items.all()
        subtotal = sum(item.subtotal for item in line_items)
        total = subtotal - invoice.discount + invoice.tax
        return subtotal, max(total, Decimal('0'))
