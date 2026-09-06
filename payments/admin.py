from django.contrib import admin
from .models import Payment, Coupon, Cart, AllAccessPlan

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'is_all_access', 'amount', 'payment_status', 'utr', 'paid_on')
    list_filter = ('is_all_access', 'payment_status', 'paid_on')
    search_fields = ('user__username', 'user__email', 'course__title', 'utr')
    list_editable = ('payment_status',)


@admin.register(AllAccessPlan)
class AllAccessPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'offer_price', 'original_price', 'is_active')
    list_editable = ('offer_price', 'is_active')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'active', 'valid_until')
    list_filter = ('active',)
    search_fields = ('code',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'added_at')
    search_fields = ('user__username', 'course__title')
