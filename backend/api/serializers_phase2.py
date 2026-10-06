"""Serializers for Phase 1.2 models."""

from rest_framework import serializers
from decimal import Decimal
from .models import (
    VendorProfile, VendorNote, Activity, MarketProduct, BoothVariant, AddOn,
    Invoice, InvoiceLineItem, Payment, InventoryHold, EmailTemplate,
    Communication, Task, Booking, Attendance, AuditLog
)


class VendorNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = VendorNote
        fields = ['id', 'note_type', 'content', 'author', 'author_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'author']


class ActivitySerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)

    class Meta:
        model = Activity
        fields = [
            'id', 'activity_type', 'description', 'actor', 'actor_name',
            'related_object_id', 'related_object_type', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MarketProductSerializer(serializers.ModelSerializer):
    booth_variants = serializers.SerializerMethodField()
    add_ons = serializers.SerializerMethodField()

    class Meta:
        model = MarketProduct
        fields = [
            'id', 'name', 'saturday_date', 'sunday_date', 'location',
            'booking_opening_date', 'booking_closing_date', 'status',
            'description', 'total_booth_capacity', 'booth_variants', 'add_ons',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_booth_variants(self, obj):
        return BoothVariantSerializer(obj.booth_variants.filter(is_active=True), many=True).data

    def get_add_ons(self, obj):
        return AddOnSerializer(obj.add_ons.filter(is_active=True), many=True).data


class BoothVariantSerializer(serializers.ModelSerializer):
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = BoothVariant
        fields = [
            'id', 'market', 'name', 'price', 'width', 'depth', 'capacity',
            'available_quantity', 'description', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_available_quantity(self, obj):
        return obj.available_quantity()


class AddOnSerializer(serializers.ModelSerializer):
    available_inventory = serializers.SerializerMethodField()

    class Meta:
        model = AddOn
        fields = [
            'id', 'market', 'name', 'description', 'price', 'unit',
            'has_inventory', 'total_inventory', 'available_inventory',
            'max_per_vendor', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_available_inventory(self, obj):
        return obj.available_inventory()


class InvoiceLineItemSerializer(serializers.ModelSerializer):
    add_on_name = serializers.CharField(source='add_on.name', read_only=True)

    class Meta:
        model = InvoiceLineItem
        fields = ['id', 'invoice', 'add_on', 'add_on_name', 'description', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['id']


class PaymentSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'amount', 'payment_date', 'payment_method',
            'transaction_reference', 'recorded_by', 'recorded_by_name',
            'internal_note', 'receipt', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Payment amount must be greater than 0')
        return value


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    balance_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_fully_paid = serializers.SerializerMethodField()
    profile_business_name = serializers.CharField(source='profile.lead.business_name', read_only=True)
    market_name = serializers.CharField(source='market.name', read_only=True)
    booth_variant_name = serializers.CharField(source='booth_variant.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'profile', 'profile_business_name', 'market', 'market_name',
            'booth_variant', 'booth_variant_name', 'invoice_number',
            'recipient_email', 'status', 'subtotal', 'discount', 'tax', 'total',
            'amount_paid', 'balance_due', 'is_fully_paid', 'issue_date', 'due_date',
            'hold_expiry_date', 'payment_instructions', 'internal_notes',
            'line_items', 'payments', 'created_by', 'created_by_name',
            'created_at', 'sent_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'invoice_number', 'amount_paid', 'balance_due',
            'created_at', 'sent_at', 'updated_at'
        ]

    def get_is_fully_paid(self, obj):
        return obj.is_fully_paid()


class BookingSerializer(serializers.ModelSerializer):
    profile_business_name = serializers.CharField(source='profile.lead.business_name', read_only=True)
    market_name = serializers.CharField(source='market.name', read_only=True)
    booth_variant_name = serializers.CharField(source='booth_variant.name', read_only=True)
    add_on_names = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'profile', 'profile_business_name', 'invoice', 'market', 'market_name',
            'booth_variant', 'booth_variant_name', 'booth_number', 'status',
            'add_ons', 'add_on_names', 'confirmed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'confirmed_at', 'created_at', 'updated_at']

    def get_add_on_names(self, obj):
        return [add_on.name for add_on in obj.add_ons.all()]


class AttendanceSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source='booking.id', read_only=True)
    market_name = serializers.CharField(source='booking.market.name', read_only=True)
    vendor_name = serializers.CharField(source='booking.profile.lead.business_name', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'booking', 'booking_id', 'market_name', 'vendor_name',
            'saturday_status', 'sunday_status', 'saturday_checked_in_at',
            'sunday_checked_in_at', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'body', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommunicationSerializer(serializers.ModelSerializer):
    profile_business_name = serializers.CharField(source='profile.lead.business_name', read_only=True)
    sent_by_name = serializers.CharField(source='sent_by.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = Communication
        fields = [
            'id', 'profile', 'profile_business_name', 'template', 'template_name',
            'recipient_email', 'subject', 'body', 'sent_by', 'sent_by_name',
            'sent_at', 'status', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    profile_business_name = serializers.CharField(source='profile.lead.business_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'profile', 'profile_business_name', 'title', 'description',
            'assigned_to', 'assigned_to_name', 'due_date', 'due_time', 'status',
            'completed_at', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VendorProfileDetailSerializer(serializers.ModelSerializer):
    """Comprehensive vendor profile with all related data."""

    lead = serializers.SerializerMethodField()
    notes = VendorNoteSerializer(many=True, read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    invoices = InvoiceSerializer(many=True, read_only=True)
    payments = serializers.SerializerMethodField()
    bookings = BookingSerializer(many=True, read_only=True)
    communications = CommunicationSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    audit_logs = serializers.SerializerMethodField()
    assigned_owner_name = serializers.CharField(source='assigned_owner.get_full_name', read_only=True)

    class Meta:
        model = VendorProfile
        fields = [
            'id', 'lead', 'qualification_status', 'application_status',
            'payment_status', 'booking_status', 'assigned_owner', 'assigned_owner_name',
            'last_activity_at', 'notes', 'activities', 'invoices', 'payments',
            'bookings', 'communications', 'tasks', 'audit_logs',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_activity_at']

    def get_lead(self, obj):
        if obj.lead:
            from .serializers import VendorLeadSerializer
            return VendorLeadSerializer(obj.lead).data
        return None

    def get_payments(self, obj):
        # Get all payments for this vendor's invoices
        payment_ids = Payment.objects.filter(invoice__profile=obj).values_list('id', flat=True)
        payments = Payment.objects.filter(id__in=payment_ids)
        return PaymentSerializer(payments, many=True).data

    def get_audit_logs(self, obj):
        logs = obj.audit_logs.all()[:10]  # Last 10 audit logs
        return AuditLogSerializer(logs, many=True).data


class VendorProfileListSerializer(serializers.ModelSerializer):
    """Simplified vendor profile for list views."""

    lead_business_name = serializers.CharField(source='lead.business_name', read_only=True)
    lead_email = serializers.CharField(source='lead.email', read_only=True)
    lead_phone = serializers.CharField(source='lead.phone_number', read_only=True)
    assigned_owner_name = serializers.CharField(source='assigned_owner.get_full_name', read_only=True)
    last_activity_days_ago = serializers.SerializerMethodField()
    invoice_count = serializers.SerializerMethodField()

    class Meta:
        model = VendorProfile
        fields = [
            'id', 'lead_business_name', 'lead_email', 'lead_phone',
            'qualification_status', 'application_status', 'payment_status',
            'booking_status', 'assigned_owner', 'assigned_owner_name',
            'last_activity_at', 'last_activity_days_ago', 'invoice_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields

    def get_last_activity_days_ago(self, obj):
        from django.utils import timezone
        if not obj.last_activity_at:
            return None
        delta = timezone.now() - obj.last_activity_at
        return delta.days

    def get_invoice_count(self, obj):
        return obj.invoices.count()


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'profile', 'event_type', 'description', 'changes',
            'actor', 'actor_name', 'created_at'
        ]
        read_only_fields = fields
