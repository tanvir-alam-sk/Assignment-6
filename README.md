# Inventory Management System API

## Overview
This project focuses on developing a Property Management System using the Django framework, integrating geospatial data storage and handling capabilities through PostgreSQL with the PostGIS extension. The system is designed to manage properties and their associated geolocations via the Django Admin interface and includes features such as hierarchical location management, user roles, and property localization.

## Project Scope
- **Database Setup**: Configure PostgreSQL with PostGIS to support geospatial data.
- **Model Definition**: Create Django models for locations, accommodations, and their localizations.
- **Admin Interface:**: Set up Django Admin with user permissions and filtering capabilities.
- **User Roles**: mplement user group permissions to control data access.
- **Frontend Development**: Provide a public-facing page for property owner registration.
- **CLI Command**: Develop a utility for generating a location-based sitemap in JSON format.

## Task Breakdown

### 1. Database Setup

- Install and configure **PostgreSQL** with the PostGIS extension for geospatial support.
- Create a PostgreSQL database and enable PostGIS features.

### 2. Project Initialization
- Initialize a Django project named **"Inventory Management."**
- Configure the database connection to use PostgreSQL with PostGIS.

### 3. Model Creation and Migration
- Define and migrate the following Django models:
- #### Location Model
  - #### Fields:
    -  id: Primary key, string (max 20 characters)
    -  title: Name, string (max 100 characters), required
    -  center: Geolocation, PostGIS point
    -  parent_id: Foreign key to self for hierarchical nesting
    -  location_type: Type of location (continent, country, state, city), string (max 20 characters)
    -  country_code: ISO country code, string (max 2 characters)
    -  state_abbr: State abbreviation, string (max 3 characters)
    -  city: City name, string (max 30 characters)
    -  created_at: Auto timestamp on create
    -  updated_at: Auto timestamp on update

- #### Accommodation Model
  - #### Fields:
    -    id: Primary key, string (max 20 characters)
    -    feed: Feed number, unsigned small integer, default is 0
    -    title: Name, string (max 100 characters), required
    -    country_code: ISO country code, string (max 2 characters), required
    -    bedroom_count: Unsigned integer
    -    review_score: Numeric with 1 decimal place, default is 0
    -    usd_rate: Price rate in USD, numeric with 2 decimal places
    -    center: Geolocation, PostGIS point
    -    images: Array of image URLs (max 300 characters each)
    -    location_id: Foreign key to Location
    -    amenities: JSONB array (max 100 characters each)
    -    user_id: Foreign key to Django's auth_user, auto-assigned on creation
    -    published: Boolean, default is false
    -    created_at: Auto timestamp on create
    -    updated_at: Auto timestamp on update

- #### LocalizeAccommodation Model
  - #### Fields:
      -  id: Primary key, auto incremented
      -  property_id: Foreign key to Accommodation
      -  language: Language code, string (max 2 characters)
      -  description: Localized description, text
      -  policy: JSONB dictionary (e.g., {"pet_policy": "value"})

- Run migrations to apply the models to the database.


### 4. Admin Configuration
  -  Create a superuser for the Django Admin interface.
  -  Register the models in the Admin interface with appropriate list views and filtering options.
  -  Populate initial location data (e.g., countries, states, cities).


### 5. User Groups and Permissions
  -  Create a Property Owners user group.
  -  Restrict users in this group to view, create, and update only their own properties.


### 6. Frontend Development
  -  Design a public-facing sign-up page for property owners to submit registration requests.


### 7. Command-Line Utility for Sitemap Generation
  -  Create a Django CLI command to generate a sitemap.json file for all country locations.
  -  URL format:
     https://www.xyz.com/location/[location_slug]
  -  JSON structure (sorted alphabetically):
  ```bash
        [
            {
                "USA": "usa",
                "locations": [
                { "Florida": "usa/florida" 
                },
                { "Texas": "usa/texas" }
                ]
            }
        ]
```

    


## Installation Instructions

1 **Clone the Repository:**: 
``` bash 
git clone https://github.com/tanvir-alam-sk/Assignment-6 inventory-management
cd inventory-management
```

2 **Set Up the Virtual Environment:**: 
```bash 
python3 -m venv venv
source venv/bin/activate
```

3 **Install Dependencies:**: 
```bash 
pip install -r requirements.txt
```

4 **Run Migrations:**: 
```bash 
docker exec -it  assignment-6-web-1 python manage.py makemigrations
docker exec -it assignment-6-web-1 python manage.py migrate
```

5 **Create Superuser:**: 
```bash 
docker exec -it assignment-6-web-1 python manage.py createsuperuser
```

6 **Docker Run**: 
```bash 
docker-compose build
docker-compose up
docker-compose down
```

7 **Generate Sitemap**: 
```bash 
docker exec -it web python manage.py createsuperuser
```

8 **Unit Testing**: 
```bash 
docker-compose exec assignment-6-web python manage.py test location
```


- **Contributing**: Contributions are welcome, especially from individuals with experience in Django Rest Framework, authentication, authorization, and payment systems like M-PESA. If you're interested in contributing to these areas, please reach out to me via [Twitter](https://twitter.com/MungaiMbuthi) for collaboration.

## Installation

This project is containerized using Docker, ensuring a consistent and isolated environment for development and deployment.

### Prerequisites

- **Docker**: You need to have Docker installed on your local machine. You can download and install Docker from the [official Docker website](https://www.docker.com/get-started).

### Getting Started with Docker
If you're new to Docker, I recommend reading these articles for a solid introduction:
- [Getting started with Docker](https://dev.to/mbuthi/docker-2oge)
- [DevOps with Fast API & PostgreSQL: How to containerize Fast API Application with Docker](https://dev.to/mbuthi/devops-with-fast-api-postgresql-how-to-containerize-fast-api-application-with-docker-1jdb)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mbuthi/Inventory_management_system.git
   ```

2. **Build the Docker Containers**:
   Navigate to the root directory of the project and run:
   ```bash
   docker-compose -f docker-compose.yml build --no-cache
   ```

3. **Start the Containers**:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

### Project Structure


```text
/project-root
├── inventory_management/
│   ├── __init__.py            # Package initialization
│   ├── settings.py            # Django project settings
│   ├── urls.py                # URL configuration
│   └── wsgi.py                # WSGI entry point for the project
├── apps/                      # Custom Django applications
│   ├── location/              # Location management app
│   │   ├── models.py          # Location model definitions
│   │   ├── views.py           # Views for handling location logic
│   │   ├── admin.py           # Admin configuration for locations
│   │   └── migrations/        # Database migrations for locations
│   ├── accommodation/         # Accommodation management app
│   │   ├── models.py          # Accommodation model definitions
│   │   ├── views.py           # Views for handling accommodation 
├── templates/                 # HTML templates for the project
├── static/                    # Static files (CSS, JS, images)
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```


### Running the Application

Once the Docker containers are up and running, the Inventory Management System API will be accessible at the designated port.

In your browser, you can access the API through HTTP://localhost:8000/api/v1

## API Endpoints

### Items
- `admin /`: Add a new inventory item.
- `/register`: Register a new user.
- `/welcome `: Welcome Registed a new user.


