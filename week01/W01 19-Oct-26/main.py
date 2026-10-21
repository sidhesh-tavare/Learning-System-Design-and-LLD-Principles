from employee_composition import *

def main():
    Asha = Employee(name = "Asha" , role = Manager , employment=FullTime , pay = 70000)
    Rahul = Employee(name = "Rahul" , role = Engineer , employment=Contractual , pay = 40000)
    Seema = Employee(name = "Seema" , role = Intern , pay = 20000 , employment=PartTime)

    emps = [Asha,Rahul,Seema]
    for emp in emps:
        print(f"Name : {emp.name}\n Pay : {emp.employment.calculate_pay()} \n Approve Leave : {emp.role.can_aprove_leave()}\nEligible for leave : {emp.employment.eligible_for_leave()}")

if __name__ == "__main__":
    main()
