from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class UserProfile(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    dob = models.DateField(null=True,blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    )


    def __str__(self):

        return f"{self.first_name} {self.last_name}".strip() if self.first_name else self.username
    


from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class CrimeReport(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)  # Linking report to a user
    date_of_crime = models.DateField()
    time_of_crime = models.TimeField()
    type_of_crime = models.CharField(
        max_length=50,
        choices=[
            ('theft', 'Theft'),
            ('assault', 'Assault'),
            ('robbery', 'Robbery'),
            ('other', 'Other')
        ]
    )
    location_of_crime = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    victim_gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female')]
    )
    number_of_victims = models.PositiveIntegerField()
    description_of_crime = models.TextField()
    description_of_suspect = models.TextField(blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)  # Timestamp when report was created
    is_approved=models.BooleanField(default=False)
    def _str_(self):
        return f"{self.type_of_crime} reported on {self.date_of_crime} at {self.location_of_crime}"
 # Ensure correct user model
from django.db import models
from django.conf import settings



class EmergencyContact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    relationship = models.CharField(max_length=50)


    def __str__(self):
        return f"{self.name} ({self.relationship}) - {self.phone}"



class Room(models.Model):
    room_name = models.CharField(max_length=50)

    def str(self):
        return self.room_name


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=50)
    message = models.TextField()
    timestamp = models.DateTimeField(default=now) 
   
    def str(self):
        return f"{str(self.room)} - {self.sender}"
    
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('general', 'General'),
        ('crime_alert', 'Crime Alert'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    crime_type = models.CharField(max_length=50, blank=True, null=True)  # Only for crime alerts
    crime_time = models.DateTimeField(blank=True, null=True)  # Only for crime alerts
    location_of_crime = models.CharField(max_length=255, blank=True, null=True)  # Only for crime alerts
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.title
    


from django.db import models
from django.conf import settings  # Import settings
from django.contrib.auth.models import User

class UserLocation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"{self.user.username} - ({self.latitude}, {self.longitude})"
    
class PoliceStation(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def _str_(self):
        return self.name

class Safeplaces(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def str(self):
        return self.name