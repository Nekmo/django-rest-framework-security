from django.urls import path

from rest_framework_sudo.views import StatusView, UpdateStatusView, ExpireNowView

urlpatterns = [
    path('status/', StatusView.as_view()),
    path('update_status/', UpdateStatusView.as_view()),
    path('expire_now/', ExpireNowView.as_view()),
]
