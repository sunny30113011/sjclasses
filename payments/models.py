from django.db import models
from django.conf import settings
from courses.models import Course

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="e.g. 20 for 20% OFF")
    active = models.BooleanField(default=True)
    valid_until = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}% OFF)"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username}'s Cart - {self.course.title}"


class Payment(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    is_all_access = models.BooleanField(default=False, help_text="Designates whether this payment is for the All-Courses Pass")

    amount = models.DecimalField(max_digits=8, decimal_places=2)

    utr = models.CharField(max_length=50)

    screenshot = models.ImageField(upload_to='payments/', blank=True, null=True)

    payment_status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='Pending'
    )

    paid_on = models.DateTimeField(auto_now_add=True)

    admin_note = models.TextField(blank=True)

    class Meta:
        ordering = ['-paid_on']

    def __str__(self):
        item = "All-Access Pass" if self.is_all_access else (self.course.title if self.course else "Item")
        return f"Payment #{self.id} - {self.user.username} - {item} - UTR: {self.utr} ({self.payment_status})"


class AllAccessPlan(models.Model):
    title = models.CharField(max_length=150, default="All-Access VIP Master Pass")
    tagline = models.CharField(max_length=255, default="Unlock Every Single Course with One Single Amount (1 Year Access)")
    original_price = models.DecimalField(max_digits=8, decimal_places=2, default=4999.00)
    offer_price = models.DecimalField(max_digits=8, decimal_places=2, default=999.00)
    duration_days = models.PositiveIntegerField(default=365, help_text="Pass access duration in days (default 365 days / 1 year)")
    features = models.TextField(
        default="Full 1 Year Access to all current and upcoming courses (365 Days)\nInstant certificate eligibility on completion\nAccess to all downloadable project source codes\nDirect instructor support in Q&A\nResume & placement drive access",
        help_text="Line-separated list of benefits shown to students"
    )
    is_active = models.BooleanField(default=True)
    upi_id = models.CharField(max_length=100, default="sunnywaghmode8@axl")
    upi_number = models.CharField(max_length=20, default="7218858764")

    @classmethod
    def get_plan(cls):
        """Get the primary plan configuration or create a default one."""
        plan = cls.objects.first()
        if not plan:
            plan = cls.objects.create()
        return plan

    @classmethod
    def get_active_plan(cls):
        """Get the active plan if offer is currently turned ON, else None."""
        return cls.objects.filter(is_active=True).first()

    def get_features_list(self):
        return [f.strip() for f in self.features.split('\n') if f.strip()]

    def __str__(self):
        return f"{self.title} (₹{self.offer_price})"
