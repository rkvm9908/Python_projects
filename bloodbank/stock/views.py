from django.shortcuts import render
from .models import BloodStock
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def blood_stock_view(request):
    stocks = BloodStock.objects.all()
    return render(request, 'stock/blood_stock.html', {'stocks': stocks})

def update_stock(request, stock_id):
    stock = get_object_or_404(BloodStock, id=stock_id)

    if request.method == 'POST':
        qty = request.POST.get('quantity')
        if qty.isdigit():
            stock.quantity = int(qty)
            stock.save()
            messages.success(
                request,
                f"{stock.blood_group} stock updated successfully 🩸"
            )
        else:
            messages.error(request, "Invalid quantity")

    return redirect('admin_dashboard')
