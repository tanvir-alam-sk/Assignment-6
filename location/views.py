from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.models import User,Group
from django.contrib import messages
# from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Welcone As a New User")


def register(request):
    print("hallo")
    if request.method == 'POST':
        # Collect data from the form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register')

        # Create a new user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            group = Group.objects.get(name="Property Owners")
            user.groups.add(group)
            messages.success(request, "Account created successfully!")
            return redirect('/welcome') 
        except Exception as e:
            messages.error(request, str(e))
            return redirect('/welcome')

    return render(request, 'register.html')

