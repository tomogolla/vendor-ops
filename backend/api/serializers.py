import re

from rest_framework import serializers

from .models import VendorLead
from decimal import Decimal


class VendorLeadSerializer(serializers.ModelSerializer):
    instagram_handle = serializers.CharField(max_length=31, required=False, allow_blank=True)
    equipment_needs = serializers.ListField(child=serializers.ChoiceField(choices=['Standard Space', 'Table Needed', 'Rack Space', 'Electricity Access']), required=False, max_length=4)
    target_market_dates = serializers.ListField(child=serializers.DateField(), required=False, max_length=100)
    agreed_pricing = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'), required=False, allow_null=True)

    class Meta:
        model = VendorLead
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def validate_instagram_handle(self, value):
        value = value.strip().removeprefix('@').lower()
        if value and not re.fullmatch(r'[A-Za-z0-9._]{1,30}', value):
            raise serializers.ValidationError('Enter a valid Instagram handle, without a URL.')
        return value

    def validate_website_url(self, value):
        if value and not value.lower().startswith(('https://', 'http://')):
            raise serializers.ValidationError('Enter a website URL starting with https:// or http://.')
        return value

    def validate_equipment_needs(self, value):
        return list(dict.fromkeys(value))

    def validate_target_market_dates(self, value):
        return sorted({day.isoformat() for day in value})

    def validate_application_decision(self, value):
        if value == 'accepted':
            raise serializers.ValidationError('Use the approval invoice action to accept an application.')
        return value

    def validate(self, attrs):
        if not any(attrs.get(field, getattr(self.instance, field, '')) for field in ('instagram_handle', 'email', 'phone_number')):
            raise serializers.ValidationError('Provide an Instagram handle, email, or phone number.')
        return attrs
