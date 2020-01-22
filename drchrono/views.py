from django.shortcuts import redirect
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth

from drchrono.endpoints import DoctorEndpoint
from drchrono.endpoints import PatientEndpoint
from drchrono.endpoints import AppointmentEndpoint
from drchrono.endpoints import OfficeEndpoint

import datetime


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def make_api_request_on_doctors(self):
        """
        """
        access_token = self.get_token()
        api = DoctorEndpoint(access_token)
        doctors = {}
        for doctor in list(api.list()):
            doctors[doctor['id']] = doctor
        return doctors

    def make_api_request_on_patients(self):
        """
        """
        access_token = self.get_token()
        api = PatientEndpoint(access_token)
        patients = {}
        for patient in list(api.list()):
            patients[patient['id']] = patient
        return patients

    def make_api_request_on_appointments(self, date=None, start=None, end=None):
        """
        """
        access_token = self.get_token()
        api = AppointmentEndpoint(access_token)
        appointments = {}
        for appointment in list(api.list(None, date, start, end)):
            appointments[appointment['id']] = appointment
        # print("debug!!!", appointments['138733281'])
        return appointments

    def make_api_request_on_offices(self):
        """
        """
        access_token = self.get_token()
        api = OfficeEndpoint(access_token)
        offices = {}
        for office in list(api.list()):
            offices[office['id']] = office
        # print("debug!!!", appointments['138733281'])
        return offices

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        # Hit the API using one of the endpoints just to prove that we can
        # If this works, then your oAuth setup is working correctly.
        today_date = datetime.datetime.now().strftime("%Y-%m-%d")

        appointments = self.make_api_request_on_appointments(today_date)
        doctors = self.make_api_request_on_doctors()
        patients = self.make_api_request_on_patients()
        offices = self.make_api_request_on_offices()

        appointments_list = []

        for appointment in appointments:
            doctor_details = doctors[appointments[appointment]['doctor']]
            patient_details = patients[appointments[appointment]['patient']]
            office_details = offices[appointments[appointment]['office']]
            exam_room_details = office_details['exam_rooms'][appointments[appointment]['exam_room']]

            time_formatted = datetime.datetime.strptime(
                appointments[appointment]['scheduled_time'], '%Y-%m-%dT%H:%M:%S'
                )
            duration_formatted = int(appointments[appointment]['duration'])
            
            appointments[appointment]['doctor_details'] = doctor_details
            appointments[appointment]['patient_details'] = patient_details
            appointments[appointment]['office_details'] = office_details
            appointments[appointment]['exam_room_details'] = exam_room_details


            appointments[appointment]['scheduled_time'] = time_formatted
            appointments[appointment]['duration'] = duration_formatted
            appointments[appointment]['schedule_card_width'] = 5+duration_formatted/2.5

            appointments_list.append(appointments[appointment])

            print(appointments[appointment].keys())

        appointments_list.sort(key=lambda x: x['scheduled_time'])
        
        kwargs['doctor'] = doctors.items()[0][1]
        kwargs["appointments"]=appointments_list

        # print(kwargs)
        return kwargs
