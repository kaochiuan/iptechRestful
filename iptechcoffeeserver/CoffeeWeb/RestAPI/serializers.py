from datetime import datetime
from django.contrib.auth.models import User, Group
from django.core.exceptions import MultipleObjectsReturned
from rest_framework import serializers
from CoffeeWeb.RestAPI.models import CoffeeStore, Menu, ConsumeRecords, UserProfile, DeviceInfo

class UserSerializer(serializers.ModelSerializer):
    def create(self, data):
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'])
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email',)
        write_only_fields = ('password',)
        read_only_fields = ('id',)

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class SotreSerializer(serializers.ModelSerializer):
    def create(self, data):
        store = CoffeeStore.objects.createStore(
            name=data['name'], latitude=data['latitude'],
            longitude=data['longitude'], address=data['address'])
        return store

    class Meta:
        model = CoffeeStore
        fields = ('storeId', 'name', 'latitude', 'longitude', 'address')
        read_only_fields = ('storeId',)

class MenuSerializer(serializers.ModelSerializer):
    def create(self, data):
        try:
            nowDateTime = datetime.now()
            menu = Menu.objects.createMenu(name=data['name'],
                                           isCustomized=data['isCustomized'],
                                           isCustomCoffeeBean=data['isCustomCoffeeBean'],
                                           coffeeCombination=data['coffeeCombination'],
                                           coffeeThickness=data['coffeeThickness'],
                                           pressureSelection=data['pressureSelection'],
                                           temperatureSelection=data['temperatureSelection'],
                                           sugarSelection=data['sugarSelection'],
                                           milkSelection=data['milkSelection'],
                                           createDate=nowDateTime,
                                           owner=data['owner'])

        except MultipleObjectsReturned:
            menu = None
        return menu


    class Meta:
        model = Menu
        fields = ('menuId', 'name', 'isCustomized',
                  'isCustomCoffeeBean', 'coffeeCombination', 'coffeeThickness',
                  'pressureSelection', 'temperatureSelection',
                  'sugarSelection', 'milkSelection',
                  'createDate', 'owner')

        read_only_fields = ('menuId', 'createDate',)
        write_only_fields = ('owner',)

class ConsumeSerializer(serializers.ModelSerializer):
    def create(self, data):
        try:
            consumeDateTime = datetime.now()

            record = ConsumeRecords.objects.createRecord(consumeDate=consumeDateTime,
                                                         status=data['status'],
                                                         store=data['store'],
                                                         menu=data['menu'],
                                                         consumer=data['consumer'])
        except MultipleObjectsReturned:
            record = None

        return record

    class Meta:
        model = ConsumeRecords
        fields = ('recordId', 'consumeDate', 'status', 'store', 'menu', 'consumer')
        read_only_fields = ('recordId', 'consumeDate',)

class ProfileSerializer(serializers.ModelSerializer):
    def create(self, data):
        try:
            profile = UserProfile.objects.createProfile(
                userId=data['userId'], gender=data['gender'],
                birthday=data['birthday'], phone=data['phone'],
                address=data['address'], username=data['username'])
        except MultipleObjectsReturned:
            profile = None

        return profile

    class Meta:
        model = UserProfile
        fields = ('profileId', 'gender', 'birthday', 'phone', 'address', 'userId', 'username')
        read_only_fields = ('profileId')

class DeviceSerializer(serializers.ModelSerializer):
    def create(self, data):
        try:
            device = DeviceInfo.objects.createDevice(
                store=data['store'], deviceName=data['deviceName'],
                ipv4Address=data['ipv4Address'], port=data['port'])
        except MultipleObjectsReturned:
            device = None

        return device

    class Meta:
        model = DeviceInfo
        fields = ('deviceId', 'deviceName', 'ipv4Address', 'port', 'store')
        read_only_fields = ('deviceId')
        write_only_fields = ('store',)
