from django.contrib import admin

# Register your models here.
from MotorInsuranceCompany.models import User, Vehicle, Owner, Policy, Claim
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserModelAdmin(BaseUserAdmin):
    list_display = ["id", "email", "name", "tc", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name", "tc"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "tc", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []
admin.site.register(User, UserModelAdmin)



class VehicleAdmin(admin.ModelAdmin):
    list_display = ["id", "vehicle_number", "make", "user", "registration_date", "purchase_price"]
    search_fields = ["vehicle_number"]
    ordering = ["vehicle_number"]
    fieldsets = [
        ("User Detail", {"fields": ["user"]}),
        ("Vehicle info", {"fields": ["vehicle_number", "vehicle_type", "make", "model", "fuel_type", "registration_date", "seats", "purchase_price"]}),
    ]
admin.site.register(Vehicle, VehicleAdmin)



# class OwnerAdmin(admin.ModelAdmin):
#     list_display =  ["id", "name", "date_of_birth", "vehicle", "gender", "address"]
#     search_fields = ["name"]
#     fieldsets = [
#         ("Vehicle Detail", {"fields": ["vehicle"]}),
#         ("Owner info", {"fields": ["name", "date_of_birth", "gender", "address"]}),
#     ]
#     ordering = ["name"]
# admin.site.register(Owner, OwnerAdmin)



class PolicyAdmin(admin.ModelAdmin):
    list_display = ['id', 'policy_number', 'vehicle', 'total_premium', 'policy_status']
    search_fields = ['vehicle']
    fieldsets = [
        ("Vehicle Detail", {"fields": ["vehicle"]}),
        ("Policy info", {"fields": ["policy_number", "description", "insured_declared_value", "policy_status", "payment_status"]}),
        ("Validity Period", {"fields": ["effective_from", "expires_on"]}),
        ("Premium Breakup", {"fields": ["base_premium", "personal_accident_premium", "passenger_cover_premium", "breakdown_assistance_premium", "total_premium"]}),
    ]
    ordering = ["vehicle"]
admin.site.register(Policy, PolicyAdmin)



class ClaimAdmin(admin.ModelAdmin) :
    list_display = ['id', 'policy', 'date_of_claim', 'reason_for_claim', 'claim_status']
    search_fields = ['policy']
    fieldsets = [
        ("Vehicle Detail", {"fields": ["vehicle"]}),
        ("Policy Detail", {"fields": ["policy"]}),
        ("Claim Info", {"fields": ["date_of_claim", "description_of_incident", "reason_for_claim", "claim_status"]}),
        ("Claimant's Bank Details", {"fields": ["claimant_bank_name", "claimant_account_number"]})
    ]
    ordering = ["policy"]
admin.site.register(Claim, ClaimAdmin)