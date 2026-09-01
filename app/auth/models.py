from dataclasses import dataclass


class Roles:
    EMPLOYEE = "EMPLOYEE"
    HR = "HR"
    ADMIN = "ADMIN"

    ALL = {
        EMPLOYEE,
        HR,
        ADMIN,
    }


@dataclass
class User:
    id: str
    username: str
    role: str