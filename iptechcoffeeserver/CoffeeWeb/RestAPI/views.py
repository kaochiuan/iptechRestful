from django.contrib.auth.models import User, Group, AnonymousUser
from rest_framework import viewsets, status
from CoffeeWeb.RestAPI.serializers import UserSerializer, GroupSerializer, MenuSerializer
from CoffeeWeb.RestAPI.serializers import ConsumeSerializer, SotreSerializer, ProfileSerializer
from CoffeeWeb.RestAPI.serializers import DeviceSerializer
from CoffeeWeb.RestAPI.models import Menu, ConsumeRecords, CoffeeStore, UserProfile, DeviceInfo
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ParseError
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.http import HttpResponse
from django.core import serializers
import requests
import itertools

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        elif self.request.method == 'POST':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super(UserViewSet, self).get_permissions()

class DeviceInfoViewSet(viewsets.ModelViewSet):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = DeviceInfo.objects.all()
    serializer_class = DeviceSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super(DeviceInfoViewSet, self).get_permissions()

class ProfileViewSet(viewsets.ModelViewSet):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer

    def create(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user)
        userid = request.data.get('userId','none')
        if userid == 'none' and (user.id is not None):
            userid = user.id
            request.data['userId'] = userid

        serializer = self.get_serializer(data=request.data)
        isvalid = serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request):
        user = User.objects.get(username=request.user)
        userid = user.id
        try:
            userprofile = UserProfile.objects.get(userId=userid)
        except:
            userprofile = UserProfile()
            pass
            
        if request.user.is_authenticated() == True:
            queryset = userprofile
            serializer = ProfileSerializer(queryset, many=False)
        else:
            queryset = profile
            serializer = ProfileSerializer(queryset, many=False)

        return Response(serializer.data)


    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super(ProfileViewSet, self).get_permissions()

class MenuViewSet(viewsets.ModelViewSet):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    serializer_class = MenuSerializer
    queryset = Menu.objects.all().order_by('-createDate')

    def create(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user)
        owner = request.data.get('ownr','none')
        if owner == 'none' and (user.id is not None):
            userid = user.id
            request.data['owner'] = userid

        serializer = self.get_serializer(data=request.data)
        isvalid = serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def list(self, request):
        systemDefaultMenus = []
        #print('UserData:{0}, {1}'.format(request.user, request.user.is_authenticated()))
        systemDefaultMenus = Menu.objects.filterSystemMenu().order_by('-createDate')
        if request.user.is_authenticated() == False:
            queryset = systemDefaultMenus
        else:
            queryset = Menu.objects.searchByOwner(name=request.user).order_by('-createDate')
            queryset = list(itertools.chain(queryset, systemDefaultMenus))
        serializer = MenuSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super(MenuViewSet, self).get_permissions()

class ConsumeViewSet(viewsets.ModelViewSet):
    authentication_classes = (JSONWebTokenAuthentication, TokenAuthentication,)

    queryset = ConsumeRecords.objects.all().order_by('-consumeDate')
    serializer_class = ConsumeSerializer

    def create(self, request, *args, **kwargs):
        user = User.objects.get(username=request.user)
        consumer = request.data.get('consumer','none')
        if consumer == 'none' and (user.id is not None):
            userid = user.id
            request.data['consumer'] = userid

        orderstatus = request.data.get('status','none')
        if orderstatus == 'none':
            request.data['status'] = 0

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        recordId = serializer.data['recordId']
        #print('added consumeRecordId: {0}'.format(recordId))
        storeId = serializer.data['store']
        devicesofstore = DeviceInfo.objects.filterByStoreId(storeId)

        try:
            counter = len(devicesofstore)

            if counter == 1:
                rndidx = 0
            elif counter == 0:
                raise Exception('none of device in the store of {}'.format(storeId))
            else:
                rndidx = random.randrange(counter - 1)

            deviceName = devicesofstore[rndidx].deviceName
            deviceIp = devicesofstore[rndidx].ipv4Address
            port = devicesofstore[rndidx].port

            resturl = 'http://{0}:{1}/api/Command/Motor/{2}/{3}/'.format(deviceIp, port, 'on', recordId)
            machineresponse = requests.get(resturl)

            #print('response result:{0}'.format(response.text))
        except:
            pass

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)

        return super(ConsumeViewSet, self).get_permissions()

class StoreViewSet(viewsets.ModelViewSet):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    queryset = CoffeeStore.objects.all()
    serializer_class = SotreSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super(StoreViewSet, self).get_permissions()

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class AuthView(APIView):
    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, format=None):
        return Response({'detail': "I suppose you are authenticated"})
