from django.urls import path

from rest_framework_security.sudo.views import StatusView, UpdateStatusView, ExpireNowView


urlpatterns = [
    path('status/', StatusView.as_view(), name='sudo-status'),
    path('update_status/', UpdateStatusView.as_view(), name='sudo-update_status'),
    path('expire_now/', ExpireNowView.as_view(), name='sudo-expire_now'),
]
