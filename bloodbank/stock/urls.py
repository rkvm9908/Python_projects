from django.urls import path
from .views import blood_stock_view, update_stock

urlpatterns = [
    path('', blood_stock_view, name='blood_stock'),
    path('update/<int:stock_id>/', update_stock, name='update_stock'),
]
