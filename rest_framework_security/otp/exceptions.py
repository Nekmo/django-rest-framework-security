class OTPException(Exception):
    pass


class OTPDevicesRequiredException(OTPException):
    pass


class OTPStaticTokensAlreadyExistsException(OTPException):
    pass
