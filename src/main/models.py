from datetime import datetime
from time import time
import django
from django.db import models
from django.contrib.auth.models import User, AbstractUser, BaseUserManager
from .choices import *
from .pays import *

class User(AbstractUser):
    id_document = models.FileField(upload_to='user/', null=True)

class Person(models.Model):
    gender = models.CharField(max_length=1, choices=GENDER)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS, default='1')
    partner_name = models.CharField(blank=True, max_length=200)
    profession = models.CharField(max_length=100, null=True)
    nationality = models.CharField(max_length=3, choices=PAYS, default='TG')
    birthday = models.DateField('birthday', default='2004-12-31')
    bornAt = models.CharField(max_length=100)
    address = models.CharField(max_length=200, default="")
    residence = models.CharField(blank=True, max_length=200, default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=100, blank=True, default='CLIENT', choices=ROLE)
    phone = models.CharField(max_length=12, null=True)

    def __str__ (self):
        return self.user.username + "\t" + self.user.get_full_name() + "\t" + str(self.birthday) + "\t" + self.type


class Requisition(models.Model):
   
    UPLOAD = f'requisition/%Y/%m/%d/'

    NUMBER = int(time())
    number = models.BigIntegerField(default=NUMBER, primary_key=True)
    # Property info
    area_a = models.PositiveIntegerField()
    area_ca = models.PositiveIntegerField()
    quality = models.IntegerField(choices=QUALITY, default=1)
    type = models.IntegerField(choices=TYPE)
    info = models.CharField(max_length=100)
    quarter = models.CharField(max_length=100)
    real_name = models.CharField(max_length=100)
    prefecture = models.CharField(max_length=100)
    
    east = models.CharField(max_length=100)
    western = models.CharField(max_length=100)
    north = models.CharField(max_length=100)
    south = models.CharField(max_length=100)
    
    # Owners info
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    co_owner = models.ManyToManyField(User, related_name='owners', blank=True)

    # Files and payment
    liquidation_receipt = models.FileField(upload_to=UPLOAD, null=True, blank=True)
    file = models.FileField(upload_to=UPLOAD, null=True, blank=True)
    land_receipt = models.FileField(upload_to=UPLOAD)
    authorization = models.FileField(upload_to=UPLOAD, null=True, blank=True)
    floor_plan = models.FileField(upload_to=UPLOAD)
    notarial_instrument = models.FileField(upload_to=UPLOAD, null=True, blank=True)
    pay = models.CharField(max_length=30, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    pay_date = models.DateTimeField(null=True, blank=True)

    def create_with_pk(self):
        instance = self.create()
        instance.save()     # probably this line is unneeded
        return instance


class State(models.Model):
    STATE = [('A', 'En cours'), ('P', 'En attente'), ('C', 'Rejetée'), ('T', 'Terminée')]

    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    state = models.CharField(max_length=1, choices=STATE, null=True, blank=True)
    raison = models.CharField(max_length=100, default='Phase initiale')
    date = models.DateTimeField(auto_now_add=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='state_author', null=True)




class Complaint(models.Model):
    id = models.BigIntegerField(default=int(time()), primary_key=True)
    requisition = models.ForeignKey(Requisition, null=True, on_delete=models.CASCADE)

    object = models.CharField(max_length=100)
    message = models.TextField(max_length=1000)
    proof_file = models.FileField(upload_to='plaintes/%Y/%m/%d/')
    state = models.BooleanField(null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    state_date = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaint_author', null=True)

    state_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaint_state_author', null=True)




class Demarcation(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE)
    choosed_date = models.DateTimeField()
    date = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    drawer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drawer', null=True)

    surveyor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveyor', null=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='demarcation_author', null=True)




class Report(models.Model):
    demarcation = models.ForeignKey(Demarcation, on_delete=models.CASCADE)
    pv = models.TextField(max_length=1000)
    floor_plan = models.FileField(upload_to='plans/%Y/%m/%d/', null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    state = models.BooleanField(null=True)



class Coordinate(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)



class landDeed(models.Model):
    number = models.BigIntegerField(default=int(time()))
    requisition = models.OneToOneField(Requisition, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_by', null=True)




class Mutation(models.Model):
    landDeed = models.ForeignKey(landDeed, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    way = models.CharField(max_length=1, choices=WAY, default='H', blank=True)
    to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to', null=True)




class Sale(models.Model):
    landDeed = models.ForeignKey(landDeed, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    purchase = models.OneToOneField(Mutation, on_delete=models.CASCADE, null=True)

