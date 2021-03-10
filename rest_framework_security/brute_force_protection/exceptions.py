class BruteForceProtectionException(Exception):
    pass


class BruteForceProtectionBanException(BruteForceProtectionException):
    pass


class BruteForceProtectionCaptchaException(BruteForceProtectionException):
    pass
