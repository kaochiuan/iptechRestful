from django.db import models

# Create your models here.
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db import models
from django.contrib.auth.models import User
from django.db.models.query_utils import Q

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)

class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value':self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)

class MenuManager(models.Manager):
    def createMenu(self, name, isCustomized, isCustomCoffeeBean, coffeeCombination,
                   coffeeThickness, pressureSelection, temperatureSelection,
                   sugarSelection, milkSelection, createDate, owner):
        menu = self.create(name=name, isCustomized=isCustomized,
                           isCustomCoffeeBean=isCustomCoffeeBean,
                           coffeeCombination=coffeeCombination,
                           coffeeThickness=coffeeThickness, pressureSelection=pressureSelection,
                           temperatureSelection=temperatureSelection,
                           sugarSelection=sugarSelection, milkSelection=milkSelection,
                           createDate=createDate, owner=owner)
        return menu
    def filterMenu(self, name, isCustomized, isCustomCoffeeBean, coffeeCombination,
                   coffeeThickness, pressureSelection, temperatureSelection, sugarSelection,
                   milkSelection, owner):
        menu = self.filter(name=name, isCustomized=isCustomized,
                           isCustomCoffeeBean=isCustomCoffeeBean,
                           coffeeCombination=coffeeCombination,
                           coffeeThickness=coffeeThickness,
                           pressureSelection=pressureSelection,
                           temperatureSelection=temperatureSelection,
                           sugarSelection=sugarSelection,
                           milkSelection=milkSelection,
                           owner=owner)
        return menu
    def searchByName(self, name):
        menu = self.filter(name__icontains=name)
        return menu
    def filterByDate(self, start, end):
        menu = self.filter(createDate__range=(start, end))
        return menu
    def searchByOwner(self, name):
        menu = self.filter(owner__username=name)
        return menu
    def filterSystemMenu(self):
        menu = self.filter(isCustomized=False)
        return menu

class Menu(models.Model):
    menuId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    isCustomized = models.BooleanField()
    isCustomCoffeeBean = models.BooleanField()
    coffeeCombination = models.PositiveSmallIntegerField()
    coffeeThickness = models.PositiveSmallIntegerField()
    temperatureSelection = models.PositiveSmallIntegerField()
    pressureSelection = models.PositiveSmallIntegerField()
    sugarSelection = models.PositiveSmallIntegerField()
    milkSelection = models.PositiveSmallIntegerField()
    createDate = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    objects = MenuManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['createDate']

class StoreManager(models.Manager):
    def createStore(self, name, latitude, longitude, address):
        store = self.create(name=name, latitude=latitude, longitude=longitude, address=address)
        return store
    def filterStore(self, name, latitude, longitude, address):
        store = self.filter(name=name, latitude=latitude, longitude=longitude, address=address)
        return store
    def searchByName(self, name):
        store = self.filter(name__icontains=name)
        return store

class CoffeeStore(models.Model):
    storeId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=120)
    objects = StoreManager()

    def __str__(self):
        return str.format("{0}_{1}", self.storeId, self.name)

class DeviceManager(models.Manager):
    def createDevice(self, store, deviceName, ipv4Address, port):
        device = self.create(store=store, deviceName=deviceName, ipv4Address=ipv4Address, port=port)
        return device

    def filterByStoreId(self, storeId):
        devices = self.filter(store__storeId=storeId)
        print('result of filterByStoreId:{0}'.format(devices))
        return devices

class DeviceInfo(models.Model):
    store = models.ForeignKey(CoffeeStore, on_delete=models.CASCADE)
    deviceId = models.AutoField(primary_key=True)
    deviceName = models.CharField(max_length=20)
    ipv4Address = models.GenericIPAddressField(protocol='IPv4')
    port = IntegerRangeField(range(0, 65535))
    objects = DeviceManager()

    def __str__(self):
        return str.format("{0}_{1}", self.deviceId, self.deviceName)


class ProfileManager(models.Manager):
    def createProfile(self, userId, gender, birthday, phone, address, username):
        profile = self.create(userId=userId, gender=gender, birthday=birthday,
                              phone=phone, address=address, username=username)
        return profile

    def searchByName(self, name):
        profile = self.filter(username=name)
        return profile

class UserProfile(models.Model):
    profileId = models.AutoField(primary_key=True)
    userId = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, blank=True)
    gender = models.PositiveSmallIntegerField()
    birthday = models.DateField(blank=True)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    objects = ProfileManager()

class ConsumeManager(models.Manager):
    def createRecord(self, consumeDate, status, store, menu, consumer):
        record = self.create(consumeDate=consumeDate, status=status,
                             store=store, menu=menu, consumer=consumer)
        return record
    def filterByDate(self, name, start, end):
        record = self.filter(consumer__username=name, consumeDate__range=(start, end))
        return record

class ConsumeRecords(models.Model):
    recordId = models.AutoField(primary_key=True)
    consumeDate = models.DateTimeField()
    store = models.ForeignKey(CoffeeStore, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    consumer = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField()
    objects = ConsumeManager()
