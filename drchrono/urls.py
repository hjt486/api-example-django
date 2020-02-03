from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^welcome/$', views.DoctorWelcome.as_view(), name='welcome'),
    url(r'^patient/$', views.Patient.as_view(), name='patient'),
    url(r'^change_status/$',
        views.ChangeStatus.as_view(), name='change_status'),
    url(r'^change_appointment_info/$',
        views.ChangeAppointmentInfo.as_view(), name='change_appointment_info'),
    url(r'^change_patient_info/$',
        views.ChangePatientInfo.as_view(), name='change_patient_info'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',
        TemplateView.as_view(template_name='homepage.html'),name='homepage'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)