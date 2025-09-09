from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import SubscriptionPlan, Subscription, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ("stripe_payment_id", "amount", "status", "created_at")
    can_delete = False
    show_change_link = True


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(ModelAdmin):
    list_display = ("name", "price", "duration_months", "created_at")
    search_fields = ("name", "stripe_plan_id")
    list_filter = ("duration_months", "created_at")
    ordering = ("-created_at",)


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ("user", "plan", "status", "start_date", "end_date")
    search_fields = ("user__username", "user__email", "plan__name")
    list_filter = ("status", "plan__name", "start_date", "end_date")
    ordering = ("-start_date",)
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ("stripe_payment_id", "subscription", "amount", "status", "created_at")
    search_fields = ("stripe_payment_id", "subscription__user__username", "subscription__user__email")
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)
