from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from leaflet.admin import LeafletGeoAdmin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import Location, Accommodation, AccommodationImage, LocalizeAccommodation


### RESOURCE CLASS FOR LOCATION ###
class LocationResource(resources.ModelResource):
    """Defines import/export behavior for the Location model."""
    
    class Meta:
        model = Location
        fields = ('id', 'title', 'location_type', 'country_code', 'state_abbr', 'city', 'center')


### LOCATION ADMIN ###
@admin.register(Location)
class LocationAdmin(ImportExportModelAdmin, LeafletGeoAdmin):
    """Admin interface for managing Location model."""
    
    resource_class = LocationResource
    list_display = ('id', 'title', 'location_type', 'country_code', 'state_abbr', 'city')
    search_fields = ('title', 'country_code', 'state_abbr', 'city')
    list_filter = ('location_type', 'country_code')


### INLINE ADMIN FOR ACCOMMODATION IMAGES ###
class AccommodationImageInline(admin.TabularInline):
    """Inline admin for managing images related to an Accommodation."""
    
    model = AccommodationImage
    extra = 1
    fields = ('image',)
    readonly_fields = ('uploaded_at',)


### ACCOMMODATION ADMIN ###
@admin.register(Accommodation)
class AccommodationAdmin(LeafletGeoAdmin):
    """Admin interface for managing Accommodation model."""

    list_display = ('id', 'title', 'country_code', 'bedroom_count', 'review_score', 'usd_rate', 'center', 'location', 'published', 'created_at', 'updated_at')
    list_filter = ('published', 'location')
    search_fields = ('title', 'country_code', 'location__title')
    ordering = ('-created_at',)
    inlines = [AccommodationImageInline]

    def get_queryset(self, request):
        """Show only accommodations created by the logged-in user if in 'Property Owners' group."""
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Property Owners').exists():
            return qs.filter(user=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        """Assign the logged-in user as the creator if not already set."""
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        """Allow Property Owners to edit only their accommodations."""
        if obj and obj.user != request.user:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Allow Property Owners to delete only their accommodations."""
        if obj and obj.user != request.user:
            return False
        return super().has_delete_permission(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Restrict user selection to the logged-in user."""
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


### ACCOMMODATION IMAGE ADMIN ###
@admin.register(AccommodationImage)
class AccommodationImageAdmin(admin.ModelAdmin):
    """Admin interface for the AccommodationImage model."""
    
    list_display = ('accommodation', 'image', 'uploaded_at')
    search_fields = ('accommodation__title',)


### LOCALIZED ACCOMMODATION ADMIN ###
@admin.register(LocalizeAccommodation)
class LocalizeAccommodationAdmin(admin.ModelAdmin):
    """Admin interface for localized accommodation information."""
    
    list_display = ('id', 'accommodation', 'language', 'description')
    list_filter = ('language',)
    search_fields = ('description', 'language')
