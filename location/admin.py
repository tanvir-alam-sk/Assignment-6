from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import Location, Accommodation, AccommodationImage, LocalizeAccommodation

# Register your models here.
@admin.register(Location)
class LocationAdmin(LeafletGeoAdmin):
    list_display = ('id', 'title', 'location_type', 'country_code', 'state_abbr', 'city')
    search_fields = ('title', 'country_code', 'state_abbr', 'city')
    list_filter = ('location_type', 'country_code')


class AccommodationImageInline(admin.TabularInline):
    """
    Inline admin for managing images related to an Accommodation.
    """
    model = AccommodationImage
    extra = 1  
    fields = ('image',)  
    readonly_fields = ('uploaded_at',)


@admin.register(Accommodation)
class AccommodationAdmin(LeafletGeoAdmin):
    list_display = ('id', 'title', 'country_code', 'bedroom_count', 'review_score', 'usd_rate', 'center', 'location', 'published', 'created_at', 'updated_at')
    list_filter = ('published', 'location') 
    search_fields = ('title', 'country_code', 'location__title')
    ordering = ('-created_at',)
    inlines = [AccommodationImageInline]  
    

    def get_queryset(self, request):
        """Limit queryset to show only accommodations created by the logged-in user for Property Owners."""
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Property Owners').exists():
            return qs.filter(user_id=request.user)
        return qs  

    def save_model(self, request, obj, form, change):
        """Automatically assign the logged-in user as the creator if not set."""
        if not obj.user_id:
            obj.user_id = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        """Allow Property Owner users to edit only their own accommodations."""
        if obj and obj.user_id != request.user:
            return False  
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """Allow Property Owner users to delete only their own accommodations."""
        if obj and obj.user_id != request.user:
            return False  
        return super().has_delete_permission(request, obj)


@admin.register(AccommodationImage)
class AccommodationImageAdmin(admin.ModelAdmin):
    """
    Admin interface for the AccommodationImage model.
    """
    list_display = ('accommodation', 'image', 'uploaded_at')
    search_fields = ('accommodation__title',)


@admin.register(LocalizeAccommodation)
class LocalizeAccommodationAdmin(admin.ModelAdmin):
    list_display = ('id', 'accommodation', 'language', 'description')
    list_filter = ('language',)
    search_fields = ('description', 'language')
