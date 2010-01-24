"""Useful exceptions for handlers."""

class HandlerError(Exception):
    pass

class ErrorSignal(HandlerError):
    pass

class RedirectError(HandlerError):
    pass

class PermissionsError(HandlerError):
    pass
