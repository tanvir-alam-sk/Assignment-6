import json
from django.core.management.base import BaseCommand
from location.models import Location

class Command(BaseCommand):
    help = "Generate a sitemap.json file for all country locations"

    def handle(self, *args, **kwargs):
        # Fetch all countries with their hierarchical children
        countries = (
            Location.objects.filter(location_type="country")
            .prefetch_related("children__children")
            .order_by("title")
        )

        sitemap = []

        # Build the sitemap structure
        for country in countries:
            country_data = {
                country.title: country.id.lower(),
                "locations": self.get_child_locations(country)
            }
            sitemap.append(country_data)

        # Save the sitemap as a JSON file
        with open("sitemap.json", "w") as f:
            json.dump(sitemap, f, indent=4)

        self.stdout.write(self.style.SUCCESS("sitemap.json generated successfully!"))

    def get_child_locations(self, parent_location):
        """
        Recursive function to get child locations (state -> city).
        """
        child_locations = parent_location.children.all().order_by("title")
        child_list = []

        for child in child_locations:
            # Get the child's children recursively
            if child.location_type == "state":
                state_data = {
                    child.title: f"{parent_location.id.lower()}/{child.id.lower()}",
                    "locations": self.get_child_locations(child)
                }
                child_list.append(state_data)
            else:  # City or leaf location
                child_list.append({
                    child.title: f"{parent_location.id.lower()}/{child.id.lower()}"
                })

        return child_list
