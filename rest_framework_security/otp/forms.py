from django import forms

from rest_framework_security.otp.models import OTPDevice


class SelectOTPDeviceForm(forms.Form):
    otp_device = forms.ModelChoiceField(OTPDevice.objects.all())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SelectOTPDeviceForm, self).__init__(*args, **kwargs)
        self.fields['otp_device'].queryset = self.fields['otp_device'].queryset.filter(user=user)
