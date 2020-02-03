from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils import dateparse

from django.http import HttpResponseRedirect
from django.views.generic import View
from django.shortcuts import render

from .forms import CheckInNameSSNForm, ChangeStatusForm, \
    ChangeAppointmentInfoForm, ChangePatientInfoForm

from social_django.models import UserSocialAuth

from drchrono.endpoints import DoctorEndpoint
from drchrono.endpoints import PatientEndpoint
from drchrono.endpoints import AppointmentEndpoint
from drchrono.endpoints import OfficeEndpoint

import datetime

# Define UTC Timezone OFFSET
# The DrChrono account has Eastern Standard Time, so here is set to UTC -5
UTC_TIMEZONE_OFFSET = -5


class Helpers:
    """
    A class contains some helpers such as time format coversion
    """
    @staticmethod
    def time_formatter(hours, minutes, ampm):
        """
        Covert time from hours, minutes, AM/PM to ISO format
        that can be sent through API
        """
        time = [0, 0]
        if ampm == "AM" and hours == "12":
            time[1] += int(minutes)
        elif ampm == "AM":
            time[0] += int(hours)
            time[1] += int(minutes)
        elif ampm == "PM" and hours == "12":
            time[0] += int(hours)
            time[1] += int(minutes)
        elif ampm == "PM":
            time[0] += int(hours) + 12
            time[1] += int(minutes)

        time = [str(x).zfill(2) for x in time]
        today = datetime.date.today()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")

        date_and_time = year + '-' + month + '-' + day + 'T'\
            + time[0] + ':' + time[1] + ':' + '00'
        date_and_time = datetime.datetime.strptime(
            date_and_time, '%Y-%m-%dT%H:%M:%S')
        date_and_time = datetime.datetime.isoformat(date_and_time)
        return date_and_time


class APIrequest:
    """
    Main agent class, to handle different API requests,
    and call Endpoints to preform API requests
    The __init__ constructor also store necessary data for views
    Note: The appointments are ALL for TODAY's ONLY
    """

    def __init__(self):
        # Lists of doctors, appointments, patients, offices etc.
        self.doctors = {}
        self.appointments = {}
        self.patients = {}
        self.offices = {}

        # Upcoming appointments in sorted by scheduled_time
        self.app_upcoming_list = []
        # Past appointments in sorted by scheduled_time
        self.app_past_list = []

        # The time spent for patient to wait for each appointment
        self.wait_time = []

        # Sum of the wait time of all patients to calculate the average
        self.wait_time_sum = 0

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens.
        This dark magic will fetch it for us if we've already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']
        return access_token

    def get_doctors(self):
        """
        Get all doctors (without pagenating), 
        should only contain 1, for developer API
        Using ID as key
        """
        access_token = self.get_token()
        api = DoctorEndpoint(access_token)
        for doctor in list(api.list()):
            self.doctors[doctor['id']] = doctor
        return self.doctors

    def get_patients(self):
        """
        Get all patients (without pagenating)
        Using ID as key
        """
        access_token = self.get_token()
        api = PatientEndpoint(access_token)
        for patient in list(api.list()):
            self.patients[patient['id']] = patient
        return self.patients

    def get_appointments(self, date=None, start=None, end=None):
        """
        Get appointments in certain date or range
        But in this Hackathon, only TODAY's appointments are pulled. 
        Using ID as key
        """
        access_token = self.get_token()
        api = AppointmentEndpoint(access_token)
        for appointment in list(api.list(None, date, start, end)):
            self.appointments[appointment['id']] = api.fetch(
                appointment['id'], 'verbose=true')
        return self.appointments

    def get_offices(self):
        """
        Get all offices, and also replace exam_rooms from list
        to dict, using exam room indexes as keys, for later access
        Using ID as key
        """
        access_token = self.get_token()
        api = OfficeEndpoint(access_token)
        for office in list(api.list()):
            exam_rooms = {}
            for exam_room in office['exam_rooms']:
                exam_rooms[exam_room['index']] = exam_room
            office['exam_rooms'] = exam_rooms
            self.offices[office['id']] = office
        return self.offices

    def fetch_a_patient(self, id='None'):
        """
        Fetch a patient using ID, return the result
        """
        access_token = self.get_token()
        api = PatientEndpoint(access_token)
        return api.fetch(id)

    def fetch_a_office(self, id='None'):
        """
        Fetch a office using ID, return the result
        """
        access_token = self.get_token()
        api = OfficeEndpoint(access_token)
        office = api.fetch(id)
        exam_rooms = {}
        for exam_room in office['exam_rooms']:
            exam_rooms[exam_room['index']] = exam_room
        office['exam_rooms'] = exam_rooms
        return office

    def make_api_request(self):
        """
        A method as automatic script to pull
        1. Today's appointment
        2. All doctors
        3. All patients
        4, All offices
        """
        # Get today's date and using it to pull all appointments of today
        self.today_datetime = datetime.datetime.utcnow(
        ) + datetime.timedelta(hours=UTC_TIMEZONE_OFFSET)
        self.today_date = self.today_datetime.strftime("%Y-%m-%d")

        self.get_appointments(self.today_date)
        self.get_doctors()
        self.get_patients()
        self.get_offices()

    def change_appointment(self, id="None", data={}):
        '''
        Submit request to change an appintment with ID
        All request data is in dict 'data',
        '''
        access_token = self.get_token()
        api = AppointmentEndpoint(access_token)
        return api.update(id, data)

    def change_patient(self, id="None", data={}):
        '''
        Submit request to change an patient with ID
        All request data is in dict 'data',
        '''
        access_token = self.get_token()
        api = PatientEndpoint(access_token)
        return api.update(id, data)

    def find_patient(self, last_name, social_security_number):
        '''
        This is for patient check in
        Based on given last time and last 4 digits of SSN
        Locate the patient, then call the method below
        to see if she/he has the appointment today

        If there are multiple appointments for 1 patient
        Get most recent one.
        '''
        for id in self.patients:
            if self.patients[id]["last_name"] == last_name \
                and self.patients[id]["social_security_number"][7:] \
                    == social_security_number:
                return self.get_patient_next_appointment_today(id)
        return None

    def get_patient_next_appointment_today(self, patient_id):
        '''
        Combined with the method "find_patient" above
        This is to find the today's most recent appointment for the patient
        from upcoming appointments
        '''
        if patient_id:
            if self.app_upcoming_list:
                i = 0
                while i < len(self.app_upcoming_list):
                    if self.app_upcoming_list[i]["patient"] == patient_id:
                        break
                    i += 1
                return self.app_upcoming_list[i]
        else:
            return None

    def get_today_appointments(self):
        '''
        Get today's all appointment, and process the data of each appointment
        '''
        for id, appointment in self.appointments.items():
            # Covert datetime from API to Python datetime object
            scheduled_time = datetime.datetime.strptime(
                appointment['scheduled_time'], '%Y-%m-%dT%H:%M:%S'
            )
            # Conver duration sent by API from string to integer
            duration_formatted = int(appointment['duration'])

            # Calculate the finish time of the appointment with
            # scheduled_time and duration
            finished_time = scheduled_time + \
                datetime.timedelta(minutes=duration_formatted)

            # Prepare to attach doctor/patient/office, exam details
            # to each appointment
            doctor_details = self.doctors[appointment['doctor']]
            patient_details = self.patients[appointment['patient']]
            office_details = self.offices[appointment['office']]
            exam_room_details \
                = office_details['exam_rooms'][appointment['exam_room']]
            # Attach
            appointment['doctor_details'] = doctor_details
            appointment['patient_details'] = patient_details
            appointment['office_details'] = office_details
            appointment['exam_room_details'] = exam_room_details

            # Get the most recent status change
            # Then process datetime to Python datetime format
            last_status = dict(appointment['status_transitions'][-1])
            for status_change in appointment['status_transitions']:
                status_change["datetime"] \
                    = dateparse.parse_datetime(status_change["datetime"])

            wait_time = None
            checked_in_time = None          # Check-in time in Date & Time
            checked_in_time_only = None     # Check-in time in TIME only

            # Process check-in time
            if last_status['to_status'] == 'Checked In':
                checked_in_time = last_status['datetime']
                checked_in_time = datetime.datetime.strptime(
                    checked_in_time, '%Y-%m-%dT%H:%M:%S')
                wait_time = (self.today_datetime -
                             checked_in_time).seconds // 60
                checked_in_time_only = checked_in_time.strftime("%-I:%-M %p")

            # Attach newly generated information
            appointment['last_status'] = last_status
            appointment['scheduled_time'] = scheduled_time
            appointment['scheduled_finish_time'] = finished_time
            appointment['duration'] = duration_formatted
            appointment['wait_time'] = wait_time
            appointment['checked_in_time'] = checked_in_time_only
            appointment['schedule_card_width'] = 5 + \
                duration_formatted/2.5

            # Decide if the appointment is finished
            # No? go to the upcoming appointments list
            # Yes? go the past appointments list
            if self.today_datetime > finished_time:
                self.app_past_list.append(appointment)
            else:
                self.app_upcoming_list.append(appointment)

            # If wait_time exists,
            # add to the list for wait time statistics and graph
            if wait_time != None:
                self.wait_time_sum += wait_time
                self.wait_time.append(
                    {"scheduled_time": scheduled_time, "wait_time": wait_time,
                     "patient_first_name": patient_details["first_name"],
                     "patient_last_name": patient_details["last_name"]})

        # Sort the list based on scheduled starting time of appointments
        self.app_upcoming_list.sort(key=lambda x: x['scheduled_time'])
        self.app_past_list.sort(key=lambda x: x['scheduled_time'])
        self.wait_time.sort(key=lambda x: x['scheduled_time'])

        return self.app_upcoming_list


class ChangeStatus(View):
    """
    A view to handle change status POST request,
    The POST data from HTML form will be processed,
    And by calling the APIrequest class to send the data out
    """
    template_name = 'post_action.html'

    def post(self, request, *args, **kwargs):
        context = {}
        context["is_success"] = False   # if success flag to let user know

        # Form validation
        check_in_form = ChangeStatusForm(request.POST)
        if check_in_form.is_valid():
            api_post_data = {}

            status = check_in_form.cleaned_data["status"]

            api_post_data["status"] = status

            # Create an instance of APIrequest
            # If the appointment needs to be changed is in today's appointment
            # Sent to server
            new_api_request = APIrequest()
            new_api_request.make_api_request()
            appointment = str(check_in_form.cleaned_data["appointment"])
            if appointment in new_api_request.appointments:
                new_api_request.change_appointment(
                    appointment, api_post_data)
                # These are for the views to display message to user
                context["is_success"] = True
                context["action"] = "change_status"
                context["status"] = check_in_form.cleaned_data["status"]

        return render(request, self.template_name, context)


class ChangeAppointmentInfo(View):
    """
    A view to handle change appointment POST request,
    The POST data from HTML form will be processed,
    And by calling the APIrequest class to send the data out
    """
    template_name = 'post_action.html'

    def post(self, request, *args, **kwargs):
        context = {}
        context["is_success"] = False   # if success flag to let user know

        # Form validation
        change_app_info_form = ChangeAppointmentInfoForm(request.POST)
        if change_app_info_form.is_valid():
            # The form send office and exam room in one string
            # Need to seperate it
            office_exam_room \
                = change_app_info_form.cleaned_data["office_exam_room"]\
                .split(" ")
            office = office_exam_room[0]
            exam_room = office_exam_room[1]

            # Process seperated time fields and converted into ISO format
            hours = change_app_info_form.cleaned_data["hours"]
            minutes = change_app_info_form.cleaned_data["minutes"]
            ampm = change_app_info_form.cleaned_data["ampm"]
            date_and_time = Helpers.time_formatter(hours, minutes, ampm)

            # Contains data to be posted for API
            # Add processed data
            api_post_data = change_app_info_form.cleaned_data
            api_post_data["appointment"] = str(api_post_data["appointment"])
            api_post_data["duration"] = str(api_post_data["duration"])
            api_post_data["scheduled_time"] = date_and_time
            api_post_data["office"] = office
            api_post_data["exam_room"] = exam_room
            # Remove original form formats that didn't meet API formats
            api_post_data.pop("hours")
            api_post_data.pop("minutes")
            api_post_data.pop("ampm")
            api_post_data.pop("office_exam_room")

            # Create an instance of APIrequest
            # If the appointment needs to be changed is in today's appointment
            # Sent to server
            new_api_request = APIrequest()
            new_api_request.make_api_request()
            appointment = api_post_data["appointment"]
            if appointment in new_api_request.appointments:
                new_api_request.change_appointment(appointment, api_post_data)
                # These are for the views to display message to user
                context["is_success"] = True
                context["action"] = "change_appointment_info"
                context["notes"] = "Change appointment information"

        return render(request, self.template_name, context)


class ChangePatientInfo(View):
    """
    A view to handle change patient info POST request,
    The POST data from HTML form will be processed,
    And by calling the APIrequest class to send the data out
    """
    template_name = 'post_action.html'

    def post(self, request, *args, **kwargs):
        context = {}
        context["is_success"] = False   # if success flag to let user know

        # Form validation
        change_patient_info_form = ChangePatientInfoForm(request.POST)
        if change_patient_info_form.is_valid():
            # Contains data to be posted for API
            # Add processed data
            api_post_data = change_patient_info_form.cleaned_data
            date_of_birth = str(api_post_data["year"]) + '-' + \
                api_post_data["month"] + '-' + \
                api_post_data["day"]
            api_post_data["patient"] = str(api_post_data["patient"])
            api_post_data["date_of_birth"] = date_of_birth
            # Remove original form formats that didn't meet API formats
            api_post_data.pop("year")
            api_post_data.pop("month")
            api_post_data.pop("day")
            # Role is to indicate, if patient or doctor is changing the info
            # Then they could return to different pages
            role = api_post_data.pop("role")

            # Create an instance of APIrequest
            # If the patient needs to be changed is in patient list
            # Sent to server
            new_api_request = APIrequest()
            new_api_request.make_api_request()
            patient = api_post_data["patient"]
            if int(patient) in new_api_request.patients:
                new_api_request.change_patient(patient, api_post_data)
                # These are for the views to display message to user
                context["is_success"] = True
                context["action"] = "change_patient_info"
                context["notes"] = "Update patient infomation"
                context["role"] = role

        return render(request, self.template_name, context)


class SetupView(TemplateView):
    """
    THIS IS NO LONGER NEEDED!!!!!

    The beginning of the OAuth sign-in flow.
    Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


class Patient(View):
    """
    View for patient to check in/edit information/cancel appointment
    # Example user: Harris, 1111
    """
    template_name = 'patient_check_in.html'

    def pull_from_api(self):
        '''
        Pull data from API by creating APIrequest objecy
        '''
        self.new_api_request = APIrequest()
        self.new_api_request.make_api_request()
        self.new_api_request.get_today_appointments()

    def get(self, request, *args, **kwargs):
        '''
        GET request, not used.
        '''
        context = {}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        '''
        POST request

        '''
        context = {}
        # Make API request
        self.pull_from_api()
        
        last_name = ""
        ssn = ""
        appointment = {}

        # Form validation
        name_ssn_form = CheckInNameSSNForm(request.POST)
        if name_ssn_form.is_valid():
            last_name = name_ssn_form.cleaned_data["last_name"]
            # Using str() to conver number/integer field to string
            ssn = str(name_ssn_form.cleaned_data["social_security_number"])
            # Find the patient and his/her appointment
            appointment = self.new_api_request.find_patient(last_name, ssn)
            if appointment:
                context["appointment"] = appointment
        return render(request, self.template_name, context)


class DoctorWelcome(TemplateView):
    """
    View for doctor to 
    see today's appointment/edit appointment info/edit patient info
    """
    template_name = 'doctor_welcome.html'

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)

        # Make API request
        new_api_request = APIrequest()
        new_api_request.make_api_request()

        # Attach API data and send to view
        kwargs['doctor'] = new_api_request.doctors.items()[0][1]
        kwargs["appointments"] = new_api_request.get_today_appointments()
        kwargs["offices"] = new_api_request.offices
        kwargs["wait_time"] = new_api_request.wait_time
        if new_api_request.wait_time:
            kwargs["wait_time_avg"] = \
                new_api_request.wait_time_sum // len(new_api_request.wait_time)
        else:
            kwargs["wait_time_avg"] = None
        return kwargs
