from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import UserProfile


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')
        blood_group = request.POST.get('blood_group')
        mobile = request.POST.get('mobile')

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # ✅ ONLY user fields here
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        # ✅ Extra fields in profile
        profile = user.userprofile
        profile.blood_group = blood_group
        profile.mobile = mobile
        profile.save()
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials!")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

import random
from django.core.mail import send_mail

# Store OTP temporarily (for simplicity, session)
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            request.session['otp'] = otp
            request.session['reset_user'] = user.id

            # Send OTP email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}',
                'admin@bloodbank.com',
                [email],
                fail_silently=False
            )
            messages.success(request, f'OTP sent to {email}')
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, "Email not found!")

    return render(request, 'accounts/forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        otp = str(request.session.get('otp'))
        if entered_otp == otp:
            messages.success(request, "OTP verified! Please reset your password.")
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid OTP!")

    return render(request, 'accounts/verify_otp.html')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('reset_password')

        user_id = request.session.get('reset_user')
        if user_id:
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            # Clear session
            request.session.pop('otp', None)
            request.session.pop('reset_user', None)
            messages.success(request, "Password reset successful! Please login.")
            return redirect('login')
        else:
            messages.error(request, "Session expired. Try again.")
            return redirect('forgot_password')

    return render(request, 'accounts/reset_password.html')
