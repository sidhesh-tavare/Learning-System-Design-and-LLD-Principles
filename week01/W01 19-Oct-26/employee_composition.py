
from abc import ABC, abstractmethod
from dataclasses import dataclass


# 1. Role abstraction
class Role(ABC):

    @abstractmethod
    def can_approve_leave(self) -> bool:
        pass


class Engineer(Role):
    def can_approve_leave(self) -> bool:
        return False


class Manager(Role):
    def can_approve_leave(self) -> bool:
        return True


class Intern(Role):
    def can_approve_leave(self) -> bool:
        return False


# 2. Employment type abstraction
class EmploymentType(ABC):

    @abstractmethod
    def calculate_pay(self, base_pay: float) -> float:
        pass

    def eligible_for_leave(self) -> bool:
        return True


class FullTime(EmploymentType):

    def calculate_pay(self, base_pay: float) -> float:
        return base_pay * 1.0


class PartTime(EmploymentType):

    def calculate_pay(self, base_pay: float) -> float:
        return base_pay * 0.7


class Contractual(EmploymentType):

    def calculate_pay(self, base_pay: float) -> float:
        return base_pay * 0.5

    def eligible_for_leave(self) -> bool:
        return False

class Director(Role):
    def can_approve_leave(self):
        return True 

class Freelancer(EmploymentType):

    def calculate_pay(self, base_pay):
        return super().calculate_pay(base_pay)


# 3. Employee composes Role and EmploymentType
@dataclass
class Employee:
    name: str
    role: Role
    employment: EmploymentType
    pay: float

    def can_approve_leave(self) -> bool:
        return self.role.can_approve_leave() 

    def calculate_pay(self) -> float:
        return self.employment.calculate_pay(self.pay)

    def eligible_for_leave(self) -> bool:
        return self.employment.eligible_for_leave()


# 4. Usage
if __name__ == "__main__":
    emp1 = Employee(
        "Sid",
        Engineer(),
        FullTime(),
        50000
    )

    emp2 = Employee(
        "Alex",
        Manager(),
        Contractual(),
        50000
    )

    print(emp1.name, emp1.calculate_pay())
    print("Can approve leave:", emp1.can_approve_leave())
    print("Eligible for leave:", emp1.eligible_for_leave())

    print()

    print(emp2.name, emp2.calculate_pay())
    print("Can approve leave:", emp2.can_approve_leave())
    print("Eligible for leave:", emp2.eligible_for_leave())
