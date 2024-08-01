from rest_framework import serializers
from MotorInsuranceCompany.models import User, Vehicle, Policy, Claim #, Owner
from datetime import date
from MotorInsuranceCompany.views import calculate_base_premium, calculate_idv
from django.utils import timezone
from datetime import timedelta


from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from MotorInsuranceCompany.utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2', 'tc']
        extra_kwargs={
            'password':{'write_only':True}
        }
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match.")
        return attrs
    
    def create(self, validate_data):
        return User.objects.create_user(**validate_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['password', 'password2']
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password and Confirm Password doesn't match.")
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email = email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded UID', uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('Password Reset Token', token)
            link = 'http://localhost:5173/reset-password/'+uid+'/'+token
            print('Password Reset Link', link)
            # Send EMail
            body = 'Click Following Link to Reset Your Password :\n'+link
            data = {
                'subject':'Reset Your Password',
                'body':body,
                'to_email':user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError('You are not a Registered User')

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Password and Confirm Password doesn't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError('Token is not Valid or Expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError('Token is not Valid or Expired')



class AddVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['vehicle_type', 'vehicle_number', 'make', 'model', 'fuel_type', 'registration_date', 'seats', 'purchase_price']

class RetrieveVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_type', 'vehicle_number', 'make', 'model', 'fuel_type', 'registration_date', 'seats', 'purchase_price', 'user']



# class OwnerSerializer(serializers.ModelSerializer):
#     vehicle_number = serializers.CharField(write_only=True)
#     class Meta:
#         model = Owner
#         fields = ('id', 'name', 'date_of_birth', 'gender', 'address', 'vehicle_number')
    
#     def create(self, validated_data):
#         vehicle_number = validated_data.pop('vehicle_number')
#         try:
#             vehicle = Vehicle.objects.get(vehicle_number=vehicle_number)
#         except Vehicle.DoesNotExist:
#             raise serializers.ValidationError(f"No vehicle found with number {vehicle_number}")
#         return Owner.objects.create(vehicle=vehicle, **validated_data)


class PolicySerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(write_only=True)
    personal_accident = serializers.BooleanField(write_only=True)
    passenger_cover = serializers.BooleanField(write_only=True)
    breakdown_assistance = serializers.BooleanField(write_only=True)
    vehicle = serializers.CharField(source='vehicle.vehicle_number', read_only=True)

    class Meta:
        model = Policy
        fields = ('id', 'policy_number', 'description', 'base_premium', 'personal_accident_premium', 
                  'passenger_cover_premium', 'breakdown_assistance_premium', 'total_premium', 
                  'insured_declared_value', 'policy_status', 'payment_status', 'effective_from', 'expires_on', 
                  'vehicle_number', 'personal_accident', 'passenger_cover', 'breakdown_assistance', 'vehicle')
    
    def create(self, validated_data):
        vehicle_number = validated_data.pop('vehicle_number')
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vehicle_number)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError(f"No vehicle found with number {vehicle_number}")
        validated_data['vehicle'] = vehicle
        try:
            policy = Policy.objects.get(vehicle_id=vehicle.id)
        except Policy.DoesNotExist:
            pass
        else:
            if policy.policy_status == "Rejected" or policy.policy_status == "Expired":
                policy.delete()
            else:
                raise serializers.ValidationError(f"Vehicle already has an Applied Proposal with Policy Status - {policy.policy_status}")
        validated_data['policy_number'] = "MSPOL"+str(vehicle.id)
        age_of_vehicle = date.today().year - vehicle.registration_date.year
        validated_data['base_premium'] = calculate_base_premium(vehicle.vehicle_type, age_of_vehicle)
        total = validated_data['base_premium']
        if validated_data.pop('personal_accident'):
            validated_data['personal_accident_premium'] = 11*12
            total += validated_data['personal_accident_premium']
        if validated_data.pop('passenger_cover'):
            validated_data['passenger_cover_premium'] = 21*12
            total += validated_data['passenger_cover_premium']
        if validated_data.pop('breakdown_assistance'):
            validated_data['breakdown_assistance_premium'] = 3*12
            total += validated_data['breakdown_assistance_premium']
        validated_data['total_premium'] = total
        validated_data['insured_declared_value'] = calculate_idv(age_of_vehicle, vehicle.purchase_price)
        validated_data['policy_status'] = 'Pending For Approval'
        return Policy.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        if 'payment_status' in validated_data:
            instance.payment_status = validated_data['payment_status']
            if instance.payment_status:
                instance.policy_status = "Active"
                instance.effective_from = timezone.now().date()
                instance.expires_on = instance.effective_from + timedelta(days=365)
        instance.save()
        return instance

class SendPolicyOnEmailSerializer(serializers.Serializer):
    vehicle_number = serializers.CharField(max_length=15)
    class Meta:
        fields = ['email', 'vehicle_number']

    def validate(self, attrs):
        vehicle_number = attrs.get('vehicle_number')
        vehicle = Vehicle.objects.get(vehicle_number = vehicle_number)
        if User.objects.filter(id=vehicle.user_id).exists():
            user = User.objects.get(id=vehicle.user_id)
            policy = Policy.objects.get(vehicle_id=vehicle.id)
            body = f'''Your Vehicle is now guarded by the Motor Shield.\n
                    Your payment has been completed and your policy has been activated.\n
                    Policy Number  :   {policy.policy_number}\n
                    Policy Holder  :   {user.name}\n
                    Vehicle Number :   {vehicle.vehicle_number}\n
                    Total Premium Charged  :   {policy.total_premium}\n
                    Effective From  :   {policy.effective_from}\n
                    Expires On  :   {policy.expires_on}\n
                    \n\n\n
                    Thank You.
                    Now, Tighten your seat belt and Enjoy a stress-free ride with Motor Shield guarding your Vehicle\n'''
            data = {
                'subject' : 'Vehical Insurance Purchase Invoice',
                'body' : body,
                'to_email':user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError('You are not a Registered User')



class ClaimSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(write_only=True)
    vehicle = serializers.CharField(source='vehicle.vehicle_number', read_only=True)
    policy = serializers.CharField(read_only=True)
    date_of_claim = serializers.DateField(read_only=True)
    
    class Meta:
        model = Claim
        fields = ('id', 'description_of_incident', 'reason_for_claim', 'date_of_claim', 'claim_status', 'claimant_bank_name', 'claimant_account_number', 'vehicle_number', 'policy', 'vehicle')

    def create(self, validated_data):
        vehicle_number = validated_data.pop('vehicle_number')
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vehicle_number)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError(f"No vehicle found with number {vehicle_number}")
        validated_data['vehicle'] = vehicle
        try:
            policy = Policy.objects.get(vehicle_id = vehicle.id)
        except:
            raise serializers.ValidationError(f"No Insurnce Policy found for vehicle number {vehicle_number}")
        if policy.policy_status != 'Active':
            raise serializers.ValidationError(f"Vehicle Number-{vehicle_number} doesn't have an ACTIVE policy")
        validated_data['policy'] = policy
        validated_data['date_of_claim'] = date.today()
        validated_data['claim_status'] = 'Pending'
        return Claim.objects.create(**validated_data)