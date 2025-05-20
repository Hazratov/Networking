# webapp/admin.py

from django.contrib import admin
from .models import Record, Lead, Communication

# === ACTIONS for Lead ===
@admin.action(description="Mark selected leads as Contacted")
def mark_as_contacted(modeladmin, request, queryset):
    queryset.update(status="contacted")

@admin.action(description="Mark selected leads as Closed")
def mark_as_closed(modeladmin, request, queryset):
    queryset.update(status="closed")

class LeadAdmin(admin.ModelAdmin):
    list_display = ('customer', 'status', 'assigned_to', 'created_at')
    list_filter = ('status', 'assigned_to', 'created_at')
    search_fields = ('customer__first_name', 'customer__last_name', 'assigned_to__username')
    actions = [mark_as_contacted, mark_as_closed]

# === Record Admin ===
class RecordAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'city', 'country', 'created_by')
    list_filter = ('city', 'country', 'created_by')
    search_fields = ('first_name', 'last_name', 'email', 'phone')

# === Communication Admin ===
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'type', 'date')
    list_filter = ('type', 'date')
    search_fields = ('customer__first_name', 'customer__last_name', 'note')

# === Register Models ===
admin.site.register(Record, RecordAdmin)
admin.site.register(Lead, LeadAdmin)
admin.site.register(Communication, CommunicationAdmin)
