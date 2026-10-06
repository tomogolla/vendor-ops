"""Duplicate vendor detection service."""

import re
from django.db.models import Q
from api.models import VendorLead, VendorProfile


class DuplicateDetectionService:
    """Find potential duplicate vendors using email, phone, and Instagram handle."""

    @staticmethod
    def normalize_email(email):
        """Normalize email for comparison."""
        if not email:
            return ''
        return email.strip().lower()

    @staticmethod
    def normalize_phone(phone):
        """Normalize phone for comparison."""
        if not phone:
            return ''
        # Remove all non-digit characters
        return re.sub(r'\D', '', phone)

    @staticmethod
    def normalize_instagram(handle):
        """Normalize Instagram handle for comparison."""
        if not handle:
            return ''
        return handle.strip().lstrip('@').lower()

    @classmethod
    def find_duplicates_by_email(cls, email, exclude_id=None):
        """Find vendors with matching email."""
        normalized = cls.normalize_email(email)
        if not normalized:
            return []

        query = Q(lead__email__iexact=normalized)
        if exclude_id:
            query &= ~Q(id=exclude_id)

        return list(VendorProfile.objects.filter(query))

    @classmethod
    def find_duplicates_by_phone(cls, phone, exclude_id=None):
        """Find vendors with matching phone number."""
        normalized = cls.normalize_phone(phone)
        if not normalized or len(normalized) < 10:
            return []

        # Get all leads with this normalized phone
        query = Q(lead__phone_number__contains=normalized)
        if exclude_id:
            query &= ~Q(id=exclude_id)

        return list(VendorProfile.objects.filter(query))

    @classmethod
    def find_duplicates_by_instagram(cls, handle, exclude_id=None):
        """Find vendors with matching Instagram handle."""
        normalized = cls.normalize_instagram(handle)
        if not normalized:
            return []

        query = Q(lead__instagram_handle__iexact=normalized)
        if exclude_id:
            query &= ~Q(id=exclude_id)

        return list(VendorProfile.objects.filter(query))

    @classmethod
    def find_all_duplicates(cls, email='', phone='', instagram_handle='', exclude_id=None):
        """Find potential duplicates across all fields."""
        duplicates = set()

        if email:
            duplicates.update(cls.find_duplicates_by_email(email, exclude_id))

        if phone:
            duplicates.update(cls.find_duplicates_by_phone(phone, exclude_id))

        if instagram_handle:
            duplicates.update(cls.find_duplicates_by_instagram(instagram_handle, exclude_id))

        return sorted(list(duplicates), key=lambda p: p.id)

    @classmethod
    def find_duplicates_for_lead(cls, lead, exclude_profile_id=None):
        """Find duplicates for a specific lead."""
        return cls.find_all_duplicates(
            email=lead.email,
            phone=lead.phone_number,
            instagram_handle=lead.instagram_handle,
            exclude_id=exclude_profile_id
        )
