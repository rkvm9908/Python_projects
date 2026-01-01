from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    mobile = models.CharField(max_length=15)
    

    def __str__(self):
        return self.user.username
