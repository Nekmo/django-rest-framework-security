"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/security/allowed_ips/", include("rest_framework_security.allowed_ips.urls")
    ),
    path(
        "api/security/authentication/",
        include("rest_framework_security.authentication.urls"),
    ),
    path(
        "api/security/brute_force_protection/",
        include("rest_framework_security.brute_force_protection.urls"),
    ),
    path("api/security/sudo/", include("rest_framework_security.sudo.urls")),
    path("api/security/otp/", include("rest_framework_security.otp.urls")),
]
