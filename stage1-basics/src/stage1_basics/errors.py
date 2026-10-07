from __future__ import annotations


class ApiError(Exception):
    pass


class AuthError(ApiError):
    pass


class NotFoundError(ApiError):
    pass


class ServerError(ApiError):
    pass
