from rest_framework import serializers
from MotorInsuranceCompany.models import User, Vehicle, Owner, Policy, Claim
from datetime import date
from MotorInsuranceCompany.views import calculate_base_premium, calculate_idv

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
        link = 'http://localhost:3000/reset/'+uid+'/'+token
        print('Password Reset Link', link)
        # Send EMail
        body = 'Click Following Link to Reset Your Password '+link
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




class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"


class OwnerSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(write_only=True)

    class Meta:
        model = Owner
        fields = ('id', 'vehicle_id', 'vehicle_number', 'name', 'date_of_birth', 'gender', 'address')
        read_only_fields = ('id', 'vehicle_id',)

    def create(self, validated_data):
        vehicle_number = validated_data.pop('vehicle_number')
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vehicle_number)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError(f"No vehicle found with number {vehicle_number}")
        try:
            owner = Owner.objects.get(vehicle_id=vehicle.id)
        except Owner.DoesNotExist:
            pass
        else:
            raise serializers.ValidationError(f"Vehicle already has an owner with ID - {owner.id}")
        validated_data['vehicle_id'] = vehicle.id
        return Owner.objects.create(**validated_data)


class PolicySerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(write_only=True)
    personal_accident = serializers.BooleanField(write_only=True)
    passenger_cover = serializers.BooleanField(write_only=True)
    breakdown_assistance = serializers.BooleanField(write_only=True)

    class Meta:
        model = Policy
        fields = ('vehicle_number', 'personal_accident', 'passenger_cover', 'breakdown_assistance', 'id', 
                  'policy_number', 'vehicle_id', 'description', 'base_premium', 'personal_accident_premium', 'passenger_cover_premium',
                  'breakdown_assistance_premium', 'total_premium', 'insured_declared_value', 'policy_status',
                  'payment_status', 'effective_from', 'expires_on')
        read_only_fields = ('id', 'policy_number', 'vehicle_id', 'description', 'base_premium', 'personal_accident_premium', 'passenger_cover_premium',
                  'breakdown_assistance_premium', 'total_premium', 'insured_declared_value')
    
    def create(self, validated_data):
        vehicle_number = validated_data.pop('vehicle_number')
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vehicle_number)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError(f"No vehicle found with number {vehicle_number}")
        validated_data['vehicle'] = vehicle
        try:
            owner = Owner.objects.get(vehicle_id=vehicle.id)
        except:
            raise serializers.ValidationError(f"We don't have the owner details for the vehicle number {vehicle_number}")
        try:
            policy = Policy.objects.get(vehicle_id=vehicle.id)
        except Policy.DoesNotExist:
            pass
        else:
            if policy.policy_status != "Rejected" or policy.policy_status != "Expired":
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
    



class ClaimSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(write_only=True)
    
    class Meta:
        model = Claim
        fields = ('id', 'policy_id', 'vehicle_id', 'vehicle_number', 'description_of_incident', 'reason_for_claim', 'date_of_claim', 'claim_status', 'claimant_bank_name', 'claimant_account_number')
        read_only_fields = ('id', 'policy_id', 'vehicle_id',)

    def create(self, validated_data):
        vehicle_number = validated_data.pop('vehicle_number')
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vehicle_number)
        except Vehicle.DoesNotExist:
            raise serializers.ValidationError(f"No vehicle found with number {vehicle_number}")
        validated_data['vehicle'] = vehicle
        try:
            owner = Owner.objects.get(vehicle_id=vehicle.id)
        except:
            raise serializers.ValidationError(f"We don't have the owner details for the vehicle number {vehicle_number}")
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