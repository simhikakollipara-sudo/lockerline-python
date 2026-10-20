"""Domain errors and problem+json definitions."""

PROBLEM = "application/problem+json"


class DomainError(Exception):
    status: int = 400
    type: str = "/errors/domain"
    title: str = "Refused"

    def __init__(self, detail: str, **extra):
        super().__init__(detail)
        self.detail = detail
        self.extra = extra


class NoSuchTower(DomainError):
    status, type, title = 404, "/errors/no-such-tower", "No such tower"


class NoSuchDoor(DomainError):
    status, type, title = 404, "/errors/no-such-door", "No such door"


class NoSuchParcel(DomainError):
    status, type, title = 404, "/errors/no-such-parcel", "No such parcel"


class NoSuchFlat(DomainError):
    status, type, title = 400, "/errors/no-such-flat", "No such flat in this tower"


class NoDoorFree(DomainError):
    status, type, title = 409, "/errors/no-door-free", "No free door of that size"


# (status, type, title) of the errors that are not domain refusals
VALIDATION_BODY = (422, "/errors/validation", "The request body is not valid")
VALIDATION_PARAMS = (400, "/errors/validation", "Invalid query parameter")

NOT_FOUND = (404, "/errors/not-found", "No such resource")
METHOD_NOT_ALLOWED = (405, "/errors/method-not-allowed", "Method not allowed")
HTTP = (500, "/errors/http", "Internal server error")