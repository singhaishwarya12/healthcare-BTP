from rest_framework.views import APIView
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import BasePermission
from doctor.models import doctor
from patient.models import patient
from django.http import JsonResponse
import folium
import requests
from geopy.distance import distance
from geopy.geocoders import Nominatim

BASE_URL = 'https://nominatim.openstreetmap.org/search?format=json'


class GeolocationView(APIView):

    def get_lat_lng_from_postcode(postcode):
        geolocator = Nominatim(user_agent="my-application")
        location = geolocator.geocode(postcode)
        if location:
            return location.latitude, location.longitude
        return None, None

    def get(self, request,pk=None, format=None):
        Patient = patient.objects.get(pk=pk)
        user_pincode = Patient.pincode
        print(user_pincode)
        response = requests.get(f"{BASE_URL}&postalcode={user_pincode}&country=India")
        """lat, lng = self.get_lat_lng_from_postcode(user_pincode)"""
        data = response.json()
        print(data)

        Userlatitude = data[0].get('lat')
        Userlongitude =data[0].get('lon')
        Userlocation = (Userlatitude,Userlongitude)

        """Userlocation = (lat,lng)"""

        my_map = folium.Map(location=Userlocation, zoom_start=10)
        folium.Marker(location=Userlocation, icon=folium.Icon(color='red')).add_to(my_map) 
        
        query = doctor.objects.all()

        for dr in query:
            dr_pincode = dr.pincode
            response = requests.get(f"{BASE_URL}&postalcode={dr_pincode}&country=India")
            data = response.json()
            print(data)
            Doclocation = (data[0].get('lat') , data[0].get('lon'))
            """lat, lng = self.get_lat_lng_from_postcode(dr_pincode)
            Doclocation = (lat,lng)"""
            dis = distance(Userlocation,Doclocation)

            if dis<1000.0 :
                popup = folium.Popup("<a href='https://www.cricbuzz.com/'><img src='https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png' alt='profile pic' style='float:left; margin-right:10px;' width='50' height='50'><p style='float:right'>Dr. Alok Sharma</p><br><p style='color:black;'> Dermatologist</p></a>")
                folium.Marker(location=Doclocation, popup=popup, tooltip='<b>Dr. Alok Sharma</b>').add_to(my_map)

        map_data = my_map.to_json()
        # return JSON response with map data
        return JsonResponse(map_data, safe=False)
    