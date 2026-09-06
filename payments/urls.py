from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:course_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/<int:course_id>/', views.checkout, name='checkout_course'),
    path('project/<int:project_id>/', views.checkout_project, name='checkout_project'),
    path('submit-project-payment/', views.submit_project_payment, name='submit_project_payment'),
    path('submit-manual-payment/', views.submit_manual_payment, name='submit_manual_payment'),
    path('all-access/', views.all_access_checkout, name='all_access_checkout'),
    path('all-access/submit/', views.submit_all_access_payment, name='submit_all_access_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
]


