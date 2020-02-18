from django.template.response import TemplateResponse
from django.contrib.auth import login as log_user_in, authenticate
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.response import Response
from .models import User, Address, State, District, SubDistrict, Village

__author__ = "Hariom"


def show_registration(request):
    if request.user.is_authenticated:
        return redirect("user:address")

    ctx = {"message": ""}
    if request.method == "POST":
        username = str(request.POST["username"]).lower()
        password = request.POST["password"]

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password)
            log_user_in(request, user)
            return redirect("user:address")
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                log_user_in(request, user)
                return redirect("user:address")
            ctx["message"] = "Username or password is not valid"
    return TemplateResponse(request, 'registration.html', ctx)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('user:registration')


@login_required
def show_address_form(request):
    try:
        if request.user.address:
            return redirect("user:registration_id")
    except AttributeError:
        if request.method == "POST":
            address_data = {
                "state"        : State.objects.get(name__iexact=request.POST['state']),
                "district"     : District.objects.get(name__iexact=request.POST['district']),
                "sub_district" : SubDistrict.objects.get(name__iexact=request.POST['sub_district']),
                "village"      : Village.objects.get(name__iexact=request.POST['village']),
                "user"         : request.user
            }
            address = Address.objects.create(**address_data)
            address.set_user_registration_code()

            return redirect("user:registration_id")

        states = State.objects.all()
        ctx = {
            "states": states
        }
    return TemplateResponse(request, 'address.html', ctx)


@login_required
def show_registration_id(request):
    registration_number = request.user.registration_number

    if not registration_number:
        return redirect("user:address")

    ctx = {
        "registration_id": request.user.registration_number
    }
    return TemplateResponse(request, 'registration_id.html', ctx)


class AddressApi(generics.GenericAPIView):

    @staticmethod
    def get(request):
        if request.GET.get('state'):
            state  = request.GET.get('state')
            states = State.objects.filter(name__iexact=state)
            if not states.exists():
                return Response({"districts": []}, status=status.HTTP_200_OK)
            else:
                return Response({"districts": [district.name for district in states.first().districts.all()]},
                                status=status.HTTP_200_OK)

        elif request.GET.get('district'):
            district = request.GET.get('district')
            districts = District.objects.filter(name__iexact=district)
            if not districts.exists():
                return Response({"sub_districts": []}, status=status.HTTP_200_OK)
            else:
                return Response({"sub_districts": [sub_district.name for sub_district in districts.first().subdistricts.all()]},
                                status=status.HTTP_200_OK)

        elif request.GET.get("sub_district"):
            sub_district = request.GET.get('sub_district')
            sub_districts = SubDistrict.objects.filter(name__iexact=sub_district)
            if not sub_districts.exists():
                return Response({"villages": []}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"villages": [village.name for village in sub_districts.first().villages.all()]},
                    status=status.HTTP_200_OK)

        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

