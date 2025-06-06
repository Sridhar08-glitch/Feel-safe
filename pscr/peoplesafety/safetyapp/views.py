from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import UserProfile
from django.http import HttpResponse
import re

from .models import CrimeReport
from .forms import CrimeReportForm

def register_view(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        dob = request.POST['dob']
        gender = request.POST['gender']
        username = request.POST['username']
        password = request.POST['password']

        # Validate email format (must end with @gmail.com)
        if not email.endswith("@gmail.com"):
            messages.error(request, "Email must end with @gmail.com")
            return redirect('register')

        # Validate password (at least 8 characters, 1 special character, 1 number)
        if not re.match(r'^(?=.*[!@#$%^&*(),.?":{}|<>])(?=.*\d)[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,}$', password):
            messages.error(request, "Password must be at least 8 characters long, contain a special character and a number.")
            return redirect('register')

        # Check if username, email, or phone number already exists
        if UserProfile.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number already registered.")
            return redirect('register')

        # Securely save user
        user = UserProfile(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            dob=dob,
            gender=gender
        )
        user.set_password(password)  # Hash password
        user.save()

        messages.success(request, "Registration successful! Please log in.")
        return redirect('home')

    return render(request, 'registerpage.html')


# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home page after successful login
        else:
            return render(request, 'loginpage.html', {'error': 'Invalid username or password'})

    return render(request, 'loginpage.html')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')


# Page Render Views
def loginpage(request):
    return render(request, 'loginpage.html')



def registerpage(request):
    return render(request, 'registerpage.html')

def forget(request):
    return render(request, 'forget_password.html')

def home(request):
    return render(request, 'home.html')

def pofficial(request):
    return render(request,'police_officials.html')

def vreports(request):
    reports = CrimeReport.objects.all()  # Get all crime reports
    return render(request, 'viewreports.html', {'reports': reports})

def dreport(request, report_id):
    report = get_object_or_404(CrimeReport, id=report_id)
    report.delete()  # Delete the report
    return redirect('viewreports') 
def nbpolice(request):
    return render(request,'nearbypolice.html')
def safeplace(request):
    return render(request,'safeplaces.html')
def track(request):
    return render(request,'track.html')
def delete_contact(request, contact_id):
    contact = get_object_or_404(EmergencyContact, id=contact_id)
    contact.delete()
    return redirect('emcontact') 
def emergency(request):
    emergency(request)
    return render('emcontact')
def viewreportcrime(request):
    return render(request, 'reportcrime.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import EmergencyContact

@login_required
def emcontact(request):
    contacts = EmergencyContact.objects.filter(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        relationship = request.POST.get('relationship')

        if name and phone and relationship:
            EmergencyContact.objects.create(
                user=request.user,
                name=name,
                phone=phone,
                relationship=relationship
            )
            return render(request, 'emcontact.html', {'contacts': contacts})

    return render(request, 'emcontact.html', {'contacts': contacts})
#forget_password_page
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import UserProfile

TWO_FACTOR_API_KEY = ""

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        
        exist = UserProfile.objects.filter(phone_number=phone).exists()
        if exist:
            try:
                # Send OTP via 2Factor API
                response = requests.get(f"https://2factor.in/API/V1/{TWO_FACTOR_API_KEY}/SMS/{phone}/AUTOGEN")
                data = response.json()

                if data["Status"] == "Success":
                    session_id = data["Details"]  # Get session ID from API
                    request.session["otp_session_id"] = session_id  # Store in Django session
                    request.session["phone"] = phone  # Store phone for later use
                    return JsonResponse({"success": True, "session_id": session_id})  
                else:
                    return JsonResponse({"error": "Failed to send OTP"})

            except Exception as e:
                return JsonResponse({"error": f"Error sending OTP: {str(e)}"})

        else:
            return JsonResponse({"error": "Number not registered"})

@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        session_id = request.session.get("otp_session_id")  # Retrieve from Django session
        phone = request.session.get("phone")  # Get stored phone number

        if not session_id:
            return JsonResponse({"error": "Session expired or invalid. Please request a new OTP."})

        try:
            print(f'Session ID: {session_id}, OTP: {otp}')
            response = requests.get(f"https://2factor.in/API/V1/{TWO_FACTOR_API_KEY}/SMS/VERIFY/{session_id}/{otp}")
            data = response.json()

            if data["Status"] == "Success":
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"error": f"Invalid OTP: {data}"})

        except Exception as e:
            return JsonResponse({"error": f"Error verifying OTP: {str(e)}"})

@csrf_exempt
def reset_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        phone = request.session.get("phone")  # Retrieve phone from session

        if not phone:
            return JsonResponse({"error": "Session expired. Please restart the process."})

        try:
            user_profile = UserProfile.objects.get(phone_number=phone)  # Use correct field name
            user_profile.set_password(new_password)  # Set new password securely
            user_profile.save()
            
            # Clear session data after password reset
            del request.session["phone"]
            del request.session["otp_session_id"]

            return JsonResponse({"success": True})
        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "User not found"})

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import CrimeReport
from django.contrib.auth.decorators import login_required

@login_required  # Ensure user is logged in
def report_crime(request):
    if request.method == "POST":
        try:
            # Fetching form data
            user = request.user
            date_of_crime = request.POST.get("date_of_crime")
            time_of_crime = request.POST.get("time_of_crime")
            type_of_crime = request.POST.get("type_of_crime")
            location_of_crime = request.POST.get("location_of_crime")
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")
            victim_gender = request.POST.get("victim_gender")
            number_of_victims = request.POST.get("number_of_victims")
            description_of_crime = request.POST.get("description_of_crime")
            description_of_suspect = request.POST.get("description_of_suspect", "")

            # Ensure no missing fields
            if not all([date_of_crime, time_of_crime, type_of_crime, location_of_crime, latitude, longitude]):
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Save to database
            CrimeReport.objects.create(
                user=user,
                date_of_crime=date_of_crime,
                time_of_crime=time_of_crime,
                type_of_crime=type_of_crime,
                location_of_crime=location_of_crime,
                latitude=latitude,
                longitude=longitude,
                victim_gender=victim_gender,
                number_of_victims=number_of_victims,
                description_of_crime=description_of_crime,
                description_of_suspect=description_of_suspect
            )

            return redirect("home")  # Redirect after submission

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "reportcrime.html")
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import CrimeReport

@login_required
def viewreports(request):
    reports = CrimeReport.objects.all()  # ✅ Fetch all crime reports (not just the logged-in user's)
    return render(request, 'viewsreports.html', {'reports': reports})



from .models import Room,Message
def RoomView(request, room_name, username):
    existing_room = Room.objects.get(room_name__icontains=room_name)
    get_messages = Message.objects.filter(room=existing_room)
    context = {
        "messages": get_messages,
        "user": request.user.username if request.user.is_authenticated else "Anonymous", 
        "room_name": existing_room.room_name,
    }

    return render(request, "chat.html", context)

@login_required
def add_profile(request):
      # No need for a DB query
    user=request.user
    if request.method=='POST':
        user.email=request.POST['email']
        user.phone_number=request.POST['phone_number']
        user.dob=request.POST['dob']
        user.gender=request.POST['gender']
        user.save()
        messages.success(request,'profile update success')
        return render(request,'profile.html',{"profile": user})

    return render(request, "profile.html", {"profile": user})


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import EmergencyContact
from .utils import send_sos_sms
import logging

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def trigger_sos(request):
    if request.method == 'POST':
        try:
            # Get latitude & longitude from request
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')

            if not lat or not lng:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing location data'
                }, status=400)

            # Fetch user's emergency contacts
            contacts = EmergencyContact.objects.filter(user=request.user)
            if not contacts.exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'No emergency contacts found'
                }, status=400)

            # Create Google Maps link
            maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

            # Prepare SOS message
            user = request.user
            message = (
                f"EMERGENCY ALERT! {user.first_name} {user.last_name} "
                f"needs help! Location: {maps_link}"
            )

            # Send SMS to each emergency contact
            failed_contacts = []
            a=None
            for contact in contacts:
                try:
                    a=send_sos_sms(contact.phone, lat,lng,user)
                except Exception as sms_error:
                    logger.error(f"Failed to send SMS to {contact.phone}: {sms_error}")
                    failed_contacts.append(contact.phone)

            # Return response with failed numbers if any
            if failed_contacts:
                return JsonResponse({
                    'status': 'partial_success',
                    'message': f'SOS sent, but failed for: {", ".join(failed_contacts)}'
                }, status=207)

            return JsonResponse({
                'status': 'success',
                'message': f'SOS alert sent successfully!{a}'
            })
        
        except Exception as e:
            logger.error(f"SOS Trigger Error: {e}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': 'An unexpected error occurred.'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)



from django.shortcuts import render
from .models import Notification

def notifications_view(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return render(request, 'notify.html', {'notifications': notifications})
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Notification

def get_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    return JsonResponse({
        'title': notification.title,
        'message': notification.message,
        'crime_time': str(notification.crime_time) if notification.crime_time else None,
        'location_of_crime': notification.location_of_crime
    })

from django.shortcuts import redirect
from django.urls import path

def redirect_to_admin(request):
    return redirect('/admin/')


from django.http import JsonResponse
from .models import CrimeReport

def get_approved_crimes(request):
    crimes = CrimeReport.objects.filter(is_approved=True).values('type_of_crime', 'latitude', 'longitude')
    return JsonResponse(list(crimes), safe=False)


def show_danger(request):
    return render(request,'danger.html')


from django.http import JsonResponse
from math import radians, sin, cos, sqrt, atan2
from .models import PoliceStation

def get_nearby_police_stations(request):
    try:
        user_lat = float(request.GET.get('lat'))
        user_lon = float(request.GET.get('lon'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid coordinates'}, status=400)

    nearby_stations = []

    for station in PoliceStation.objects.all():
        station_lat = float(station.latitude)
        station_lon = float(station.longitude)

        # Haversine formula for distance calculation
        R = 6371  # Radius of Earth in km
        dlat = radians(station_lat - user_lat)
        dlon = radians(station_lon - user_lon)
        a = sin(dlat / 2) ** 2 + cos(radians(user_lat)) * cos(radians(station_lat)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        if distance <= 5:  # Filter within 5km
            nearby_stations.append({
                'name': station.name,
                'latitude': station_lat,
                'longitude': station_lon,
                'distance': round(distance, 2)
            })

    return JsonResponse({'nearby_stations': nearby_stations})

from django.shortcuts import render

def map_view(request):
    return render(request, 'nearbypolice.html')



from .models import Safeplaces

Safeplaces.objects.create(latitude=13.083211494138329,longitude= 80.17959946434873, name='Srinivasa eye hospital')

from django.http import JsonResponse
from math import radians, sin, cos, sqrt, atan2
from .models import Safeplaces

def get_nearby_safe_places(request):
    try:
        user_lat = float(request.GET.get('lat'))
        user_lon = float(request.GET.get('lon'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid coordinates'}, status=400)

    nearby_stations = []

    for station in Safeplaces.objects.all():
        station_lat = float(station.latitude)
        station_lon = float(station.longitude)

        # Haversine formula for distance calculation
        R = 6371  # Radius of Earth in km
        dlat = radians(station_lat - user_lat)
        dlon = radians(station_lon - user_lon)
        a = sin(dlat / 2) ** 2 + cos(radians(user_lat)) * cos(radians(station_lat)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        if distance <= 5:  # Filter within 5km
            nearby_stations.append({
                'name': station.name,
                'latitude': station_lat,
                'longitude': station_lon,
                'distance': round(distance, 2)
            })

    return JsonResponse({'nearby_stations': nearby_stations})

from django.shortcuts import render

def safemap_view(request):
    return render(request, 'safeplaces.html')




from .models import PoliceStation

PoliceStation.objects.create(name="Teynampet Police Station", latitude=13.0489, longitude=80.2496)
PoliceStation.objects.create(name="Guindy Police Station", latitude=13.0072, longitude=80.2201)

PoliceStation.objects.create(latitude= 13.067439, longitude=80.237617, name="Egmore Police Station")
PoliceStation.objects.create(latitude= 13.0625, longitude=80.2476, name="Triplicane Police Station")
PoliceStation.objects.create(latitude= 13.0823, longitude=80.2756, name="Teynampet Police Station")
PoliceStation.objects.create(latitude= 13.0878, longitude=80.2785, name= "Kilpauk Police Station")

PoliceStation.objects.create(latitude=13.0339, longitude=80.2596, name= "Guindy Police Station" )
PoliceStation.objects.create(latitude=13.022408223814168, longitude= 80.22614338800288, name="Saidapet J-1 Police Station")
PoliceStation.objects.create(latitude=13.092840786203318, longitude=80.2751248091113, name="Elephant Gate C-2 Police Station")

PoliceStation.objects.create(latitude=13.09962357553559, longitude=80.28180464634256,name="seven wells C-3 police station ")
PoliceStation.objects.create(latitude=13.082239051371937, longitude=80.27545513599081,name="Gov-hospital C-4 police staion")
PoliceStation.objects.create(latitude=13.08711767553012, longitude=80.2850939460496,name="esplande B-2 police station")
PoliceStation.objects.create(latitude=13.09643133312534, longitude=80.28647213794765,name="harbour B-5 police station")
PoliceStation.objects.create(latitude=13.090007387894994, longitude=80.29046749562,name="north beach B-1 police station")

PoliceStation.objects.create(latitude=13.079086191382014, longitude=80.28506256307605,name="fort B-3 police station")
PoliceStation.objects.create(latitude=13.105353114502865, longitude=80.28410101579367,name="Muthliapet N-3 police station")
PoliceStation.objects.create(latitude=13.095609883965471, longitude=80.28066021096511,name="kothavalachavadi C-5 police station")
PoliceStation.objects.create(latitude=13.108858070875403, longitude= 80.28065891096533,name="washermenpet H-1 police station")
PoliceStation.objects.create(latitude=13.123429070834662, longitude=80.2873033379481,name="tondaiyarpet H-3 police station")
PoliceStation.objects.create(latitude=13.117801215864581, longitude=80.27993465143933,name="korukpet H-4 police station")
PoliceStation.objects.create(latitude=13.124589470241524, longitude=80.27724711281941,name="Rk nagar H-6 police station")
PoliceStation.objects.create(latitude=13.105365229466834, longitude=80.28439428212904,name="stanley hospital H-2 police station")
PoliceStation.objects.create(latitude=13.15429941228623, longitude=80.30073686493121,name="thiruvottiyur H-8 police station")
PoliceStation.objects.create(latitude=13.12673692923053, longitude=80.28715149174883,name="peripal hospital H-7 police station")
PoliceStation.objects.create(latitude=13.139697117441862,longitude=80.2891003398021,name="new washermenpet H-5 police station")
PoliceStation.objects.create(latitude=13.112086266106479, longitude=80.29381182260293,name="Royapuram N-1 police station")
PoliceStation.objects.create(latitude=13.120215757808547, longitude=80.29485533794802,name="kasimedu N-2 police station")
PoliceStation.objects.create(latitude=13.129227113048204, longitude=80.2959840379482,name="fishing harbour N-4 police station")
PoliceStation.objects.create(latitude=13.131641294432443, longitude=80.23780889376697,name="madhavaram M-1 police station")
PoliceStation.objects.create(latitude=13.146297231152586, longitude=80.23959886678475,name="milk colony M-2 police station")
PoliceStation.objects.create(latitude=13.16031788144109, longitude=80.20288022631127,name="Puzhal M-3 police station")
PoliceStation.objects.create(latitude=13.191475153019946, longitude=80.1855828821306,name="redhills M-4 police station")
PoliceStation.objects.create(latitude=13.20918990162058,longitude=80.31640771096716,name="ennore police M-5 police station")
PoliceStation.objects.create(latitude=13.163764403267876, longitude=80.26361349562136,name="Manali M-6 police station")
PoliceStation.objects.create(latitude=13.206795402684829, longitude=80.2760897532946,name="manali new tow M-7 police station")
PoliceStation.objects.create(latitude=13.175258528593098, longitude=80.28553103069001,name="sathangadu M-8 police station")
PoliceStation.objects.create(latitude=13.100293178134969, longitude=80.26010235329267,name="pulianthope P-1 police station")
PoliceStation.objects.create(latitude=13.100548579415593, longitude=80.25151669562018,name="otteri P-2 police station")
PoliceStation.objects.create(latitude=13.095419134280846, longitude=80.26623302445638,name="basin bridge P-4 police station")
PoliceStation.objects.create(latitude=13.123279214140638, longitude=80.26140292445686,name="mkb nagar P-5 police station")
PoliceStation.objects.create(latitude=13.131789007980442, longitude=80.25698533794824,name="kodungaiyur P-6 police station")
PoliceStation.objects.create(latitude=13.111789508672459, longitude=80.26536134958539,name="Vysarpadi P-3 police station")
PoliceStation.objects.create(latitude=13.110700880623348, longitude=80.24044671096536,name="sembiam K-1 police station")
PoliceStation.objects.create(latitude=13.111537673488073, longitude=80.22646656863787,name="peralavur K-5 police station")
PoliceStation.objects.create(latitude=13.122644763273897, longitude=80.23622431096557,name="Thiru Vika Nagar K-9 police station")
PoliceStation.objects.create(latitude=13.081371993994077, longitude=80.2180113821286,name="amangikarai K-3 police station")
PoliceStation.objects.create(latitude=13.093125237506065, longitude=80.21794857346326,name="anna nagar K-4 police station")
PoliceStation.objects.create(latitude=13.069066268504104, longitude=80.21371916492964,name="arumbakkam K-8 police station")
PoliceStation.objects.create(latitude=13.076663294694624, longitude=80.17531031096473,name="JJ nagar V-3 police station")
PoliceStation.objects.create(latitude=13.093395334456053, longitude=80.19771153995711,name="thirumangalam V-5 police station")
PoliceStation.objects.create(latitude=13.0776578805423, longitude=80.17571684201425,name="nolambur V-7 police station")
PoliceStation.objects.create(latitude=13.069857805465341, longitude=80.2002294360934,name="koyambedu K-10 police station")
PoliceStation.objects.create(latitude=13.067250140308547, longitude=80.17661175143837,name="madhuravayal T-4 police station")
PoliceStation.objects.create(latitude=13.103776876671903, longitude=80.20629926678406,name="villivakam V-1 police station")
PoliceStation.objects.create(latitude=13.122326968769281, longitude=80.20529418027562,name="rajamangalam V-4 police station")
PoliceStation.objects.create(latitude=13.110403120234142, longitude=80.21366338027536,name="kolathur V-6 police station")
PoliceStation.objects.create(latitude=13.109794323766305, longitude=80.15116601019062,name="ambatur T-1 police station")
PoliceStation.objects.create(latitude=13.095625434489879, longitude=80.1637762226026,name="ambattur estate T-2 police station")
PoliceStation.objects.create(latitude=13.110847061097783, longitude=80.18667042839087,name="korattur T-3 police station")
PoliceStation.objects.create(latitude=13.117414422802295,longitude=80.10276928212926,name="avadi T-6 police station")
PoliceStation.objects.create(latitude=13.158594079976531, longitude=80.10357721695364,name="Tank factory T-7 police station")
PoliceStation.objects.create(latitude=13.124704153224963, longitude=80.11673169376687,name="Thirumullivayal T-10 police station")
PoliceStation.objects.create(latitude=13.131590294486731,longitude=80.03632179562076,name="Thirunivarur T-11 police station")
PoliceStation.objects.create(latitude=13.147062010161726, longitude=80.0416952001538,name="Muthapudupet T-8 police station")
PoliceStation.objects.create(latitude=13.122328160893034, longitude=80.0626432802756,name="pattabiram T-9 police station")
PoliceStation.objects.create(latitude=13.050339049407379, longitude=80.0910776993268,name="poonamallle T-12 police station")
PoliceStation.objects.create(latitude=13.04744545732505, longitude=80.07795092306752,name="nazarpettai T-16 police station")
PoliceStation.objects.create(latitude=13.074164201813781, longitude=80.12525360725725,name="thiruverkadu T-5 police station")
PoliceStation.objects.create(latitude=13.041543821059985, longitude=80.13317513562032,name="srmc T-15 police station")
PoliceStation.objects.create(latitude=13.039429227486423, longitude=80.11373871458446,name="managadu T-14 police station")
PoliceStation.objects.create(latitude=12.997534088842079, longitude=80.09188929561832,name="kunrathur T-5 police station")
            
PoliceStation.objects.create(latitude=13.050898556090678,longitude=80.21905131078954,name="R2 Kodambakkam police station")
PoliceStation.objects.create(latitude=13.039448531217065,longitude=80.24598010893841,name="E3 Teynampet Police Station")
PoliceStation.objects.create(latitude=13.044110915255724,longitude=80.21733049544609,name="R3 Ashok Nagar Police Station")
PoliceStation.objects.create(latitude=13.041981450174347,longitude=80.20525163824958,name="KK Nagar police station")
PoliceStation.objects.create(latitude=13.031326957856642,longitude=80.20172134058447,name="R10 MGR Nagar Police Station")
PoliceStation.objects.create(latitude=13.043537127758155,longitude=80.17602593592345,name="R9 Valasaravakkam Police Station")
PoliceStation.objects.create(latitude=13.032077732426055,longitude=80.17867323777418,name="R11 Royala Nagar Police Station")
PoliceStation.objects.create(latitude=13.049816329499345,longitude=80.21163122243108,name="R-8 Vadapalani Police Station")
PoliceStation.objects.create(latitude=13.049872867116257,longitude=80.19932688380466,name="R-5 Virugambakkam Police Station")
PoliceStation.objects.create(latitude=5146168186264,longitude=80.22945353777416,name="R1 Mambalam Police Station")
PoliceStation.objects.create(latitude=12.947827352391151,longitude=80.25400832428018,name="J 8 Neelangarai Police Station")
PoliceStation.objects.create(latitude=12.8224220197158,longitude=80.24019486384198,name="J-12 Kaanathur, Police Station")
PoliceStation.objects.create(latitude=12.947530360144574, longitude= 80.24040762428015, name= "J-9 Thuraipakkam Police Station")
PoliceStation.objects.create(latitude=12.900684709643992, longitude= 80.22816073962274, name= "J-10 Semmenchery Police Station")
PoliceStation.objects.create(latitude=12.984776558921354, longitude= 80.26097406660912, name= "J6 - Thiruvanmiyur Police Station")
PoliceStation.objects.create(latitude=12.994872436223542, longitude= 80.24300212428099, name= "J13 Tharamani Police Station")
PoliceStation.objects.create(latitude=13.009585256449249, longitude= 80.21072386846052, name= "Guindy Police Station")
PoliceStation.objects.create(latitude=12.981085943198424,longitude= 80.22093469729583, name="J7 - Velachery Police Station")
PoliceStation.objects.create(latitude=13.022604407505662, longitude= 80.22624627873866, name="J1 Saidapet Police Station")
PoliceStation.objects.create(latitude=13.028424982539617, longitude= 80.21654956660994, name= "R6 Kumaran Nagar Police Station")
PoliceStation.objects.create(latitude=12.997991304382099, longitude= 80.25563400893766, name= "J2 Adyar Police Station")
PoliceStation.objects.create(latitude=13.000766594729802, longitude= 80.26592192428112, name= "J5 Sastri Nagar Police Station")
PoliceStation.objects.create(latitude=12.95621390140227, longitude= 80.18529823777278, name="Madipakkam S7 Police Station")
PoliceStation.objects.create(latitude=12.990659926668924, longitude= 80.20883388010168, name= "S8 Adambakkam Police Station")
PoliceStation.objects.create(latitude=12.91698866083719, longitude= 80.19502498195129, name="T14 Pallikaranai Traffic Police Station")
PoliceStation.objects.create(latitude=12.923147572431281, longitude= 80.13543131263822, name= "S15 Selaiyur Police Station")
PoliceStation.objects.create(latitude=12.93981896403287, longitude=80.13809489544417, name= "S12 Chitlapakkam Police Station")
PoliceStation.objects.create(latitude=12.90572740158089, longitude=80.09755257824922, name="S14 Peerkankaranai Police Station")
PoliceStation.objects.create(latitude=12.925679171156712, longitude=80.11453125126468, name= "S11 Tambaram Police Station")
PoliceStation.objects.create(latitude=12.955384567658632, longitude=80.13299930893692, name= "S13 Chrompet Police Station")
PoliceStation.objects.create(latitude=12.97447275460467, longitude= 80.14762155969616, name="T3 Pallavaram Police Station")
PoliceStation.objects.create(latitude=12.968371060010583, longitude= 80.12497161078805, name= "S6 Sankar Nagar Police Station")
PoliceStation.objects.create(latitude=12.978861337104988, longitude= 80.15975830708892, name= "S2 Airport Police Station")
PoliceStation.objects.create(latitude=12.986586366983524, longitude= 80.17495879729597, name= "S3 Meenambakkam Police Station")
PoliceStation.objects.create(latitude=12.999273280103392, longitude= 80.19997902243017, name= "S1 St. Thomas Mount Police Station")
PoliceStation.objects.create(latitude=13.016287697612537, longitude= 80.189370508938, name= "S4 Nungaambakkam Police Station")
PoliceStation.objects.create(latitude=12.98443492344018, longitude=80.18578281078837, name="S9 Palavanthangal Police Station")
PoliceStation.objects.create(latitude=13.050898556090678, longitude=80.21905131078954, name= "R2 Kodambakkam Police Station")
           
PoliceStation.objects.create(latitude=13.082680, longitude=80.270718, name= "K6 TP Chathiram Police Station" )
PoliceStation.objects.create(latitude=13.080280, longitude=80.249360, name= "G3 Kilpauk Police Station" )
PoliceStation.objects.create(latitude=13.067560, longitude=80.252450, name= "G7 Chetpet Police Station" )
PoliceStation.objects.create(latitude=13.078520, longitude=80.253790, name= "G6 KMC Police Station" )
PoliceStation.objects.create(latitude=13.085300, longitude=80.265000, name= "G1 Vepery Police Station" )
PoliceStation.objects.create(latitude=13.087600, longitude=80.278500, name= "G2 Periamet Police Station" )
PoliceStation.objects.create(latitude=13.104500, longitude=80.233700, name= "K2 Ayanavaram Police Station" )
PoliceStation.objects.create(latitude=13.098400, longitude=80.232100, name= "K7 ICF Police Station" )
PoliceStation.objects.create(latitude=13.078900, longitude=80.243500, name= "G4 Mental Hospital Police Station" )
PoliceStation.objects.create(latitude=13.081200, longitude=80.249900, name= "G5 Secretary Colony Police Station" )
PoliceStation.objects.create(latitude=13.0606, longitude=80.2780, name= "D1 Triplicane Police Station" )
PoliceStation.objects.create(latitude=13.0827, longitude=80.2707, name= "D8 K.G. Hospital Police Station" )
PoliceStation.objects.create(latitude=13.0600, longitude=80.2664, name= "D2 Anna Salai Police Station" )
PoliceStation.objects.create(latitude=13.0726, longitude=80.2698, name= "D4 Zam Bazaar Police Station" )
PoliceStation.objects.create(latitude=13.0500, longitude=80.2820, name= "D6 Anna Square Police Station" )
PoliceStation.objects.create(latitude=13.0680, longitude=80.2730, name= "F1 Chintadripet Police Station" )
PoliceStation.objects.create(latitude=13.0795, longitude=80.2606, name= "F2 Egmore Police Station" )
PoliceStation.objects.create(latitude=13.0820, longitude=80.2550, name= "F7 Maternity Hospital Police Station" )
PoliceStation.objects.create(latitude=13.0604, longitude=80.2430, name="F2 Nungambakkam Police Station" )
PoliceStation.objects.create(latitude=13.0700, longitude= 80.2300, name= "R5 Choolaimedu Police Station")
PoliceStation.objects.create(latitude=13.0330, longitude= 80.2680, name= "E1 Mylapore Police Station")
PoliceStation.objects.create(latitude=13.0160, longitude= 80.2790, name= "E5 Foreshore Estate Police Station")
PoliceStation.objects.create(latitude=13.0500, longitude= 80.2830, name= "D5 Marina Police Station" )
PoliceStation.objects.create(latitude=13.0400, longitude= 80.2600, name= "E4 Abiramapuram Police Station" )
PoliceStation.objects.create(latitude=13.0100, longitude= 80.2400, name= "J2 Kotturpuram Police Station" )
PoliceStation.objects.create(latitude=13.0500, longitude= 80.2700, name= "E2 Royapettah Police Station")
PoliceStation.objects.create(latitude=13.0400, longitude= 80.2800, name= "D3 Ice House Police Station" )
PoliceStation.objects.create(latitude=13.0500, longitude= 80.2600, name= "E6 GOVT Royapettah Police Station")


from .models import Safeplaces


Safeplaces.objects.create(latitude=13.031842026362941,longitude= 80.20167874988611, name='R10 MGR Nagar Police station')
Safeplaces.objects.create(latitude=13.035705624949141, longitude=80.21101697825152,name='ashok nagar metro station')
Safeplaces.objects.create(latitude=13.036020991559655, longitude=80.20878893591606,name='government college of physiotheraphy')
Safeplaces.objects.create(latitude=13.034923416507455, longitude=80.2072989072655, name='esic hospital')
Safeplaces.objects.create(latitude=13.049217002913718,longitude= 80.20381145204931, name='kauvery hospital')
Safeplaces.objects.create(latitude=13.05306322783237,longitude= 80.21162204454619, name='sims hospital')
Safeplaces.objects.create(latitude=13.05114560767856,longitude= 80.2094543954462, name='forum mall')
Safeplaces.objects.create(latitude=13.04173538301235,longitude= 80.19328054562467, name='fitness factory kk nagar')
Safeplaces.objects.create(latitude=13.041814204033244, longitude=80.20543402428186,name='kk nagar police station')
Safeplaces.objects.create(latitude=13.047252450978558, longitude=80.1901524315097,name='D mart')
Safeplaces.objects.create(latitude=13.051376717202523,longitude= 80.18612043704606, name='Sadiq Basha Nagar Mosque')
Safeplaces.objects.create(latitude=13.04610506003289,longitude= 80.18882803445973, name='The Dolphin Park Hotel')