"""API views for Phase 1.2 models."""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count, Sum, F
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal

from .models import (
    VendorProfile, VendorLead, Invoice, Payment, Booking, Activity,
    MarketProduct, BoothVariant, AddOn, Task, Communication,
    EmailTemplate, Attendance
)
from .serializers_phase2 import (
    VendorProfileDetailSerializer, VendorProfileListSerializer,
    InvoiceSerializer, PaymentSerializer, BookingSerializer,
    ActivitySerializer, TaskSerializer, MarketProductSerializer,
    BoothVariantSerializer, AddOnSerializer, CommunicationSerializer,
    EmailTemplateSerializer, AttendanceSerializer
)
from .services.duplicate_detection import DuplicateDetectionService
from .services.payments import PaymentProcessingService
from .services.status_transitions import StatusTransitionService
from .services.inventory import InventoryManagementService
from .services.activities import ActivityRecordingService


class VendorProfileViewSet(viewsets.ModelViewSet):
    """Vendor profile management with filtering and actions."""

    permission_classes = [IsAuthenticated]
    queryset = VendorProfile.objects.prefetch_related(
        'notes', 'activities', 'invoices', 'bookings', 'communications', 'tasks'
    )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VendorProfileDetailSerializer
        return VendorProfileListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtering
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(
                Q(qualification_status=status_filter) |
                Q(application_status=status_filter) |
                Q(payment_status=status_filter) |
                Q(booking_status=status_filter)
            )

        owner_id = self.request.query_params.get('owner')
        if owner_id:
            queryset = queryset.filter(assigned_owner_id=owner_id)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(lead__business_name__icontains=search) |
                Q(lead__email__icontains=search) |
                Q(lead__phone_number__icontains=search)
            )

        return queryset.order_by('-updated_at')

    @action(detail=True, methods=['post'])
    def qualify(self, request, pk=None):
        """Mark vendor as qualified."""
        profile = self.get_object()
        reason = request.data.get('reason', '')

        try:
            StatusTransitionService.change_qualification_status(
                profile, 'qualified', reason, request.user
            )
            return Response({'status': 'qualified'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Mark vendor as not qualified."""
        profile = self.get_object()
        reason = request.data.get('reason', '')

        try:
            StatusTransitionService.change_qualification_status(
                profile, 'not_qualified', reason, request.user
            )
            return Response({'status': 'not_qualified'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def accept_application(self, request, pk=None):
        """Accept vendor application."""
        profile = self.get_object()
        reason = request.data.get('reason', '')

        try:
            StatusTransitionService.change_application_status(
                profile, 'accepted', reason, request.user
            )
            return Response({'status': 'accepted'})
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def find_duplicates(self, request, pk=None):
        """Find potential duplicate vendors."""
        profile = self.get_object()
        lead = profile.lead

        duplicates = DuplicateDetectionService.find_duplicates_for_lead(lead, profile.id)

        return Response({
            'count': len(duplicates),
            'duplicates': VendorProfileListSerializer(duplicates, many=True).data
        })

    @action(detail=False, methods=['get'])
    def awaiting_payment(self, request):
        """Vendors awaiting payment."""
        queryset = self.get_queryset().filter(
            payment_status__in=['invoice_sent', 'payment_pending', 'overdue']
        ).order_by('invoices__due_date')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'])
    def qualified_no_invoice(self, request):
        """Qualified vendors without invoices."""
        queryset = self.get_queryset().filter(
            qualification_status='qualified',
            payment_status='not_invoiced'
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'])
    def confirmed_bookings(self, request):
        """Vendors with confirmed bookings."""
        queryset = self.get_queryset().filter(booking_status='confirmed')

        serializer = self.get_serializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})


class InvoiceViewSet(viewsets.ModelViewSet):
    """Invoice management."""

    permission_classes = [IsAuthenticated]
    queryset = Invoice.objects.prefetch_related('line_items', 'payments')
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by profile
        profile_id = self.request.query_params.get('profile')
        if profile_id:
            queryset = queryset.filter(profile_id=profile_id)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by market
        market_id = self.request.query_params.get('market')
        if market_id:
            queryset = queryset.filter(market_id=market_id)

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send invoice to vendor."""
        invoice = self.get_object()

        if not invoice.recipient_email:
            return Response(
                {'error': 'Recipient email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: Implement email sending in Phase 2
        invoice.sent_at = timezone.now()
        invoice.save(update_fields=['sent_at'])

        ActivityRecordingService.record_invoice_sent(invoice.profile, invoice, request.user)

        return Response({'status': 'sent', 'sent_at': invoice.sent_at})

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """Record a payment against this invoice."""
        invoice = self.get_object()

        serializer = PaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment, updated_invoice = PaymentProcessingService.record_payment(
                invoice=invoice,
                amount=request.data.get('amount'),
                payment_date=request.data.get('payment_date'),
                payment_method=request.data.get('payment_method'),
                transaction_reference=request.data.get('transaction_reference', ''),
                internal_note=request.data.get('internal_note', ''),
                recorded_by=request.user
            )

            return Response({
                'payment': PaymentSerializer(payment).data,
                'invoice': InvoiceSerializer(updated_invoice).data
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Payment history and details."""

    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        invoice_id = self.request.query_params.get('invoice')
        if invoice_id:
            queryset = queryset.filter(invoice_id=invoice_id)

        profile_id = self.request.query_params.get('profile')
        if profile_id:
            queryset = queryset.filter(invoice__profile_id=profile_id)

        return queryset.order_by('-created_at')


class BookingViewSet(viewsets.ModelViewSet):
    """Booking management."""

    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.prefetch_related('add_ons')
    serializer_class = BookingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        profile_id = self.request.query_params.get('profile')
        if profile_id:
            queryset = queryset.filter(profile_id=profile_id)

        market_id = self.request.query_params.get('market')
        if market_id:
            queryset = queryset.filter(market_id=market_id)

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in vendor for Saturday or Sunday."""
        booking = self.get_object()
        day = request.data.get('day')  # 'saturday' or 'sunday'

        if day not in ['saturday', 'sunday']:
            return Response(
                {'error': 'day must be "saturday" or "sunday"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            attendance = booking.attendance
            now = timezone.now()

            if day == 'saturday':
                attendance.saturday_status = 'checked_in'
                attendance.saturday_checked_in_at = now
            else:
                attendance.sunday_status = 'checked_in'
                attendance.sunday_checked_in_at = now

            attendance.save()

            return Response(AttendanceSerializer(attendance).data)
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'Attendance record not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AttendanceViewSet(viewsets.ModelViewSet):
    """Attendance tracking."""

    permission_classes = [IsAuthenticated]
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        market_id = self.request.query_params.get('market')
        if market_id:
            queryset = queryset.filter(booking__market_id=market_id)

        return queryset.order_by('-created_at')


class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """Vendor activity timeline."""

    permission_classes = [IsAuthenticated]
    serializer_class = ActivitySerializer

    def get_queryset(self):
        queryset = Activity.objects.all()

        profile_id = self.request.query_params.get('profile')
        if profile_id:
            queryset = queryset.filter(profile_id=profile_id)

        activity_type = self.request.query_params.get('type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        return queryset.order_by('-created_at')


class MarketProductViewSet(viewsets.ModelViewSet):
    """Market product (weekend) management."""

    permission_classes = [IsAuthenticated]
    queryset = MarketProduct.objects.prefetch_related('booth_variants', 'add_ons')
    serializer_class = MarketProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('saturday_date')


class DashboardView(APIView):
    """Dashboard metrics and actionable insights."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get dashboard metrics."""
        now = timezone.now()
        seven_days_ago = now - timezone.timedelta(days=7)

        return Response({
            # Lead metrics
            'new_leads_this_week': VendorLead.objects.filter(
                created_at__gte=seven_days_ago
            ).count(),

            # Application metrics
            'applications_awaiting_review': VendorProfile.objects.filter(
                application_status='under_review'
            ).count(),
            'applications_requiring_info': VendorProfile.objects.filter(
                application_status='more_information_required'
            ).count(),

            # Qualification metrics
            'vendors_awaiting_contact': VendorProfile.objects.filter(
                qualification_status='contact_needed'
            ).count(),
            'qualified_vendors': VendorProfile.objects.filter(
                qualification_status='qualified'
            ).count(),

            # Invoice & payment metrics
            'invoices_sent_unpaid': Invoice.objects.filter(
                status__in=['invoice_sent', 'payment_pending', 'overdue']
            ).count(),
            'overdue_invoices': Invoice.objects.filter(
                status='overdue'
            ).count(),
            'total_amount_pending': Invoice.objects.filter(
                status__in=['invoice_sent', 'payment_pending', 'overdue']
            ).aggregate(total=Sum('balance_due'))['total'] or Decimal('0'),

            # Booking metrics
            'confirmed_bookings': Booking.objects.filter(
                status='confirmed'
            ).count(),
            'preparing_for_market': Booking.objects.filter(
                status='preparing'
            ).count(),

            # Inventory metrics
            'active_holds': Booking.objects.filter(
                status='reserved'
            ).count(),
            'expiring_holds_soon': Booking.objects.filter(
                status='reserved',
                created_at__lt=now - timezone.timedelta(hours=20)
            ).count(),
        })


class FilteredVendorListView(APIView):
    """Various filtered vendor lists for operational views."""

    permission_classes = [IsAuthenticated]

    def get(self, request, filter_type):
        """Get filtered vendor lists."""

        filters = {
            'awaiting-payment': lambda: VendorProfile.objects.filter(
                payment_status__in=['invoice_sent', 'payment_pending', 'overdue']
            ).order_by('invoices__due_date'),

            'qualified-no-invoice': lambda: VendorProfile.objects.filter(
                qualification_status='qualified',
                payment_status='not_invoiced'
            ),

            'accepted-unpaid': lambda: VendorProfile.objects.filter(
                application_status='accepted',
                payment_status__in=['invoice_draft', 'invoice_sent', 'payment_pending']
            ),

            'confirmed-bookings': lambda: VendorProfile.objects.filter(
                booking_status='confirmed'
            ),

            'preparing-market': lambda: VendorProfile.objects.filter(
                booking_status='preparing'
            ),

            'post-market-followup': lambda: VendorProfile.objects.filter(
                bookings__status='attended'
            ).distinct(),

            'overdue-payments': lambda: VendorProfile.objects.filter(
                invoices__status='overdue'
            ).distinct(),
        }

        if filter_type not in filters:
            return Response(
                {'error': f'Unknown filter type: {filter_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = filters[filter_type]()
        serializer = VendorProfileListSerializer(queryset, many=True)

        return Response({
            'filter': filter_type,
            'count': queryset.count(),
            'results': serializer.data
        })
