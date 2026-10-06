from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from .models import ApprovalInvoice, CATEGORIES, MarketWeekendBooking, VendorLead
from .test_utils import AuthenticatedAPITestCase


class CallQualificationTests(AuthenticatedAPITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('vendor-leads')
        self.payload = {
            'business_name': 'Test Brand', 'email': 'contact@example.com',
            'vendor_category': CATEGORIES[0], 'lead_source': 'Instagram',
            'interest_level': 'warm', 'vendor_contact_name': 'Jane Doe',
            'website_url': 'https://example.com/catalog',
            'product_category': 'Apparel/Fashion', 'price_point_range': '$15–$50',
            'brand_description_aesthetic': 'Bright handmade clothing',
            'readiness_level': 'Ready Now',
            'previous_market_experience': 'Returning Good Flea Vendor',
            'equipment_needs': ['Standard Space', 'Electricity Access'],
            'operational_placement_notes': 'Near an outlet',
            'target_market_dates': ['2026-10-18', '2026-10-10', '2026-10-10'],
            'booking_type': 'Multi-Weekend Package', 'agreed_pricing': '125.50',
            'invoice_email': 'billing@example.com',
            'primary_vendor_goal': 'High Sales Volume', 'objections_concerns': 'Load-in timing',
            'historical_vendor_feedback': 'More rack space next time',
            'lead_qualification': 'Qualified & Ready',
            'vendor_pipeline_stage': 'Call Completed -> Pending Invoice',
            'next_action_required': 'Send Shopify Draft Invoice',
            'next_followup_date': '2026-10-09', 'notes': 'Promised load-in instructions',
        }

    def test_create_read_edit_and_clear_new_answers_preserves_legacy(self):
        response = self.client.post(self.url, {**self.payload, 'offer_concerns': 'Original call note'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        detail = reverse('vendor-lead-detail', kwargs={'pk': response.data['id']})
        saved = self.client.get(detail).data['lead']
        for field, value in self.payload.items():
            if field != 'target_market_dates':
                self.assertEqual(saved[field], value, field)
        self.assertEqual(saved['target_market_dates'], ['2026-10-10', '2026-10-18'])
        response = self.client.patch(detail, {
            'equipment_needs': [], 'target_market_dates': [], 'agreed_pricing': None,
            'next_followup_date': None, 'lead_qualification': 'Needs Follow-Up',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        lead = VendorLead.objects.get(pk=saved['id'])
        self.assertEqual(lead.equipment_needs, [])
        self.assertEqual(lead.target_market_dates, [])
        self.assertIsNone(lead.agreed_pricing)
        self.assertIsNone(lead.next_followup_date)
        self.assertEqual(lead.offer_concerns, 'Original call note')

    def test_invalid_inputs_rejected(self):
        invalid = {
            'website_url': 'javascript:alert(1)', 'product_category': 'Unknown',
            'readiness_level': 'Unknown', 'previous_market_experience': 'Unknown',
            'equipment_needs': ['Unknown'], 'target_market_dates': ['2026-02-30'],
            'booking_type': 'Unknown', 'agreed_pricing': '-0.01',
            'invoice_email': 'invalid', 'primary_vendor_goal': 'Unknown',
            'lead_qualification': 'Unknown', 'vendor_pipeline_stage': 'Unknown',
            'next_action_required': 'Unknown', 'next_followup_date': 'invalid',
        }
        for field, value in invalid.items():
            with self.subTest(field=field):
                response = self.client.post(self.url, {**self.payload, field: value}, format='json')
                self.assertEqual(response.status_code, 400, response.data)
                self.assertIn(field, response.data)
        self.assertFalse(VendorLead.objects.exists())

    def test_pipeline_selection_does_not_record_payment_or_book_dates(self):
        response = self.client.post(self.url, {**self.payload, 'vendor_pipeline_stage': 'Booked & Paid'}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['application_decision'], 'pending')
        self.assertFalse(ApprovalInvoice.objects.exists())
        self.assertFalse(MarketWeekendBooking.objects.exists())

    @override_settings(INVOICE_EMAIL_READY=True, EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_invoice_uses_confirmed_billing_email_and_not_target_dates(self):
        response = self.client.post(self.url, self.payload, format='json')
        url = reverse('vendor-lead-approve-invoice', kwargs={'pk': response.data['id']})
        response = self.client.post(url, {
            'amount': '125.50', 'due_date': timezone.localdate().isoformat(),
            'invoice_link': 'https://example.com/invoice',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['recipient_email'], 'billing@example.com')
        self.assertEqual(mail.outbox[0].to, ['billing@example.com'])
        self.assertFalse(MarketWeekendBooking.objects.exists())
