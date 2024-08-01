from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Vehicle, Owner, Policy, Claim

from django.core import signing #This module is used to Encrypt and Decrypt Data in Django
from django.urls import reverse

from datetime import date, timedelta
# Create your views here.

def home(request):
    return render(request, 'MotorInsuranceCompany/home.html')


def signup(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        if pass1 == pass2:
            if User.objects.filter(email=email).exists():
                error = "Email already Registered."
                return render(request, "MotorInsuranceCompany/signup.html", {'error': error})
            newuser = User.objects.create_user(name=name, 
                                            email=email, 
                                            tc=True, 
                                            password=pass1)
            newuser.save()
            return redirect('signin')
        else:
            error = "The Password Fields do not match... Please Try Again."
            return render(request, "MotorInsuranceCompany/signup.html", {'error': error})
        
    return render(request, "MotorInsuranceCompany/signup.html")


def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        pass1 = request.POST['pass1']
        user = authenticate(email=email, password=pass1)
        if user is not None:
            login(request, user)
            return render(request, "MotorInsuranceCompany/menu.html")
        else:
            error = "Invalid Email or Password.."
            return render(request, "MotorInsuranceCompany/signin.html", {'error': error})
    return render(request, "MotorInsuranceCompany/signin.html")


def signout(request):
    logout(request)
    return redirect('home')


def about(request):
    return render(request, 'MotorInsuranceCompany/about.html')


def menu(request):
    return render(request, "MotorInsuranceCompany/menu.html")


def vehicle_details(request):
    if request.method == 'POST':
        vehicleType = request.POST['vehicleType']
        vehicleNumber = request.POST['vehicleNumber']
        make = request.POST['make']
        model = request.POST['model']
        fuelType = request.POST['fuelType']
        registrationDate = request.POST['registrationDate']
        num_seats = request.POST['num_seats']
        price = request.POST['purchase_price']
        new_vehicle = Vehicle.objects.create(user = request.user,
                                             vehicle_type=vehicleType,
                                             vehicle_number=vehicleNumber,
                                             make=make,
                                             model=model,
                                             fuel_type=fuelType,
                                             registration_date=registrationDate,
                                             seats=num_seats,
                                             purchase_price=price)
        new_vehicle.save()
        vid = new_vehicle.id
        #Encrypting the vehicle id before passing it to the url
        signed_vid = signing.dumps(vid)
        return redirect(reverse('owner_details', kwargs={'signed_vid': signed_vid}))
    return render(request, 'MotorInsuranceCompany/vehicle_details.html')


def owner_details(request, signed_vid):
    #Decrypting the vehicle_id received from vehicle_details()
    vid = signing.loads(signed_vid)
    vehicle = Vehicle.objects.get(id=vid)
    if request.method == 'POST':
        name = request.POST['name']
        dob = request.POST['dob']
        gender = request.POST['gender']
        address = request.POST['address']
        owner = Owner.objects.create(vehicle=vehicle,
                                     name=name,
                                     date_of_birth=dob,
                                     gender=gender,
                                     address=address)
        owner.save()
        return  redirect(reverse('add_ons', kwargs={'signed_vid': signed_vid}))
    return render(request, "MotorInsuranceCompany/owner_details.html", {'signed_vid': signed_vid})

def add_ons(request, signed_vid):
    vid = signing.loads(signed_vid)
    vehicle = Vehicle.objects.get(id=vid)
    try:
        expired_polixy = Policy.objects.get(vehicle_id = vid)
        expired_polixy.delete()
    except:
        pass
    if request.method == 'POST':
        pn = "MSPOL"+str(vid)
        desc = "This Insurance Policy will provide financial protection against damage or loss to your vehicle due to accidents, theft, or natural disasters, as well as covers the liability claims arising from third-party injuries or property damage."
        today_date = date.today()
        age_of_vehicle = today_date.year - vehicle.registration_date.year
        basePremium = calculate_base_premium(vehicle.vehicle_type, age_of_vehicle)
        personalAccident, passengerCover, breakdownAssistance = 0.00, 0.00, 0.00
        if 'personal_accident' in request.POST:
            personalAccident = request.POST['personal_accident']
            personalAccident = int(personalAccident)*12
        if 'passenger_cover' in request.POST:
            passengerCover = request.POST['passenger_cover']
            passengerCover = int(passengerCover)*12
        if 'breakdown_assistance' in request.POST:
            breakdownAssistance = request.POST['breakdown_assistance']
            breakdownAssistance = int(breakdownAssistance)*12
        totalPremium = basePremium + personalAccident + passengerCover + breakdownAssistance
        idv = calculate_idv(age_of_vehicle, vehicle.purchase_price)
        # Creating the new policy
        new_policy = Policy.objects.create(policy_number=pn,
                                           vehicle=vehicle,
                                           description=desc,
                                           base_premium=basePremium,
                                           personal_accident_premium=personalAccident,
                                           passenger_cover_premium=passengerCover,
                                           breakdown_assistance_premium=breakdownAssistance,
                                           total_premium=totalPremium,
                                           insured_declared_value=idv)
        new_policy.save()
        return redirect(reverse('proposal_form_submitted', kwargs={'signed_vid': signed_vid}))
    return render(request, "MotorInsuranceCompany/add_ons.html", {'signed_vid': signed_vid})

def calculate_base_premium(vtype, vage):
    base = 0
    # Considering Vehicle Type
    if vtype == 'Two Wheeler':
        base = 1000.00
    elif vtype == 'Four Wheeler':
        base = 2000.00
    elif vtype == 'Commercial Vehicle':
        base = 4000.00
    # Considering Vehicle Age
    if vage <=2:
        base *= 0.90
    elif vage <= 4:
        base *= 1.00
    elif vage <=6:
        base *= 1.10
    else:
        base *= 1.20
    return base

def calculate_idv(vage, vprice):
    cover = float(vprice)
    if vage <=1:
        cover *= 0.85
    elif vage <=3:
        cover *= 0.70
    elif vage <=5:
        cover *= 0.55
    else:
        cover *= 0.40
    return cover


def proposal_form_submitted(request, signed_vid):
    return render(request, "MotorInsuranceCompany/proposal_form_submitted.html", {'signed_vid': signed_vid})


def details_to_track_policy(request):
    if request.method == 'POST':
        vnumber = request.POST['vnumber']
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vnumber)
        except:
            error = "No such vehicle found... Try Again"
            return render(request, "MotorInsuranceCompany/details_to_track_policy.html", {'error': error})
        vid = vehicle.id
        signed_vid = signing.dumps(vid)
        return redirect(reverse('track_policy', kwargs={'signed_vid': signed_vid}))
    return render(request, "MotorInsuranceCompany/details_to_track_policy.html")


def track_policy(request, signed_vid):
    vid = signing.loads(signed_vid)
    vehicle = Vehicle.objects.get(id=vid)
    policy = Policy.objects.get(vehicle_id=vid)
    owner = Owner.objects.get(vehicle_id=vid)
    pid = policy.id
    signed_pid = signing.dumps(pid)
    context = {
        'vehicle': vehicle,
        'policy': policy,
        'owner': owner,
        'signed_pid': signed_pid,
        'signed_vid': signed_vid,
    }
    return render(request, "MotorInsuranceCompany/track_policy.html", context)


def details_to_make_payment(request):
    if request.method == 'POST':
        vnumber = request.POST['vnumber']
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vnumber)
        except:
            error = "No such vehicle found... Try Again"
            return render(request, "MotorInsuranceCompany/details_to_make_payment.html", {'error': error})
        policy = Policy.objects.get(vehicle_id=vehicle.pk)
        if policy.policy_status == 'Active':
            error = "You already have an 'Active' Policy."
        elif policy.policy_status == 'Pending For Approval':
            error = "You can't make the Payment unless your Proposal is Approved."
        elif policy.policy_status == 'Rejected':
            error = 'Your Proposal has been Rejected.'
        elif policy.policy_status == 'Expired':
            error = 'Please renew yor policy, it has expired..'
        elif policy.policy_status == 'Pay to Activate Your Policy':
            pid = policy.id
            signed_pid = signing.dumps(pid)
            return redirect(reverse('premium_breakup', kwargs={'signed_pid': signed_pid}))
        return render(request, "MotorInsuranceCompany/details_to_make_payment.html", {'error': error})
    return render(request, "MotorInsuranceCompany/details_to_make_payment.html")


def premium_breakup(request, signed_pid):
    pid = signing.loads(signed_pid)
    policy = Policy.objects.get(id=pid)
    context = {
        'policy': policy,
        'signed_pid': signed_pid,
    }
    return render(request, "MotorInsuranceCompany/premium_breakup.html", context)

def payment_done(request, signed_pid):
    pid = signing.loads(signed_pid)
    policy = Policy.objects.get(id=pid)
    policy.payment_status = True
    policy.policy_status = 'Active'
    policy.effective_from = date.today()
    policy.expires_on = date.today() + timedelta(days=365)
    policy.save()
    return render(request, "MotorInsuranceCompany/payment_done.html", {'policy': policy})


def details_to_renew_policy(request):
    if request.method == 'POST':
        vnumber = request.POST['vnumber']
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vnumber)
        except:
            error = "No such vehicle found, try Creating a Proposal"
            return render(request, "MotorInsuranceCompany/details_to_renew_policy.html", {'error': error})
        policy = Policy.objects.get(vehicle_id=vehicle.pk)
        if vehicle.user_id != request.user.id:
            error = "This vehicle is not registered from your id.."
        elif policy.policy_status == 'Active':
            error = "You already have an 'Active' Policy."
        elif policy.policy_status == 'Pay to Activate Your Policy':
            error = "You have already applied for the policy.\n'Pay to Activate Your Policy'"
        elif policy.policy_status == 'Pending For Approval':
            error = "You have already applied for the policy.'Pending For Approval'\n"
        else :
            policy.delete()
            vid = vehicle.id
            signed_vid = signing.dumps(vid)
            return  redirect(reverse('add_ons', kwargs={'signed_vid': signed_vid}))
        return render(request, "MotorInsuranceCompany/details_to_renew_policy.html", {'error': error})
    return render(request, "MotorInsuranceCompany/details_to_renew_policy.html")


def file_for_claim(request):
    if request.method == 'POST':
        vehicleNumber = request.POST['vehicleNumber']
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vehicleNumber)
        except:
            error = "No such vehicle found..."
            return render(request, "MotorInsuranceCompany/file_for_claim.html", {'error': error})
        policy = Policy.objects.get(vehicle_id=vehicle.pk)
        if policy.policy_status != 'Active':
            error = "You do not have an Active Insurance Policy for this vehicle"
            return render(request, "MotorInsuranceCompany/file_for_claim.html", {'error': error})
        reasonForClaim = request.POST['reasonForClaim']
        descriptionOfIncident = request.POST['descriptionOfIncident']
        claimantBankName = request.POST['claimantBankName']
        claimantAccountNumber = request.POST['claimantAccountNumber']
        new_claim = Claim.objects.create(vehicle=vehicle,
                                         policy=policy,
                                         date_of_claim=date.today(),
                                         description_of_incident=descriptionOfIncident,
                                         reason_for_claim=reasonForClaim,
                                         claimant_bank_name=claimantBankName,
                                         claimant_account_number=claimantAccountNumber)
        new_claim.save()
        vid = vehicle.id
        signed_vid = signing.dumps(vid)
        return redirect(reverse('claim_submitted', kwargs={'signed_vid': signed_vid}))
    return render(request, 'MotorInsuranceCompany/file_for_claim.html')


def claim_submitted(request, signed_vid):
    return render(request, "MotorInsuranceCompany/claim_submitted.html", {'signed_vid': signed_vid})


def track_claim(request, signed_vid):
    vid = signing.loads(signed_vid)
    vehicle = Vehicle.objects.get(id=vid)
    policy = Policy.objects.get(vehicle_id=vid)
    claim = Claim.objects.get(vehicle_id=vid)
    context = {
        'vehicle': vehicle,
        'policy': policy,
        'claim': claim,
    }
    return render(request, "MotorInsuranceCompany/track_claim.html", context)


def details_to_track_claim(request):
    if request.method == 'POST':
        vnumber = request.POST['vnumber']
        try:
            vehicle = Vehicle.objects.get(vehicle_number=vnumber)
        except:
            error = "No such vehicle found... Try Again"
            return render(request, "MotorInsuranceCompany/details_to_track_claim.html", {'error': error})
        try:
            claim = Claim.objects.get(vehicle_id=vehicle.pk)
        except:
            error = "You haven't filed for a claim.."
            return render(request, "MotorInsuranceCompany/details_to_track_claim.html", {'error': error})
        vid = vehicle.id
        signed_vid = signing.dumps(vid)
        return redirect(reverse('track_claim', kwargs={'signed_vid': signed_vid}))
    return render(request, "MotorInsuranceCompany/details_to_track_claim.html")