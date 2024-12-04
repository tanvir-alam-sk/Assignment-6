import os
import json
from uuid import uuid4
from decimal import Decimal
from django.db import models
from django.contrib.gis.db import models as geomodels  # For spatial fields
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify


# Utility Functions
def validate_amenities(value):
    """
    Validate amenities JSON field. Ensures each amenity is a string with a max length of 100 characters.
    """
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            raise ValidationError("Invalid JSON format for amenities.")

    if not isinstance(value, list):
        raise ValidationError("Amenities must be a list of strings.")
    
    for amenity in value:
        if not isinstance(amenity, str):
            raise ValidationError(f"'{amenity}' is not a string.")
        if len(amenity) > 100:
            raise ValidationError(f"Amenity '{amenity}' exceeds 100 characters.")


def upload_accommodation_image(instance, filename):
    """
    Upload handler for Accommodation images, renames to a slugified filename with a unique identifier.
    """
    ext = os.path.splitext(filename)[1].lower()
    unique_id = uuid4().hex[:8]
    slugified_name = slugify(os.path.splitext(filename)[0])
    new_filename = f"{slugified_name}-{unique_id}{ext}"
    upload_path = f"accommodations/{instance.accommodation.id}/images/"
    return os.path.join(upload_path, new_filename)


### Models

class Location(models.Model):
    """
    Location model for storing hierarchical geographic data.
    """
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=100)
    center = geomodels.PointField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    location_type = models.CharField(
        max_length=20,
        choices=[('country', 'Country'), ('state', 'State'), ('city', 'City')],
        default='city'
    )
    country_code = models.CharField(max_length=2)
    state_abbr = models.CharField(max_length=3, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    def __str__(self):
        return f"{self.title} ({self.location_type})"


class Accommodation(models.Model):
    """
    Accommodation model to store details of various properties.
    """
    id = models.CharField(max_length=20, primary_key=True)
    title = models.CharField(max_length=100)
    feed = models.PositiveSmallIntegerField(default=0)
    country_code = models.CharField(max_length=2)
    bedroom_count = models.PositiveIntegerField()
    review_score = models.DecimalField(
        max_digits=3, decimal_places=1, default=0,
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('5.0'))]
    )
    usd_rate = models.DecimalField(max_digits=10, decimal_places=2)
    center = geomodels.PointField()
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name="accommodations")
    amenities = models.JSONField(null=True, blank=True, validators=[validate_amenities])
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Accommodation"
        verbose_name_plural = "Accommodations"

    def __str__(self):
        return f"{self.title} - {self.location.title}"


class AccommodationImage(models.Model):
    """
    Image model for Accommodation.
    """
    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.CASCADE, related_name='accommodation_images'
    )
    image = models.ImageField(upload_to=upload_accommodation_image)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.accommodation.title}"


class LocalizeAccommodation(models.Model):
    """
    Localized details for Accommodation, supporting multiple languages.
    """
    accommodation = models.ForeignKey(
        Accommodation, on_delete=models.CASCADE, related_name='localized'
    )
    language = models.CharField(max_length=2)  # Language code (ISO 639-1)
    description = models.TextField()
    policy = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('accommodation', 'language')
        verbose_name = "Localized Accommodation"
        verbose_name_plural = "Localized Accommodations"

    def __str__(self):
        return f"{self.accommodation.title} - {self.language}"
