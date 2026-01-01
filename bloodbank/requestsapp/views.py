from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
import threading
from django.conf import settings
from django.contrib.auth.models import User
from accounts.models import UserProfile
from .models import BloodRequest
from django.utils import timezone
from datetime import timedelta
from .utils import COMPATIBLE
from stock.models import BloodStock  # optional if you have stock management

# ===============================
# USER DASHBOARD
# ===============================
@login_required
def dashboard(request):
    user_requests = BloodRequest.objects.filter(user=request.user)
    user_requests = user_requests.exclude(id__isnull=True)
    context = {
        'total': user_requests.count(),
        'pending': user_requests.filter(status='Pending').count(),
        'approved': user_requests.filter(status='Approved').count(),
        'not_available': user_requests.filter(status='Not Available').count(),
        'requests': user_requests
    }
    return render(request, 'requestsapp/dashboard.html', context)


# ===============================
# REQUEST BLOOD PAGE (USER)
# ===============================
@login_required
def request_blood(request):
    if request.method == 'POST':
        blood_group = request.POST.get('blood_group')
        if blood_group:
            BloodRequest.objects.create(
                user=request.user,
                blood_group=blood_group
            )
        return redirect('dashboard')

    return render(request, 'requestsapp/request_blood.html')


# ===============================
# ADMIN: DONOR LIST & REQUEST
# ===============================
def send_email_async(subject, message, recipient):
    def task():
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [recipient],
                fail_silently=False
            )
        except Exception as e:
            print("EMAIL ERROR:", e)

    threading.Thread(target=task).start()
    
@staff_member_required
def donor_list(request, req_id):
    req = get_object_or_404(BloodRequest, id=req_id)
    compatible_groups = COMPATIBLE.get(req.blood_group, [])

    donors = UserProfile.objects.filter(blood_group__in=compatible_groups)

    if request.method == 'POST':
        selected = request.POST.getlist('donors')
        emails = [d.user.email for d in donors if str(d.id) in selected]

        if emails:
            send_email_async(
                subject="Urgent Blood Requirement",
                message=f"Urgent need for {req.blood_group} blood. Please contact hospital immediately.",
                recipients=emails
            )

            req.last_email_sent = timezone.now()
            req.save()

            messages.success(
                request,
                "✅ Email sent successfully! Donor search locked for 30 minutes."
            )

        return redirect('admin_dashboard')

    return render(request, 'requestsapp/find_donor.html', {
        'donors': donors,
        'req': req
    })

@staff_member_required
def admin_donor_list(request):
    donors = UserProfile.objects.all().order_by('blood_group')

    return render(request, 'requestsapp/admin_donor_list.html', {
        'donors': donors
    })

# ===============================
# ADMIN DASHBOARD
# ===============================
@staff_member_required
def admin_dashboard(request):
    requests = BloodRequest.objects.all().order_by('-created_at')
    stocks = BloodStock.objects.all()  # optional
    for r in requests:
        r.cooldown_active = False

        if r.last_email_sent:
            diff = timezone.now() - r.last_email_sent
            if diff < timedelta(minutes=30):
                r.cooldown_active = True
                r.remaining_seconds = int(1800 - diff.total_seconds())
            else:
                r.remaining_seconds = 0
    return render(request, 'requestsapp/admin_dashboard.html', {
        'requests': requests,
        'stocks': stocks
    })


# ===============================
# ADMIN: UPDATE REQUEST (APPROVE/NOT AVAILABLE)
# ===============================
@staff_member_required
def update_request(request, req_id, action):
    req = get_object_or_404(BloodRequest, id=req_id)

    stock = BloodStock.objects.filter(blood_group=req.blood_group).first()
    compatible_groups = COMPATIBLE.get(req.blood_group, [])

    if action == 'approve':
        if stock and stock.quantity > 0:
            req.status = 'Approved'
            stock.quantity -= 1
            stock.save()
        else:
            req.status = 'Not Available'

            donors = UserProfile.objects.filter(blood_group__in=compatible_groups)
            emails = [d.user.email for d in donors]

            if emails:
                send_email_async(
                    subject=f"Urgent need for {req.blood_group} blood",
                    message=f"Dear Donor,\n\nUrgently needed {req.blood_group} blood. Please contact the hospital immediately.",
                    recipients=emails
                )

    elif action == 'not_available':
        req.status = 'Not Available'

    req.save()
    return redirect('admin_dashboard')

