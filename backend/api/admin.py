from django.contrib import admin
from .models import (
    ApprovalInvoice, MarketWeekendBooking, VendorLead,
    VendorProfile, VendorNote, Activity, MarketProduct, BoothVariant, AddOn,
    Invoice, InvoiceLineItem, Payment, InventoryHold, InventoryHoldAddOn,
    EmailTemplate, Communication, Task, Booking, Attendance, AuditLog
)

admin.site.register(VendorLead)

@admin.register(ApprovalInvoice)
class ApprovalInvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'lead', 'amount', 'due_date', 'sent_at')
    search_fields = ('lead__business_name', 'recipient_email')


@admin.register(MarketWeekendBooking)
class MarketWeekendBookingAdmin(admin.ModelAdmin):
    list_display = ('weekend', 'lead', 'amount_paid', 'invoice')
    list_editable = ('amount_paid',)
    list_filter = ('weekend',)
    search_fields = ('lead__business_name', 'lead__email')


# ============================================================================
# PHASE 1.2 NEW ADMIN CLASSES
# ============================================================================

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead_business_name', 'qualification_status', 'payment_status', 'booking_status', 'assigned_owner')
    list_filter = ('qualification_status', 'payment_status', 'booking_status', 'assigned_owner')
    search_fields = ('lead__business_name', 'lead__email')
    readonly_fields = ('created_at', 'updated_at', 'last_activity_at')

    def lead_business_name(self, obj):
        return obj.lead.business_name if obj.lead else 'Unlinked'
    lead_business_name.short_description = 'Business Name'


@admin.register(VendorNote)
class VendorNoteAdmin(admin.ModelAdmin):
    list_display = ('profile', 'note_type', 'author', 'created_at')
    list_filter = ('note_type', 'created_at')
    search_fields = ('profile__lead__business_name', 'content')
    readonly_fields = ('created_at',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('profile', 'activity_type', 'actor', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('profile__lead__business_name', 'description')
    readonly_fields = ('created_at',)


@admin.register(MarketProduct)
class MarketProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'saturday_date', 'sunday_date', 'status', 'total_booth_capacity')
    list_filter = ('status', 'saturday_date')
    search_fields = ('name', 'location')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BoothVariant)
class BoothVariantAdmin(admin.ModelAdmin):
    list_display = ('market', 'name', 'price', 'capacity', 'is_active')
    list_filter = ('market', 'is_active')
    search_fields = ('market__name', 'name')


@admin.register(AddOn)
class AddOnAdmin(admin.ModelAdmin):
    list_display = ('market', 'name', 'price', 'has_inventory', 'total_inventory', 'is_active')
    list_filter = ('market', 'is_active', 'has_inventory')
    search_fields = ('market__name', 'name')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'profile', 'status', 'total', 'amount_paid', 'due_date')
    list_filter = ('status', 'market', 'due_date')
    search_fields = ('invoice_number', 'profile__lead__business_name', 'recipient_email')
    readonly_fields = ('created_at', 'updated_at', 'sent_at')

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing invoice
            readonly.extend(['invoice_number', 'profile', 'market'])
        return readonly


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('invoice__market',)
    search_fields = ('invoice__invoice_number', 'description')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'payment_date', 'payment_method', 'recorded_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('invoice__invoice_number', 'transaction_reference')
    readonly_fields = ('created_at',)


@admin.register(InventoryHold)
class InventoryHoldAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'booth_variant', 'expires_at', 'is_expired')
    list_filter = ('is_expired', 'held_at')
    search_fields = ('invoice__invoice_number',)
    readonly_fields = ('held_at',)


@admin.register(InventoryHoldAddOn)
class InventoryHoldAddOnAdmin(admin.ModelAdmin):
    list_display = ('hold', 'add_on', 'quantity')
    list_filter = ('hold__held_at',)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'subject')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'recipient_email', 'status', 'sent_at')
    list_filter = ('status', 'sent_at')
    search_fields = ('profile__lead__business_name', 'recipient_email', 'subject')
    readonly_fields = ('created_at',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'assigned_to', 'status', 'due_date')
    list_filter = ('status', 'due_date', 'assigned_to')
    search_fields = ('profile__lead__business_name', 'title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('profile', 'market', 'booth_variant', 'status', 'booth_number')
    list_filter = ('status', 'market')
    search_fields = ('profile__lead__business_name', 'booth_number')
    readonly_fields = ('created_at', 'updated_at', 'confirmed_at')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('booking', 'saturday_status', 'sunday_status')
    list_filter = ('saturday_status', 'sunday_status')
    search_fields = ('booking__profile__lead__business_name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('profile', 'event_type', 'actor', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('profile__lead__business_name', 'description')
    readonly_fields = ('created_at',)
