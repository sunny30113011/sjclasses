from courses.models import Category, Notification
from payments.models import Cart, AllAccessPlan

def lms_context(request):
    categories = Category.objects.all()[:10]
    cart_count = 0
    unread_notifications_count = 0
    user_notifications = []
    
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:8]

    # Active All-Access Pass Offer (None if offer is toggled off or inactive)
    active_all_access_plan = AllAccessPlan.get_active_plan()

    return {
        'nav_categories': categories,
        'cart_count': cart_count,
        'unread_notifications_count': unread_notifications_count,
        'user_notifications': user_notifications,
        'all_access_plan': active_all_access_plan,
        'has_all_access_offer': active_all_access_plan is not None,
    }
