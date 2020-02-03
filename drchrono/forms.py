from django import forms
from django.forms import widgets

FULL_STATUS_CHOICES = [("Arrived", "Arrived"), ("Checked In", "Checked In"),
                        ("In Room", "In Room"), ("Cancelled", "Cancelled"),
                        ("Complete","Complete"), ("Confirmed", "Confirmed"),
                        ("In Session", "In Session"), ("No Show", "No Show"),
                        ("Not Confirmed", "Not Confirmed"), 
                        ("Rescheduled", "Rescheduled")]
PATIENT_STATUS_CHOICES = [("Checked In", "Checked In"),
                        ("Cancelled", "Cancelled"),]
HOURS_CHOICES = [("1", "1"),("2", "2"),("3", "3"),("4", "4"),("5", "5"),
                ("6", "6"),("7", "7"),("8", "8"),("9", "9"),("10", "10"),
                ("11", "11"),("12", "12")]
MINUTES_CHOICES = [("00", "00"),("15", "15"),("30", "30"),("45", "45")]
AMPM_CHOICES = [("AM", "AM"),("PM", "PM")]
MONTH_CHOICES = [("01", "01"),("02", "02"),("03", "03"),("04", "04"),("05", "05"),
                ("06", "06"),("07", "07"),("08", "08"),("09", "09"),("10", "10"),
                ("11", "11"),("12", "12")]
DAY_CHOICES = [("01", "01"),("02", "02"),("03", "03"),("04", "04"),("05", "05"),
                ("06", "06"),("07", "07"),("08", "08"),("09", "09"),("10", "10"),
                ("11", "11"),("12", "12"),("13", "13"),("14", "14"),("15", "15"),
                ("16", "16"),("17", "17"),("18", "18"),("19", "19"),("20", "20"),
                ("21", "21"),("22", "22"),("23", "23"),("24", "24"),("25", "25"),
                ("26", "26"),("27", "27"),("28", "28"),("29", "29"),("30", "30"),
                ("31", "31"),]
ROLE_CHOICES = [("doctor", "doctor"),("patient", "patient")]
GENDER_CHOICES = [("Male", "Male"),("Female", "Female"), ("Other", "Other")]
ETHNICITY_CHOICES = [("blank", "blank"),("hispanic", "hispanic"),
                    ("not_hispanic", "not_hispanic"), ("declined", "declined")]
RACE_CHOICES = [("blank", "blank"),("indian", "indian"),
                ("asian", "asian"), ("black", "black"),
                ("hawaiian", "hawaiian"), ("white", "white"),
                ("declined", "declined")]

# Add your forms here
class CheckInNameSSNForm(forms.Form):
    last_name = forms.CharField(required=True, label='Last Name', max_length=100)
    social_security_number = forms.IntegerField(required=True, label='Last 4 digits of SSN', max_value=9999, min_value=1)

class ChangeStatusForm(forms.Form):
    appointment = forms.IntegerField(required=True, label='Appointment ID')
    status = forms.ChoiceField(required=True, label='Status', choices=PATIENT_STATUS_CHOICES)

class ChangeAppointmentInfoForm(forms.Form):
    appointment = forms.IntegerField(required=True, label='Appointment ID')
    status = forms.ChoiceField(required=True, label='Status', choices=FULL_STATUS_CHOICES)
    hours = forms.ChoiceField(required=True, label='Hours', choices=HOURS_CHOICES)
    minutes = forms.ChoiceField(required=True, label='Minutes', choices=MINUTES_CHOICES)
    ampm = forms.ChoiceField(required=True, label='AM/PM', choices=AMPM_CHOICES)
    duration = forms.IntegerField(required=True, label='Duration')
    office_exam_room = forms.CharField(required=True, label='Office/Exam Room', max_length=100)
    notes = forms.CharField(required=False, label='Notes', max_length=500)
    reason = forms.CharField(required=False, label='Reason', max_length=500)

class ChangePatientInfoForm(forms.Form):
    patient = forms.IntegerField(required=True, label='Patient ID')
    role = forms.ChoiceField(required=True, label='Role', choices=ROLE_CHOICES)

    first_name = forms.CharField(required=False, label='First Name', max_length=100)
    last_name = forms.CharField(required=False, label='Last Name', max_length=100)
    gender = forms.ChoiceField(required=True, label='Gender', choices=GENDER_CHOICES)
    email = forms.EmailField(required=False, label='Email', max_length=100, min_length=3)
    cell_phone = forms.CharField(required=False, label='Cell Phone', max_length=100)
    ethnicity = forms.ChoiceField(required=True, label='Ethnicity', choices=ETHNICITY_CHOICES)
    race = forms.ChoiceField(required=True, label='Race', choices=RACE_CHOICES)
    address = forms.CharField(required=False, label='Gender', max_length=100)
    city = forms.CharField(required=False, label='City', max_length=100)
    state = forms.CharField(required=False, label='State', max_length=100)
    zip_code = forms.CharField(required=False, label='Zip Code', max_length=100)
    emergency_contact_name = forms.CharField(required=False, label='Name', max_length=100)
    emergency_contact_phone = forms.CharField(required=False, label='Phone', max_length=100)
    emergency_contact_relation = forms.CharField(required=False, label='Relation', max_length=100)
    year = forms.IntegerField(required=False, label='Year', max_value=9999, min_value=1900)
    month = forms.ChoiceField(required=True, label='Month', choices=MONTH_CHOICES)
    day = forms.ChoiceField(required=True, label='Day', choices=DAY_CHOICES)