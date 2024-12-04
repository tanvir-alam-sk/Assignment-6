from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User,Group
from location.models import Location, Accommodation, AccommodationImage, LocalizeAccommodation
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from django.urls import reverse
from django.contrib.messages import get_messages
from django.http import HttpResponse
from unittest.mock import patch
from decimal import Decimal



class LocationModelTestCase(TestCase):
    
    def setUp(self):
        # Create a Location instance for testing
        self.location = Location.objects.create(
            id="usa",
            title="USA",
            location_type="country",
            country_code="US",
            center="POINT(-77.0369 38.9072)"
        )

    def test_location_creation(self):
        # Verify the Location instance is created
        self.assertEqual(self.location.title, "USA")
        self.assertEqual(self.location.location_type, "country")
        self.assertEqual(self.location.country_code, "US")

class AccommodationModelTestCase(TestCase):

    def setUp(self):
        # Create a Location instance and a user for the accommodation
        self.location = Location.objects.create(
            id="usa",
            title="USA",
            location_type="country",
            country_code="US",
            center="POINT(-77.0369 38.9072)"
        )
        self.user = User.objects.create_user(username="testuser", password="password")
        # Create an Accommodation instance for testing
        self.accommodation = Accommodation.objects.create(
            id="accom001",
            title="Test Accommodation",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=Decimal('100.00'),
            center="POINT(-77.0369 38.9072)",
            location=self.location,
            user=self.user
        )

    def test_accommodation_creation(self):
        # Verify the Accommodation instance is created
        self.assertEqual(self.accommodation.title, "Test Accommodation")
        self.assertEqual(self.accommodation.location.title, "USA")
        self.assertEqual(self.accommodation.user.username, "testuser")

    def test_amenities_validation(self):
        # Test valid amenities
        self.accommodation.amenities = json.dumps(["WiFi", "Pool", "Gym"])
        try:
            self.accommodation.full_clean()  # Trigger validation
        except ValidationError:
            self.fail("Amenities validation failed for valid input.")

        # Test invalid amenities
        self.accommodation.amenities = json.dumps(["WiFi", "A very long amenity name" * 10])
        with self.assertRaises(ValidationError):
            self.accommodation.full_clean()  # Should raise ValidationError

class AccommodationImageModelTestCase(TestCase):

    def setUp(self):
        # Create a Location and a User
        self.location = Location.objects.create(
            id="usa",
            title="USA",
            location_type="country",
            country_code="US",
            center="POINT(-77.0369 38.9072)"
        )
        self.user = User.objects.create_user(username="testuser", password="password")
        self.accommodation = Accommodation.objects.create(
            id="accom001",
            title="Test Accommodation",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=Decimal('100.00'),
            center="POINT(-77.0369 38.9072)",
            location=self.location,
            user=self.user
        )

    def test_accommodation_image_upload(self):
        # Create a mock image for testing
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        accommodation_image = AccommodationImage.objects.create(accommodation=self.accommodation, image=image)
        
        # Verify image upload
        self.assertTrue(os.path.exists(accommodation_image.image.path))  # Image file should exist

    def test_image_filename_format(self):
        # Test if the image filename is being slugified and renamed correctly
        image = SimpleUploadedFile("test Image.jpg", b"file_content", content_type="image/jpeg")
        accommodation_image = AccommodationImage.objects.create(accommodation=self.accommodation, image=image)

        # Check if filename is slugified
        self.assertTrue(accommodation_image.image.name.startswith("test-image"))

class LocalizeAccommodationModelTestCase(TestCase):

    def setUp(self):
        # Create a Location, User, and Accommodation
        self.location = Location.objects.create(
            id="usa",
            title="USA",
            location_type="country",
            country_code="US",
            center="POINT(-77.0369 38.9072)"
        )
        self.user = User.objects.create_user(username="testuser", password="password")
        self.accommodation = Accommodation.objects.create(
            id="accom001",
            title="Test Accommodation",
            country_code="US",
            bedroom_count=2,
            review_score=4.5,
            usd_rate=Decimal('100.00'),
            center="POINT(-77.0369 38.9072)",
            location=self.location,
            user=self.user
        )

    def test_localized_accommodation_creation(self):
        # Create Localized Accommodation instance for testing
        localized_accommodation = LocalizeAccommodation.objects.create(
            accommodation=self.accommodation,
            language="en",
            description="Test description",
            policy=json.dumps({"policy1": "value1"})
        )

        # Verify the Localized Accommodation instance is created
        self.assertEqual(localized_accommodation.language, "en")
        self.assertEqual(localized_accommodation.description, "Test description")
        self.assertTrue(isinstance(localized_accommodation.policy, dict))

    def test_unique_together_constraint(self):
        # Test the unique constraint on (accommodation, language)
        LocalizeAccommodation.objects.create(
            accommodation=self.accommodation,
            language="en",
            description="Test description",
            policy=json.dumps({"policy1": "value1"})
        )
        with self.assertRaises(ValidationError):
            LocalizeAccommodation.objects.create(
                accommodation=self.accommodation,
                language="en",  # Duplicate language
                description="Another description",
                policy=json.dumps({"policy1": "value2"})
            )


# views



class TestViews(TestCase):
    def setUp(self):
        # Set up a user group for testing
        self.group_name = "Property Owners"
        self.group = Group.objects.create(name=self.group_name)
        
        # Set up URL for testing
        self.index_url = reverse('index')  # Assuming 'index' is the name of the URL for the index view
        self.register_url = reverse('register')  # Assuming 'register' is the name of the URL for the register view

    def test_index_view(self):
        """
        Test the index view renders correctly.
        """
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Welcone As a New User</h1>")

    @patch('django.contrib.messages.add_message')
    def test_register_view_valid_data(self, mock_messages):
        """
        Test that user can successfully register with valid data.
        """
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }

        response = self.client.post(self.register_url, user_data)

        # Check that the user was created successfully
        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, '/welcome')
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Check if the user is added to the correct group
        user = User.objects.get(username='newuser')
        self.assertTrue(user.groups.filter(name=self.group_name).exists())

        # Check if success message is sent
        mock_messages.assert_called_with(response.wsgi_request, 25, 'Account created successfully!')

    @patch('django.contrib.messages.add_message')
    def test_register_view_password_mismatch(self, mock_messages):
        """
        Test that the register view shows error if passwords don't match.
        """
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password'
        }

        response = self.client.post(self.register_url, user_data)

        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, self.register_url)
        
        # Check that an error message is set
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Passwords do not match.")

    @patch('django.contrib.messages.add_message')
    def test_register_view_username_taken(self, mock_messages):
        """
        Test that the register view shows error if the username is already taken.
        """
        existing_user = User.objects.create_user(
            username='existinguser',
            email='existinguser@example.com',
            password='password123'
        )

        user_data = {
            'username': 'existinguser',  # Already taken username
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }

        response = self.client.post(self.register_url, user_data)

        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, self.register_url)
        
        # Check that an error message is set
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Username already taken.")

    @patch('django.contrib.messages.add_message')
    def test_register_view_email_taken(self, mock_messages):
        """
        Test that the register view shows error if the email is already taken.
        """
        existing_user = User.objects.create_user(
            username='existinguser',
            email='existinguser@example.com',
            password='password123'
        )

        user_data = {
            'username': 'newuser',
            'email': 'existinguser@example.com',  # Already taken email
            'password': 'password123',
            'confirm_password': 'password123'
        }

        response = self.client.post(self.register_url, user_data)

        self.assertEqual(response.status_code, 302)  # Should redirect
        self.assertRedirects(response, self.register_url)
        
        # Check that an error message is set
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Email already in use.")


from django.test import TestCase
from django.contrib.auth.models import User
from .models import Accommodation
from .forms import AccommodationForm

class AccommodationFormTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create some dummy data for the form (excluding 'user' field)
        self.accommodation_data = {
            'title': 'Test Accommodation',
            'location': 'Test Location',  # Replace with a valid location
            'bedroom_count': 3,
            'usd_rate': 100.00,
            'center': 'POINT(0 0)',  # Valid geospatial point
            'amenities': ['WiFi', 'Air Conditioning'],
            'published': True
        }

    def test_form_valid(self):
        # Initialize form with valid data and the user
        form = AccommodationForm(data=self.accommodation_data, user=self.user)

        # Check if form is valid
        self.assertTrue(form.is_valid())

        # Save the form without committing to the database to check instance
        accommodation = form.save(commit=False)
        # Ensure the user is correctly assigned
        self.assertEqual(accommodation.user, self.user)

    def test_form_invalid_missing_user(self):
        # Initialize form with valid data but no user
        form = AccommodationForm(data=self.accommodation_data)

        # Check if form is invalid due to missing user
        self.assertFalse(form.is_valid())
        self.assertIn('user', form.errors)

    def test_form_initial_user_value(self):
        # Initialize the form with valid data
        form = AccommodationForm(data=self.accommodation_data, user=self.user)
        
        # Check if the user field is pre-populated with the logged-in user
        self.assertEqual(form.fields['user'].initial, self.user)

    def test_form_user_filter(self):
        # Create a second user
        another_user = User.objects.create_user(username='anotheruser', password='password123')

        # Initialize form with valid data and the first user
        form = AccommodationForm(data=self.accommodation_data, user=self.user)

        # Check that the queryset only contains the first user (not the second user)
        self.assertIn(self.user, form.fields['user'].queryset.all())
        self.assertNotIn(another_user, form.fields['user'].queryset.all())

    def test_form_save_creates_accommodation(self):
        # Initialize form with valid data and the user
        form = AccommodationForm(data=self.accommodation_data, user=self.user)

        # Check that the form is valid
        self.assertTrue(form.is_valid())

        # Save the form
        accommodation = form.save()

        # Ensure the accommodation is saved and has the correct user
        self.assertEqual(accommodation.user, self.user)
        self.assertEqual(accommodation.title, 'Test Accommodation')
        self.assertEqual(accommodation.location, 'Test Location')  # Modify this to match your model
        self.assertEqual(accommodation.bedroom_count, 3)
        self.assertEqual(accommodation.usd_rate, 100.00)


