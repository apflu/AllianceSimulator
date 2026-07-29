class ApplicationError(Exception):
    """Base error safe for inbound adapters to translate."""


class NotFoundError(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class ActionNotReadyError(ApplicationError):
    pass
