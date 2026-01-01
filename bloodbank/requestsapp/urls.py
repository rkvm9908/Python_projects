from django.urls import path
from .views import dashboard, request_blood, donor_list,  update_request, admin_dashboard, admin_donor_list

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),  # User
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),  # Admin
    path('request/', request_blood, name='request_blood'),
    path('donor-list/<int:req_id>/', donor_list, name='donor_list'),
    path('update/<int:req_id>/<str:action>/', update_request, name='update_request'),
    path('admin-donors/', admin_donor_list, name='admin_donor_list'),
]
