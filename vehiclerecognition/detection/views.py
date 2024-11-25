from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import ImageUploadForm
from PIL import Image
import numpy as np
import pytesseract
import os


# Replace 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' with the actual installation path on your system
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load mappings of state and district codes (this should be a dictionary or function you define)
state_district_map = {
    "KA": "Karnataka",
    "MH": "Maharashtra",
    "DL": "Delhi",
    "TN": "TamilNadu",
    # Add other mappings as needed
}

# Function to extract state and district from the vehicle number
def extract_state_and_district(plate_text):
    # Extract the first two characters to identify the state
    state_code = plate_text[:2].upper()
    state = state_district_map.get(state_code, "Unknown State")
    # Add custom logic here if you want to extract district codes or other details from the plate text
    return state

# Home view
def home_view(request):
    return render(request, 'base.html')

# Register view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('upload_image')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = UserCreationForm()
    return render(request, 'detection/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('upload_image')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login details.")
    else:
        form = AuthenticationForm()
    return render(request, 'detection/login.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# Upload Image view for vehicle number plate detection
def upload_image_view(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to upload images.")
        return redirect('login')

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']

            try:
                img = Image.open(image)
                
                # Use pytesseract to extract text from the image
                plate_text = pytesseract.image_to_string(img, config='--psm 8')
                plate_text = plate_text.replace("\n", "").strip()  # Clean up the text

                if plate_text:
                    # Extract state and district from the detected text
                    state = extract_state_and_district(plate_text)
                    result = f"Detected Vehicle Number: {plate_text}, State: {state}"
                else:
                    result = "No text detected. Please try again with a clearer image."

                # Return the result or render a template with the result
                return render(request, 'detection/result.html', {'prediction': result})

            except Exception as e:
                messages.error(request, f"An error occurred while processing the image: {str(e)}")
                return redirect('upload_image')
        else:
            messages.error(request, "Please upload a valid image.")

    else:
        form = ImageUploadForm()

    return render(request, 'detection/upload_image.html', {'form': form})

# Contact view
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Logic to handle contact form submission (e.g., sending an email)
        # For now, just display a success message
        if name and email and subject and message:
            messages.success(request, "Thank you for reaching out! We will get back to you soon.")
            return redirect('contact')  # Redirect to contact page after submission
        else:
            messages.error(request, "All fields are required.")
    
    return render(request, 'detection/contact.html')
# Services view
def services_view(request):
    # You can add additional logic here in the future if needed
    return render(request, 'detection/services.html')