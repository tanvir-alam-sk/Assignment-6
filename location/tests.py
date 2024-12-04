from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from location.models import Location
from location.models import Accommodation, validate_amenities
from django.core.exceptions import ValidationError
from decimal import Decimal
import json

class LocationModelTest(TestCase):

    def setUp(self):
        self.location = Location.objects.create(
            id="LOC001",
            title="Test City",
            center=Point(90.4125, 23.8103),  # Coordinates of Dhaka, Bangladesh
            location_type="city",
            country_code="BD",
        )

    def test_location_creation(self):
        self.assertEqual(self.location.title, "Test City")
        self.assertEqual(self.location.location_type, "city")
        self.assertEqual(self.location.country_code, "BD")
        self.assertEqual(self.location.center.x, 90.4125)
        self.assertEqual(self.location.center.y, 23.8103)

    def test_location_str_representation(self):
        self.assertEqual(str(self.location), "Test City (city)")


class AccommodationModelTest(TestCase):

    def setUp(self):
        self.location = Location.objects.create(
            id="LOC001",
            title="Test City",
            center=Point(90.4125, 23.8103),
            location_type="city",
            country_code="BD",
        )
        self.user = User.objects.create(username="testuser")
        self.accommodation = Accommodation.objects.create(
            id="ACC001",
            title="Test Accommodation",
            country_code="BD",
            bedroom_count=2,
            review_score=Decimal("4.5"),
            usd_rate=Decimal("100.00"),
            center=Point(90.4125, 23.8103),
            location=self.location,
            amenities=json.dumps(["WiFi", "Air Conditioning"]),
            user=self.user,
            published=True,
        )

    def test_accommodation_creation(self):
        self.assertEqual(self.accommodation.title, "Test Accommodation")
        self.assertEqual(self.accommodation.review_score, Decimal("4.5"))
        self.assertEqual(self.accommodation.usd_rate, Decimal("100.00"))
        self.assertEqual(self.accommodation.location, self.location)
        self.assertEqual(self.accommodation.user, self.user)

    def test_accommodation_str_representation(self):
        self.assertEqual(str(self.accommodation), "Test Accommodation - Test City")

    def test_amenities_validation(self):
        # Test valid amenities
        valid_amenities = json.dumps(["WiFi", "Parking"])
        validate_amenities(valid_amenities)  # Should not raise any exceptions

        # Test invalid amenities: non-string elements
        invalid_amenities = json.dumps(["WiFi", 12345])
        with self.assertRaises(ValidationError):
            validate_amenities(invalid_amenities)

        # Test invalid amenities: string length > 100
        invalid_amenities_long = json.dumps(["W" * 101])
        with self.assertRaises(ValidationError):
            validate_amenities(invalid_amenities_long)

    def test_accommodation_user_relation(self):
        self.assertEqual(self.accommodation.user.username, "testuser")