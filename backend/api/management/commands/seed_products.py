from decimal import Decimal
from django.core.management.base import BaseCommand
from api.models import BoothSize, AddOn, Discount


class Command(BaseCommand):
    help = 'Seeds the database with booth sizes, add-ons, and discounts'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seed...')

        # Clear existing data
        BoothSize.objects.all().delete()
        AddOn.objects.all().delete()
        Discount.objects.all().delete()

        # Create booth sizes
        booth_sizes = [
            {
                'name': '8x12',
                'width': 8,
                'length': 12,
                'base_price': Decimal('530.00'),
                'description': 'Standard 8ft × 12ft booth space',
            },
            {
                'name': '8x8',
                'width': 8,
                'length': 8,
                'base_price': Decimal('400.00'),
                'description': 'Compact 8ft × 8ft booth space',
            },
            {
                'name': '10x10',
                'width': 10,
                'length': 10,
                'base_price': Decimal('525.00'),
                'description': 'Square 10ft × 10ft booth space',
            },
        ]

        for booth_data in booth_sizes:
            booth = BoothSize.objects.create(**booth_data, is_active=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created booth size: {booth.width}ft × {booth.length}ft @ ${booth.base_price}'
                )
            )

        # Create add-ons
        add_ons = [
            {
                'name': 'Tent Rental',
                'price_per_weekend': Decimal('60.00'),
                'description': 'Premium tent rental (protects from weather)',
            },
            {
                'name': 'Table & Chairs',
                'price_per_weekend': Decimal('40.00'),
                'description': 'One 6ft table + 2 chairs for display',
            },
            {
                'name': 'Electricity',
                'price_per_weekend': Decimal('75.00'),
                'description': '20-amp electrical service at booth',
            },
            {
                'name': 'Security Deposit',
                'price_per_weekend': Decimal('100.00'),
                'description': 'Refundable security/damage deposit',
            },
        ]

        for addon_data in add_ons:
            addon = AddOn.objects.create(**addon_data, is_active=True)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created add-on: {addon.name} @ ${addon.price_per_weekend}/weekend'
                )
            )

        # Create discounts
        discounts = [
            {
                'name': 'Early Bird',
                'description': '10% discount for early registration',
                'discount_type': 'percentage',
                'value': Decimal('10.00'),
            },
            {
                'name': 'Multi-Market',
                'description': 'Referral bonus - $50 off',
                'discount_type': 'fixed',
                'value': Decimal('50.00'),
            },
            {
                'name': 'Non-Profit',
                'description': '15% discount for registered non-profits',
                'discount_type': 'percentage',
                'value': Decimal('15.00'),
            },
            {
                'name': 'Seasonal',
                'description': 'End-of-season clearance - 20% off',
                'discount_type': 'percentage',
                'value': Decimal('20.00'),
            },
        ]

        for discount_data in discounts:
            discount = Discount.objects.create(**discount_data, is_active=True)
            discount_display = (
                f'{discount.value}%' if discount.discount_type == 'percentage'
                else f'${discount.value}'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Created discount: {discount.name} ({discount_display})'
                )
            )

        self.stdout.write(
            self.style.SUCCESS('\n✅ Database seeded successfully!')
        )
        self.stdout.write(
            self.style.WARNING(
                f'Created: {BoothSize.objects.count()} booth sizes, '
                f'{AddOn.objects.count()} add-ons, {Discount.objects.count()} discounts'
            )
        )
