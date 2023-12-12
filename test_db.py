from DbModels import Employee

for i in Employee.get_all_employee():
    print(i.name, i.email)

print(Employee.get_employee_by_id(1).name)
print(Employee.get_employee_by_email('john@g.com').name)
