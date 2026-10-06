"""Tests for Phase 1.2 services."""

from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

from .models import (
    VendorLead, VendorProfile, MarketProduct, BoothVariant, AddOn,
    Invoice, InvoiceLineItem, Payment, InventoryHold, Activity, AuditLog
)
from .services.duplicate_detection import DuplicateDetectionService
from .services.activities import ActivityRecordingService
from .services.status_transitions import StatusTransitionService
from .services.payments import PaymentProcessingService
from .services.inventory import InventoryManagementService


class DuplicateDetectionTests(TestCase):
    """Test duplicate vendor detection."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

        self.lead1 = VendorLead.objects.create(
            business_name='Test Brand',
            email='test@example.com',
            phone_number='555-1234',
            instagram_handle='testbrand',
            lead_source='Instagram',
            interest_level='hot'
        )
        self.profile1 = VendorProfile.objects.create(lead=self.lead1)

    def test_find_duplicates_by_email(self):
        """Find duplicate by matching email."""
        lead2 = VendorLead.objects.create(
            business_name='Different Name',
            email='test@example.com',  # Same email
            phone_number='555-9999',
            lead_source='Email',
            interest_level='warm'
        )
        profile2 = VendorProfile.objects.create(lead=lead2)

        duplicates = DuplicateDetectionService.find_duplicates_by_email('test@example.com')
        self.assertEqual(len(duplicates), 2)

    def test_find_duplicates_by_instagram(self):
        """Find duplicate by matching Instagram handle."""
        lead2 = VendorLead.objects.create(
            business_name='Another Brand',
            email='another@example.com',
            instagram_handle='testbrand',  # Same handle
            lead_source='Instagram',
            interest_level='cold'
        )
        profile2 = VendorProfile.objects.create(lead=lead2)

        duplicates = DuplicateDetectionService.find_duplicates_by_instagram('testbrand')
        self.assertEqual(len(duplicates), 2)

    def test_normalize_functions(self):
        """Test normalization of contact info."""
        self.assertEqual(
            DuplicateDetectionService.normalize_instagram('@TestBrand'),
            'testbrand'
        )
        self.assertEqual(
            DuplicateDetectionService.normalize_email('TEST@EXAMPLE.COM'),
            'test@example.com'
        )
        self.assertEqual(
            DuplicateDetectionService.normalize_phone('(555) 123-4567'),
            '5551234567'
        )


class ActivityRecordingTests(TestCase):
    """Test activity recording."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.lead = VendorLead.objects.create(
            business_name='Test Brand',
            email='test@example.com',
            lead_source='Instagram',
            interest_level='hot'
        )
        self.profile = VendorProfile.objects.create(lead=self.lead)

    def test_record_activity(self):
        """Record activity event."""
        activity = ActivityRecordingService.record_activity(
            self.profile,
            'lead_registered',
            'New lead registered',
            self.user
        )

        self.assertEqual(activity.profile, self.profile)
        self.assertEqual(activity.activity_type, 'lead_registered')
        self.assertEqual(activity.actor, self.user)
        self.assertIsNotNone(activity.created_at)

    def test_activity_updates_last_activity_at(self):
        """Recording activity updates profile's last_activity_at."""
        self.assertIsNone(self.profile.last_activity_at)

        ActivityRecordingService.record_lead_registered(self.profile, self.user)

        self.profile.refresh_from_db()
        self.assertIsNotNone(self.profile.last_activity_at)


class StatusTransitionTests(TestCase):
    """Test status transitions."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.lead = VendorLead.objects.create(
            business_name='Test Brand',
            email='test@example.com',
            lead_source='Instagram',
            interest_level='hot'
        )
        self.profile = VendorProfile.objects.create(lead=self.lead)

    def test_qualification_transition(self):
        """Test qualification status transition."""
        self.assertEqual(self.profile.qualification_status, 'unreviewed')

        StatusTransitionService.change_qualification_status(
            self.profile, 'contact_needed', 'Need to call vendor', self.user
        )

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.qualification_status, 'contact_needed')

    def test_invalid_transition_raises_error(self):
        """Invalid transition raises ValueError."""
        self.profile.qualification_status = 'qualified'
        self.profile.save()

        # qualified -> contact_needed is invalid
        with self.assertRaises(ValueError):
            StatusTransitionService.change_qualification_status(
                self.profile, 'contact_needed', '', self.user
            )

    def test_status_change_creates_audit_log(self):
        """Status change creates audit log entry."""
        StatusTransitionService.change_qualification_status(
            self.profile, 'qualified', 'Vendor approved', self.user
        )

        audit = AuditLog.objects.filter(profile=self.profile).first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.event_type, 'status_change')
        self.assertIn('qualified', audit.description)


class PaymentProcessingTests(TestCase):
    """Test payment processing."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.lead = VendorLead.objects.create(
            business_name='Test Brand',
            email='test@example.com',
            lead_source='Instagram',
            interest_level='hot'
        )
        self.profile = VendorProfile.objects.create(lead=self.lead)

        # Create market and invoice
        self.market = MarketProduct.objects.create(
            name='October Market',
            saturday_date=date.today() + timedelta(days=7),
            sunday_date=date.today() + timedelta(days=8),
            booking_opening_date=date.today(),
            booking_closing_date=date.today() + timedelta(days=6)
        )

        self.invoice = Invoice.objects.create(
            profile=self.profile,
            market=self.market,
            invoice_number='INV-001',
            recipient_email='vendor@example.com',
            subtotal=Decimal('500.00'),
            total=Decimal('500.00'),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=14)
        )

    def test_record_payment(self):
        """Record payment against invoice."""
        # Set invoice to sent status first (required before payment can be recorded)
        self.invoice.status = 'invoice_sent'
        self.invoice.save()

        self.assertEqual(self.invoice.amount_paid, Decimal('0'))

        payment, updated_invoice = PaymentProcessingService.record_payment(
            self.invoice,
            Decimal('500.00'),
            date.today(),
            'bank_transfer',
            'REF-123',
            'Payment received',
            self.user
        )

        self.assertEqual(payment.amount, Decimal('500.00'))
        self.assertEqual(updated_invoice.amount_paid, Decimal('500.00'))
        self.assertEqual(updated_invoice.status, 'paid')

    def test_partial_payment(self):
        """Record partial payment."""
        self.invoice.status = 'invoice_sent'
        self.invoice.save()

        payment, invoice = PaymentProcessingService.record_payment(
            self.invoice,
            Decimal('250.00'),
            date.today(),
            'bank_transfer',
            'REF-123',
            '',
            self.user
        )

        self.assertEqual(invoice.status, 'partially_paid')
        self.assertEqual(invoice.balance_due, Decimal('250.00'))

    def test_payment_exceeding_balance_raises_error(self):
        """Payment exceeding balance raises error."""
        self.invoice.status = 'invoice_sent'
        self.invoice.save()

        with self.assertRaises(ValueError):
            PaymentProcessingService.record_payment(
                self.invoice,
                Decimal('600.00'),  # More than invoice total
                date.today(),
                'bank_transfer',
                '',
                '',
                self.user
            )


class InventoryManagementTests(TestCase):
    """Test inventory hold management."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.lead = VendorLead.objects.create(
            business_name='Test Brand',
            email='test@example.com',
            lead_source='Instagram',
            interest_level='hot'
        )
        self.profile = VendorProfile.objects.create(lead=self.lead)

        # Create market and booth
        self.market = MarketProduct.objects.create(
            name='October Market',
            saturday_date=date.today() + timedelta(days=7),
            sunday_date=date.today() + timedelta(days=8),
            booking_opening_date=date.today(),
            booking_closing_date=date.today() + timedelta(days=6),
            total_booth_capacity=10
        )

        self.booth = BoothVariant.objects.create(
            market=self.market,
            name='8x12 Booth',
            price=Decimal('530.00'),
            capacity=1
        )

        self.invoice = Invoice.objects.create(
            profile=self.profile,
            market=self.market,
            booth_variant=self.booth,
            invoice_number='INV-001',
            recipient_email='vendor@example.com',
            subtotal=Decimal('530.00'),
            total=Decimal('530.00'),
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=14)
        )

    def test_create_inventory_hold(self):
        """Create inventory hold."""
        hold = InventoryManagementService.create_hold(
            self.invoice, self.booth, hold_duration_hours=24, actor=self.user
        )

        self.assertEqual(hold.invoice, self.invoice)
        self.assertEqual(hold.booth_variant, self.booth)
        self.assertFalse(hold.is_expired)

    def test_hold_has_expiry_date(self):
        """Hold has correct expiry time."""
        hold = InventoryManagementService.create_hold(
            self.invoice, self.booth, hold_duration_hours=24, actor=self.user
        )

        self.assertIsNotNone(hold.expires_at)
        delta = hold.expires_at - hold.held_at
        self.assertAlmostEqual(delta.total_seconds(), 24 * 3600, delta=60)

    def test_booth_availability(self):
        """Check booth availability."""
        self.assertTrue(self.booth.available_quantity() > 0)

        # Create hold
        hold = InventoryManagementService.create_hold(
            self.invoice, self.booth, actor=self.user
        )

        # Booth should now show reduced availability
        available = self.booth.available_quantity()
        self.assertEqual(available, 0)  # 1 capacity - 1 held = 0
