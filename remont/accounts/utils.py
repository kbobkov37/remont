from django_otp import DEVICE_ID_SESSION_KEY


def is_otp_verified(request) -> bool:
    """Проверка 2FA по сессии (работает сразу после login())."""
    return bool(request.session.get(DEVICE_ID_SESSION_KEY))


def user_is_verified(user) -> bool:
    """Проверка 2FA на объекте user (после OTPMiddleware)."""
    check = getattr(user, "is_verified", None)
    if callable(check):
        return check()
    return False
