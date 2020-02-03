from django import forms
from django.forms import widgets


# Add your forms here
class CheckInNameSSNForm(forms.Form):
    last_name = forms.CharField(required=True, label='Last Name', max_length=100)
    social_security_number = forms.CharField(required=True, label='Last 4 digits of SSN', max_length=4, min_length=4)

class ChangeStatusForm(forms.Form):
    appointment = forms.CharField(required=True, label='Appointment ID', max_length=100)
    status = forms.CharField(required=True, label='Status', max_length=100)

class ChangeAppointmentInfoForm(forms.Form):
    appointment = forms.CharField(required=True, label='Appointment ID', max_length=100)
    status = forms.CharField(required=False, label='Status', max_length=100)
    hours = forms.CharField(required=True, label='Hours', max_length=2)
    minutes = forms.CharField(required=True, label='Minuts', max_length=2)
    ampm = forms.CharField(required=True, label='AM/PM', max_length=2)
    duration = forms.CharField(required=True, label='Duration', max_length=3)
    office_exam_room = forms.CharField(required=True, label='Office/Exam Room', max_length=100)
    notes = forms.CharField(required=False, label='Notes', max_length=500)
    reason = forms.CharField(required=False, label='Reason', max_length=500)

class ChangePatientInfoForm(forms.Form):
    patient = forms.CharField(required=True, label='Patient ID', max_length=100)
    role = forms.CharField(required=False, label='Role', max_length=100)

    first_name = forms.CharField(required=False, label='First Name', max_length=100)
    last_name = forms.CharField(required=False, label='Last Name', max_length=100)
    gender = forms.CharField(required=True, label='Gender', max_length=6)
    email = forms.CharField(required=False, label='Gender', max_length=100)
    cell_phone = forms.CharField(required=False, label='Cell Phone', max_length=100)
    ethnicity = forms.CharField(required=False, label='Ethnicity', max_length=100)
    race = forms.CharField(required=False, label='Race', max_length=100)
    address = forms.CharField(required=False, label='Gender', max_length=100)
    city = forms.CharField(required=False, label='City', max_length=100)
    state = forms.CharField(required=False, label='State', max_length=100)
    zip_code = forms.CharField(required=False, label='Zip Code', max_length=100)
    emergency_contact_name = forms.CharField(required=False, label='Name', max_length=100)
    emergency_contact_phone = forms.CharField(required=False, label='Phone', max_length=100)
    emergency_contact_relation = forms.CharField(required=False, label='Relation', max_length=100)
    year = forms.CharField(required=False, label='Year', max_length=100)
    month = forms.CharField(required=False, label='Month', max_length=100)
    day = forms.CharField(required=False, label='Day', max_length=100)