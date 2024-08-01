from django.db import models
from django.utils import timezone
from datetime import timedelta
# Create your models here.
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, name, tc, password=None, password2=None):
        """
        Creates and saves a User with the given email, name, tc and password.
        """
        if not email:
            raise ValueError("User must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, tc, password=None):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

#Custom User Model
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="Email",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'tc']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin



class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vtype = (
        ('Two Wheeler', 'Two Wheeler'),
        ('Four Wheeler', 'Four Wheeler'),
        ('Commercial Vehicle', 'Commercial Vehicle'),
    )
    vehicle_type = models.CharField(max_length=50, choices=vtype)
    vehicle_number = models.CharField(max_length=15)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    ftype = (
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    )
    fuel_type = models.CharField(max_length=15, choices=ftype)
    registration_date = models.DateField()
    seats = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return self.vehicle_number

class Owner(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gen = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Undisclosed', 'Undisclosed'),
    )
    gender = models.CharField(max_length=15, choices=gen)
    address = models.CharField(max_length=300)


class Policy(models.Model):
    policy_number = models.CharField(max_length=20, null=False, default='MSPOL')
    vehicle = models.ForeignKey('Vehicle', on_delete=models.CASCADE)
    description = models.TextField(max_length=1000, default='This Insurance Policy will provide financial protection against damage or loss to your vehicle due to accidents, theft, or natural disasters, as well as covers the liability claims arising from third-party injuries or property damage.')
    base_premium = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    personal_accident_premium = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    passenger_cover_premium = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    breakdown_assistance_premium = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_premium = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    insured_declared_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = (
        ('Active', 'Active'),
        ('Pay to Activate Your Policy', 'Pay to Activate Your Policy'),
        ('Pending For Approval', 'Pending For Approval'),
        ('Rejected', 'Rejected'),
        ('Expired', 'Expired'),
    )
    policy_status = models.CharField(max_length=50, choices=status, default= 'Pending For Approval')
    payment_status = models.BooleanField(default=False)
    effective_from = models.DateField(default=None, null=True, blank=True)
    expires_on = models.DateField(default=None, null=True, blank=True)

    def __str__(self):
        return self.policy_number

    def save(self, *args, **kwargs):
        self.total_premium = self.base_premium + self.personal_accident_premium + self.passenger_cover_premium + self.breakdown_assistance_premium
        if self.payment_status and not self.effective_from:
            self.effective_from = timezone.now().date()
            self.expires_on = self.effective_from + timedelta(days=365)
        if self.expires_on and self.expires_on < timezone.now().date():
            self.policy_status = "expired"
        super().save(*args, **kwargs)



class Claim(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Settled', 'Settled'),
        ('Rejected', 'Rejected'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE)
    date_of_claim = models.DateField()
    description_of_incident = models.TextField()
    reason_for_claim = models.CharField(max_length=50)
    claim_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    claimant_bank_name = models.CharField(max_length=80)
    claimant_account_number = models.CharField(max_length=20)

    def __str__(self):
        return str(self.id)