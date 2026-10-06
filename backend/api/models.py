from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import json

CATEGORIES = [
    'Arts, Prints & Stickers', 'Beauty & Cosmetics', 'Ceramics / Glass',
    'Clothing Brand', 'Crotchet, Sewing, Quilt Goods', 'Cultural Collectibles',
    'Experience', 'Homeware', 'Jewelry', 'Leatherwork', 'Music / Vinyl',
    'NYC Merch', 'Pets Accessories', 'Photography', 'Plants',
    'Soaps / Candles and Perfume', 'Stationery', 'Unique Things',
    'Vintage Clothing', 'Vintage General', 'Vintage Homeware',
    'Vintage Jewelry', 'Vintage Upcycled',
]
LEAD_SOURCES = ['Instagram', 'Email', 'Meta ads', 'Shopify form', 'Google form', 'Google Sheets']
MARKET_WEEKENDS = [
    'October 10 & 11', 'October 17 & 18', 'October 24 & 25',
    'October 31 & November 1', 'November 7 & 8', 'November 14 & 15',
    'November 21 & 22', 'November 28 & 29', 'December 5 & 6',
    'December 12 & 13', 'December 19 & 20', 'December 26 & 27',
]

# Qualification statuses
QUALIFICATION_STATUSES = [
    ('unreviewed', 'Unreviewed'),
    ('contact_needed', 'Contact Needed'),
    ('discovery_scheduled', 'Discovery Scheduled'),
    ('qualified', 'Qualified'),
    ('not_qualified', 'Not Qualified'),
]

# Application statuses
APPLICATION_STATUSES = [
    ('new', 'New'),
    ('under_review', 'Under Review'),
    ('more_information_required', 'More Information Required'),
    ('accepted', 'Accepted'),
    ('waitlisted', 'Waitlisted'),
    ('declined', 'Declined'),
]

# Payment statuses
PAYMENT_STATUSES = [
    ('not_invoiced', 'Not Invoiced'),
    ('invoice_draft', 'Invoice Draft'),
    ('invoice_sent', 'Invoice Sent'),
    ('payment_pending', 'Payment Pending'),
    ('partially_paid', 'Partially Paid'),
    ('paid', 'Paid'),
    ('overdue', 'Overdue'),
    ('cancelled', 'Cancelled'),
    ('refunded', 'Refunded'),
]

# Booking statuses
BOOKING_STATUSES = [
    ('not_booked', 'Not Booked'),
    ('reserved', 'Reserved'),
    ('confirmed', 'Confirmed'),
    ('preparing', 'Preparing'),
    ('attended', 'Attended'),
    ('no_show', 'No-show'),
    ('cancelled', 'Cancelled'),
]

# Activity types
ACTIVITY_TYPES = [
    ('lead_registered', 'Lead Registered'),
    ('lead_imported', 'Lead Imported from CSV'),
    ('application_submitted', 'Application Submitted'),
    ('call_attempted', 'Call Attempted'),
    ('call_completed', 'Call Completed'),
    ('qualification_changed', 'Qualification Changed'),
    ('application_reviewed', 'Application Reviewed'),
    ('note_added', 'Note Added'),
    ('email_drafted', 'Email Drafted'),
    ('email_sent', 'Email Sent'),
    ('market_dates_shared', 'Market Dates Shared'),
    ('pricing_shared', 'Pricing Shared'),
    ('invoice_created', 'Invoice Created'),
    ('invoice_sent', 'Invoice Sent'),
    ('payment_reminder_sent', 'Payment Reminder Sent'),
    ('payment_recorded', 'Payment Recorded'),
    ('booking_confirmed', 'Booking Confirmed'),
    ('market_packet_sent', 'Market Packet Sent'),
    ('attendance_recorded', 'Attendance Recorded'),
    ('post_market_appreciation_sent', 'Post-Market Appreciation Sent'),
]

# Note types
NOTE_TYPES = [
    ('lead_intake', 'Lead Intake'),
    ('discovery_call', 'Discovery Call'),
    ('qualification', 'Qualification'),
    ('application_review', 'Application Review'),
    ('payment', 'Payment'),
    ('market_preparation', 'Market Preparation'),
    ('post_market', 'Post-Market'),
    ('general', 'General'),
]

# Attendance statuses
ATTENDANCE_STATUSES = [
    ('expected', 'Expected'),
    ('checked_in', 'Checked In'),
    ('absent', 'Absent'),
    ('no_show', 'No-show'),
    ('excused', 'Excused'),
]

# Payment methods
PAYMENT_METHODS = [
    ('bank_transfer', 'Bank Transfer'),
    ('credit_card', 'Credit Card'),
    ('cash', 'Cash'),
    ('check', 'Check'),
    ('stripe', 'Stripe'),
    ('other', 'Other'),
]


class VendorLead(models.Model):
    FUNNEL_STAGES = [('new_application', 'New application'), ('vendor', 'Vendor')]

    instagram_handle = models.CharField(max_length=30, blank=True)
    business_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=40, blank=True)
    vendor_category = models.CharField(max_length=100, choices=[(v, v) for v in CATEGORIES])
    lead_source = models.CharField(max_length=30, choices=[(v, v) for v in LEAD_SOURCES])
    interest_level = models.CharField(max_length=4, choices=[('hot', 'Hot'), ('warm', 'Warm'), ('cold', 'Cold')])
    next_followup = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, max_length=10000)
    vendor_contact_name = models.CharField(max_length=200, blank=True)
    website_url = models.URLField(max_length=2048, blank=True)
    product_category = models.CharField(max_length=40, blank=True, choices=[(v, v) for v in ['Apparel/Fashion', 'Jewelry & Accessories', 'Beauty & Wellness', 'Home Goods', 'Vintage/Thrift', 'Art & Craft', 'Pre-Packaged Food', 'Other']])
    price_point_range = models.CharField(max_length=200, blank=True)
    brand_description_aesthetic = models.TextField(blank=True, max_length=10000)
    readiness_level = models.CharField(max_length=30, blank=True, choices=[(v, v) for v in ['Ready Now', 'Needs 1–2 Weeks', 'Exploring Options']])
    previous_market_experience = models.CharField(max_length=40, blank=True, choices=[(v, v) for v in ['First-Time Vendor', 'Experienced Pop-Up Vendor', 'Returning Good Flea Vendor']])
    equipment_needs = models.JSONField(default=list, blank=True)
    operational_placement_notes = models.TextField(blank=True, max_length=10000)
    target_market_dates = models.JSONField(default=list, blank=True)
    booking_type = models.CharField(max_length=40, blank=True, choices=[(v, v) for v in ['Single Weekend', 'Multi-Weekend Package', 'Recurring Seasonal Vendor']])
    agreed_pricing = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    invoice_email = models.EmailField(blank=True)
    primary_vendor_goal = models.CharField(max_length=30, blank=True, choices=[(v, v) for v in ['High Sales Volume', 'Brand Awareness', 'Product Testing', 'Content Creation']])
    objections_concerns = models.TextField(blank=True, max_length=10000)
    historical_vendor_feedback = models.TextField(blank=True, max_length=10000)
    lead_qualification = models.CharField(max_length=30, blank=True, choices=[(v, v) for v in ['Qualified & Ready', 'Needs Follow-Up', 'Deferred', 'Not a Fit']])
    vendor_pipeline_stage = models.CharField(max_length=50, blank=True, choices=[(v, v) for v in ['Call Completed -> Pending Invoice', 'Invoice Sent -> Awaiting Payment', 'Booked & Paid', 'Closed / Rejected']])
    next_action_required = models.CharField(max_length=40, blank=True, choices=[(v, v) for v in ['Send Shopify Draft Invoice', 'Send Follow-Up Email', 'Schedule Second Call', 'Pass to Market Ops']])
    next_followup_date = models.DateField(null=True, blank=True)
    call_at = models.DateTimeField(null=True, blank=True)
    call_outcome = models.CharField(max_length=30, blank=True, choices=[(v, v) for v in ['Connected', 'Left Voicemail', 'Busy', 'Rescheduled']])
    identity_verified = models.CharField(max_length=3, blank=True, choices=[('Yes', 'Yes'), ('No', 'No')])
    available_to_chat = models.CharField(max_length=30, blank=True, choices=[(v, v) for v in ['Yes', 'Reschedule requested']])
    business_commitment = models.CharField(max_length=20, blank=True, choices=[(v, v) for v in ['Full-time', 'Part-time', 'Hobbyist']])
    currently_does_markets = models.CharField(max_length=3, blank=True, choices=[('Yes', 'Yes'), ('No', 'No')])
    markets_and_frequency = models.TextField(blank=True, max_length=10000)
    team_details = models.TextField(blank=True, max_length=10000)
    primary_goals = models.TextField(blank=True, max_length=10000)
    registration_status = models.CharField(max_length=20, blank=True, choices=[(v, v) for v in ['LLC', 'Sole Prop', 'In Progress', 'None']])
    insurance_status = models.CharField(max_length=30, blank=True, choices=[(v, v) for v in ['Have active policy', 'Need guidance', "Don't have"]])
    application_challenges = models.TextField(blank=True, max_length=10000)
    location_pain_points = models.TextField(blank=True, max_length=10000)
    revenue_consistency = models.TextField(blank=True, max_length=10000)
    offer_interest = models.PositiveSmallIntegerField(null=True, blank=True, choices=[(1, 'Very Hesitant'), (2, 'Hesitant'), (3, 'Neutral'), (4, 'Excited'), (5, 'Extremely Excited')])
    offer_concerns = models.TextField(blank=True, max_length=10000)
    long_term_outlook = models.CharField(max_length=40, blank=True, choices=[(v, v) for v in ['One-off', 'Seasonal', 'Long-term recurring anchor vendor']])
    trial_commitment = models.CharField(max_length=30, blank=True, choices=[(v, v) for v in ['Agreed', 'Under Consideration', 'Declined']])
    agreed_weekend_dates = models.CharField(max_length=500, blank=True)
    onboarding_dates_confirmed = models.BooleanField(default=False)
    trial_term_agreed = models.BooleanField(default=False)
    insurance_setup_walked_through = models.BooleanField(default=False)
    information_packet_sent = models.BooleanField(default=False)
    added_to_market_schedule = models.BooleanField(default=False)
    followup_status = models.CharField(max_length=30, blank=True, choices=[(v, v) for v in ['Closed - Confirmed', 'Follow-up Needed', 'Unqualified', 'Lost']])
    vendor_contract = models.BooleanField(default=False)
    coi = models.BooleanField(default=False)
    info_packet = models.BooleanField(default=False)
    application_decision = models.CharField(max_length=10, default='pending', choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('waitlisted', 'Waitlisted'), ('declined', 'Declined')])
    funnel_stage = models.CharField(max_length=20, choices=FUNNEL_STAGES, default='vendor', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return self.business_name


class ApprovalInvoice(models.Model):
    lead = models.OneToOneField(VendorLead, on_delete=models.PROTECT, related_name='approval_invoice')
    recipient_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    due_date = models.DateField()
    payment_instructions = models.TextField(max_length=2000)
    invoice_link = models.URLField(max_length=2048, blank=True)
    personal_message = models.TextField(blank=True, max_length=5000)
    weekend_dates = models.CharField(max_length=500, blank=True)
    sent_at = models.DateTimeField(default=timezone.now)

    @property
    def number(self):
        return f'GF-{self.sent_at.year}-{self.pk:06d}'

    def __str__(self):
        return self.number


class MarketWeekendBooking(models.Model):
    lead = models.ForeignKey(VendorLead, on_delete=models.PROTECT, related_name='market_bookings')
    invoice = models.ForeignKey(ApprovalInvoice, on_delete=models.PROTECT, related_name='market_bookings')
    weekend = models.CharField(max_length=50, choices=[(value, value) for value in MARKET_WEEKENDS])
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['weekend', 'lead__business_name', 'lead_id']
        constraints = [
            models.UniqueConstraint(fields=['lead', 'weekend'], name='unique_vendor_market_weekend'),
            models.CheckConstraint(condition=models.Q(amount_paid__gte=0), name='market_booking_nonnegative_paid'),
        ]

    def __str__(self):
        return f'{self.lead.business_name} — {self.weekend}'


# ============================================================================
# PHASE 1.2 NEW MODELS
# ============================================================================

class VendorProfile(models.Model):
    """Canonical source of truth for vendor information.
    Links all related records: leads, applications, invoices, bookings, etc."""

    lead = models.OneToOneField(VendorLead, on_delete=models.PROTECT, related_name='vendor_profile', null=True, blank=True)

    # Status tracking
    qualification_status = models.CharField(
        max_length=30, choices=QUALIFICATION_STATUSES, default='unreviewed', db_index=True
    )
    application_status = models.CharField(
        max_length=30, choices=APPLICATION_STATUSES, default='new', db_index=True
    )
    payment_status = models.CharField(
        max_length=30, choices=PAYMENT_STATUSES, default='not_invoiced', db_index=True
    )
    booking_status = models.CharField(
        max_length=30, choices=BOOKING_STATUSES, default='not_booked', db_index=True
    )

    # Ownership
    assigned_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['qualification_status', '-updated_at']),
            models.Index(fields=['payment_status', '-updated_at']),
            models.Index(fields=['booking_status', '-updated_at']),
        ]

    def __str__(self):
        return f'{self.lead.business_name if self.lead else "Unlinked"} (Profile)'


class VendorNote(models.Model):
    """Typed internal notes for vendors."""

    profile = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='notes')
    note_type = models.CharField(max_length=30, choices=NOTE_TYPES)
    content = models.TextField(max_length=10000)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', '-created_at']),
            models.Index(fields=['note_type', '-created_at']),
        ]

    def __str__(self):
        return f'{self.get_note_type_display()} - {self.profile}'


class Activity(models.Model):
    """Immutable vendor activity timeline."""

    profile = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=40, choices=ACTIVITY_TYPES, db_index=True)
    description = models.TextField(blank=True)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Related records (generic relations)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f'{self.get_activity_type_display()} - {self.profile}'


class MarketProduct(models.Model):
    """Represents one complete Saturday-Sunday market weekend."""

    name = models.CharField(max_length=200)
    saturday_date = models.DateField()
    sunday_date = models.DateField()
    location = models.CharField(max_length=255, blank=True)
    booking_opening_date = models.DateField()
    booking_closing_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('open', 'Open'), ('closed', 'Closed'), ('completed', 'Completed')],
        default='draft'
    )
    description = models.TextField(blank=True)
    total_booth_capacity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['saturday_date']
        indexes = [
            models.Index(fields=['status', 'saturday_date']),
        ]

    def __str__(self):
        return self.name


class BoothVariant(models.Model):
    """Booth types available for a market."""

    market = models.ForeignKey(MarketProduct, on_delete=models.CASCADE, related_name='booth_variants')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    width = models.PositiveIntegerField(help_text='Width in feet', null=True, blank=True)
    depth = models.PositiveIntegerField(help_text='Depth in feet', null=True, blank=True)
    capacity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['market', 'price']
        indexes = [
            models.Index(fields=['market', 'is_active']),
        ]

    def __str__(self):
        return f'{self.name} — ${self.price}'

    def available_quantity(self):
        """Calculate available capacity."""
        confirmed = self.bookings.filter(status='confirmed').count()
        held = self.holds.filter(is_expired=False).count()
        return max(0, self.capacity - confirmed - held)


class AddOn(models.Model):
    """Optional add-ons for invoices and bookings."""

    market = models.ForeignKey(MarketProduct, on_delete=models.CASCADE, related_name='add_ons')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=50, default='per weekend')
    has_inventory = models.BooleanField(default=False)
    total_inventory = models.PositiveIntegerField(null=True, blank=True)
    max_per_vendor = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['market', 'name']
        indexes = [
            models.Index(fields=['market', 'is_active']),
        ]

    def __str__(self):
        return f'{self.name} — ${self.price}'

    def available_inventory(self):
        """Calculate available inventory."""
        if not self.has_inventory or not self.total_inventory:
            return None
        allocated = self.line_items.filter(invoice__payment_status__in=['paid', 'payment_pending']).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        return max(0, self.total_inventory - allocated)


class Invoice(models.Model):
    """Invoice for booth and add-ons."""

    profile = models.ForeignKey(VendorProfile, on_delete=models.PROTECT, related_name='invoices')
    market = models.ForeignKey(MarketProduct, on_delete=models.PROTECT, related_name='invoices')
    booth_variant = models.ForeignKey(BoothVariant, on_delete=models.SET_NULL, null=True, blank=True)

    # Invoice metadata
    invoice_number = models.CharField(max_length=50, unique=True)
    recipient_email = models.EmailField()
    status = models.CharField(max_length=30, choices=PAYMENT_STATUSES, default='invoice_draft', db_index=True)

    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0)

    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    hold_expiry_date = models.DateTimeField(null=True, blank=True)

    # Payment instructions and notes
    payment_instructions = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)

    # Third-party provider fields (for future Stripe integration)
    payment_provider = models.CharField(max_length=50, blank=True)
    external_payment_id = models.CharField(max_length=255, blank=True)
    webhook_event_id = models.CharField(max_length=255, blank=True)
    payment_url = models.URLField(blank=True)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_status = models.CharField(max_length=50, blank=True)

    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices_created')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['market', 'status']),
        ]

    def __str__(self):
        return self.invoice_number

    @property
    def balance_due(self):
        return max(0, self.total - self.amount_paid)

    def is_fully_paid(self):
        return self.balance_due == 0


class InvoiceLineItem(models.Model):
    """Line items for invoices (booth + add-ons)."""

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    add_on = models.ForeignKey(AddOn, on_delete=models.SET_NULL, null=True, blank=True, related_name='line_items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ['invoice', 'id']

    def __str__(self):
        return f'{self.description} x {self.quantity}'


class Payment(models.Model):
    """Payment recording for invoices."""

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS)
    transaction_reference = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    internal_note = models.TextField(blank=True, max_length=1000)
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['invoice', '-created_at']),
        ]

    def __str__(self):
        return f'${self.amount} on {self.payment_date}'


class InventoryHold(models.Model):
    """Temporary booth and add-on reservations."""

    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name='inventory_hold')
    booth_variant = models.ForeignKey(BoothVariant, on_delete=models.PROTECT, related_name='holds')

    # Hold details
    held_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_expired = models.BooleanField(default=False, db_index=True)

    # Add-ons held
    add_ons = models.ManyToManyField(AddOn, through='InventoryHoldAddOn', related_name='holds')

    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-held_at']
        indexes = [
            models.Index(fields=['booth_variant', 'is_expired']),
        ]

    def __str__(self):
        return f'Hold for {self.invoice}'


class InventoryHoldAddOn(models.Model):
    """Add-ons held in an inventory hold."""

    hold = models.ForeignKey(InventoryHold, on_delete=models.CASCADE)
    add_on = models.ForeignKey(AddOn, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['hold', 'add_on']


class EmailTemplate(models.Model):
    """Reusable email templates with variable support."""

    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    description = models.TextField(blank=True)

    # Supported variables: {{vendor_name}}, {{market_date}}, {{booth_number}}, {{invoice_number}}, etc

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Communication(models.Model):
    """Sent communications and emails."""

    profile = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='communications')
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)

    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField()

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('sent', 'Sent'), ('failed', 'Failed'), ('opened', 'Opened')],
        default='draft'
    )
    error_message = models.TextField(blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', '-sent_at']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return f'{self.subject} to {self.recipient_email}'


class Task(models.Model):
    """Follow-up tasks for vendors."""

    profile = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Assignment and due date
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    due_time = models.TimeField(null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[('open', 'Open'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
        default='open'
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']
        indexes = [
            models.Index(fields=['profile', 'status', 'due_date']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return self.title


class Booking(models.Model):
    """Vendor booking for a market."""

    profile = models.ForeignKey(VendorProfile, on_delete=models.PROTECT, related_name='bookings')
    invoice = models.OneToOneField(Invoice, on_delete=models.PROTECT, related_name='booking')
    market = models.ForeignKey(MarketProduct, on_delete=models.PROTECT, related_name='bookings')
    booth_variant = models.ForeignKey(BoothVariant, on_delete=models.PROTECT, related_name='bookings')

    # Booth assignment
    booth_number = models.CharField(max_length=50, blank=True)

    # Status
    status = models.CharField(max_length=30, choices=BOOKING_STATUSES, default='reserved', db_index=True)

    # Add-ons
    add_ons = models.ManyToManyField(AddOn, related_name='bookings', blank=True)

    # Audit
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['profile', 'market'], condition=models.Q(status__in=['reserved', 'confirmed']), name='unique_active_booking_per_market'),
        ]
        indexes = [
            models.Index(fields=['market', 'status']),
            models.Index(fields=['profile', 'status']),
        ]

    def __str__(self):
        return f'{self.profile} — {self.market.name}'


class Attendance(models.Model):
    """Saturday and Sunday attendance tracking."""

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='attendance')

    saturday_status = models.CharField(max_length=20, choices=ATTENDANCE_STATUSES, default='expected')
    sunday_status = models.CharField(max_length=20, choices=ATTENDANCE_STATUSES, default='expected')

    saturday_checked_in_at = models.DateTimeField(null=True, blank=True)
    sunday_checked_in_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.booking.profile.lead.business_name} — {self.booking.market.name} Attendance'


class AuditLog(models.Model):
    """Audit trail for critical operations."""

    profile = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='audit_logs')

    # Event details
    event_type = models.CharField(
        max_length=50,
        choices=[
            ('status_change', 'Status Change'),
            ('application_decision', 'Application Decision'),
            ('payment_recorded', 'Payment Recorded'),
            ('payment_reversed', 'Payment Reversed'),
            ('booking_confirmed', 'Booking Confirmed'),
            ('booking_cancelled', 'Booking Cancelled'),
            ('hold_extended', 'Hold Extended'),
            ('inventory_adjusted', 'Inventory Adjusted'),
            ('booth_reassigned', 'Booth Reassigned'),
            ('authorization_override', 'Authorization Override'),
        ]
    )
    description = models.TextField()
    changes = models.JSONField(default=dict, blank=True)

    # Actor
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['profile', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
        ]

    def __str__(self):
        return f'{self.get_event_type_display()} — {self.profile}'
