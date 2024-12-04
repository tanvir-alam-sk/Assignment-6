from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.exceptions import ValidationError


def index(request):
    """Display a welcome message to the new user."""
    return HttpResponse("<h1>Welcome as a New User</h1>")


def validate_registration_data(username, email, password, confirm_password):
    """Helper function to validate registration form data."""
    
    if password != confirm_password:
        raise ValidationError("Passwords do not match.")
    
    if User.objects.filter(username=username).exists():
        raise ValidationError("Username already taken.")
    
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already in use.")


def create_new_user(username, email, password):
    """Helper function to create a new user."""
    
    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()
    
    # Assign the user to the "Property Owners" group
    group = Group.objects.get(name="Property Owners")
    user.groups.add(group)
    
    return user


def register(request):
    """View for user registration."""
    if request.method == 'POST':
        # Collect data from the form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        try:
            # Validate and create a new user
            validate_registration_data(username, email, password, confirm_password)
            user = create_new_user(username, email, password)
            
            messages.success(request, "Account created successfully!")
            return redirect('/welcome') 
        
        except ValidationError as e:
            # Handle validation errors
            messages.error(request, str(e))
            return redirect('register')
        except Exception as e:
            # Handle any other errors
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            return redirect('register')

    return render(request, 'register.html')
