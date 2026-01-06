import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { EmployeeService, Employee, EmployeeBase } from './employee.service';
import { OrgUnit } from './org-unit.service';
import { HolidayGroup } from './holiday-group.service';
import { Department } from './department.service';

describe('EmployeeService', () => {
  let service: EmployeeService;
  let httpMock: HttpTestingController;
  const baseUrl = 'employees';

  // Mock data
  const mockOrgUnit: OrgUnit = {
    id: 1,
    name: 'Engineering'
  };

  const mockHolidayGroup: HolidayGroup = {
    id: 1,
    name: 'US Holidays',
    holidays: []
  };

  const mockDepartment: Department = {
    id: 1,
    name: 'Software Development'
  };

  const mockEmployee: Employee = {
    id: 1,
    badge_number: 'EMP001',
    first_name: 'John',
    last_name: 'Doe',
    payroll_type: 'Salary',
    payroll_sync: 'Manual',
    workweek_type: 'Standard',
    time_type: true,
    allow_clocking: true,
    external_clock_allowed: false,
    allow_delete: true,
    org_unit: mockOrgUnit,
    holiday_group: mockHolidayGroup,
    departments: [mockDepartment]
  };

  const mockEmployeeBase: EmployeeBase = {
    badge_number: 'EMP002',
    first_name: 'Jane',
    last_name: 'Smith',
    payroll_type: 'Hourly',
    payroll_sync: 'Auto',
    workweek_type: 'Standard',
    time_type: false,
    allow_clocking: true,
    external_clock_allowed: true,
    allow_delete: false,
    org_unit_id: 1,
    holiday_group_id: 1
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [EmployeeService]
    });

    service = TestBed.inject(EmployeeService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('getEmployees', () => {
    it('should retrieve all employees', (done) => {
      const mockEmployees: Employee[] = [
        mockEmployee,
        {
          ...mockEmployee,
          id: 2,
          badge_number: 'EMP002',
          first_name: 'Jane',
          last_name: 'Smith'
        }
      ];

      service.getEmployees().subscribe(employees => {
        expect(employees.length).toBe(2);
        expect(employees).toEqual(mockEmployees);
        expect(employees[0].badge_number).toBe('EMP001');
        expect(employees[1].badge_number).toBe('EMP002');
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('GET');
      req.flush(mockEmployees);
    });

    it('should return empty array when no employees exist', (done) => {
      service.getEmployees().subscribe(employees => {
        expect(employees).toEqual([]);
        expect(employees.length).toBe(0);
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush([]);
    });

    it('should handle server errors', (done) => {
      service.getEmployees().subscribe(
        () => fail('should have failed'),
        (error) => {
          expect(error.status).toBe(500);
          done();
        }
      );

      const req = httpMock.expectOne(baseUrl);
      req.flush('Server error', { status: 500, statusText: 'Internal Server Error' });
    });
  });

  describe('getEmployeeById', () => {
    it('should retrieve employee by id', (done) => {
      service.getEmployeeById(1).subscribe(employee => {
        expect(employee).toEqual(mockEmployee);
        expect(employee.id).toBe(1);
        expect(employee.badge_number).toBe('EMP001');
        expect(employee.first_name).toBe('John');
        expect(employee.org_unit).toEqual(mockOrgUnit);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockEmployee);
    });

    it('should handle employee not found', (done) => {
      service.getEmployeeById(999).subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Employee not found', { status: 404, statusText: 'Not Found' });
    });

    it('should retrieve employee with nested manager', (done) => {
      const manager: Employee = {
        ...mockEmployee,
        id: 10,
        badge_number: 'MGR001',
        first_name: 'Manager',
        last_name: 'Boss'
      };

      const employeeWithManager: Employee = {
        ...mockEmployee,
        id: 5,
        manager: manager
      };

      service.getEmployeeById(5).subscribe(employee => {
        expect(employee.manager).toBeDefined();
        expect(employee.manager?.badge_number).toBe('MGR001');
        expect(employee.manager?.first_name).toBe('Manager');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/5`);
      req.flush(employeeWithManager);
    });
  });

  describe('getEmployeeByBadgeNumber', () => {
    it('should retrieve employee by badge number', (done) => {
      service.getEmployeeByBadgeNumber('EMP001').subscribe(employee => {
        expect(employee).toEqual(mockEmployee);
        expect(employee.badge_number).toBe('EMP001');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/badge/EMP001`);
      expect(req.request.method).toBe('GET');
      req.flush(mockEmployee);
    });

    it('should handle badge number not found', (done) => {
      service.getEmployeeByBadgeNumber('INVALID').subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/badge/INVALID`);
      req.flush('Employee not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('getEmployeesByCriteria', () => {
    it('should search by badge number', (done) => {
      service.getEmployeesByCriteria(undefined, undefined, undefined, 'EMP001')
        .subscribe(employees => {
          expect(employees.length).toBe(1);
          expect(employees[0].badge_number).toBe('EMP001');
          done();
        });

      const req = httpMock.expectOne(
        req => req.url === `${baseUrl}/search` && req.params.has('badge_number')
      );
      expect(req.request.params.get('badge_number')).toBe('EMP001');
      req.flush([mockEmployee]);
    });

    it('should search by first name', (done) => {
      service.getEmployeesByCriteria(undefined, undefined, undefined, undefined, 'John')
        .subscribe(employees => {
          expect(employees.length).toBe(1);
          done();
        });

      const req = httpMock.expectOne(
        req => req.url === `${baseUrl}/search` && req.params.has('first_name')
      );
      expect(req.request.params.get('first_name')).toBe('John');
      req.flush([mockEmployee]);
    });

    it('should search by last name', (done) => {
      service.getEmployeesByCriteria(undefined, undefined, undefined, undefined, undefined, 'Doe')
        .subscribe(employees => {
          expect(employees.length).toBe(1);
          done();
        });

      const req = httpMock.expectOne(
        req => req.url === `${baseUrl}/search` && req.params.has('last_name')
      );
      expect(req.request.params.get('last_name')).toBe('Doe');
      req.flush([mockEmployee]);
    });

    it('should search by department name', (done) => {
      service.getEmployeesByCriteria('Engineering')
        .subscribe(employees => {
          expect(employees.length).toBe(1);
          done();
        });

      const req = httpMock.expectOne(
        req => req.url === `${baseUrl}/search` && req.params.has('department_name')
      );
      expect(req.request.params.get('department_name')).toBe('Engineering');
      req.flush([mockEmployee]);
    });

    it('should search by org unit name', (done) => {
      service.getEmployeesByCriteria(undefined, 'Engineering')
        .subscribe(employees => {
          expect(employees.length).toBe(1);
          done();
        });

      const req = httpMock.expectOne(
        req => req.url === `${baseUrl}/search` && req.params.has('org_unit_name')
      );
      expect(req.request.params.get('org_unit_name')).toBe('Engineering');
      req.flush([mockEmployee]);
    });

    it('should search by holiday group name', (done) => {
      service.getEmployeesByCriteria(undefined, undefined, 'US Holidays')
        .subscribe(employees => {
          expect(employees.length).toBe(1);
          done();
        });

      const req = httpMock.expectOne(
        req => req.url === `${baseUrl}/search` && req.params.has('holiday_group_name')
      );
      expect(req.request.params.get('holiday_group_name')).toBe('US Holidays');
      req.flush([mockEmployee]);
    });

    it('should search with multiple criteria', (done) => {
      service.getEmployeesByCriteria('Engineering', 'IT', 'US Holidays', 'EMP001', 'John', 'Doe')
        .subscribe(employees => {
          expect(employees.length).toBe(1);
          done();
        });

      const req = httpMock.expectOne(
        req => req.url === `${baseUrl}/search` &&
               req.params.has('department_name') &&
               req.params.has('org_unit_name') &&
               req.params.has('holiday_group_name') &&
               req.params.has('badge_number') &&
               req.params.has('first_name') &&
               req.params.has('last_name')
      );
      expect(req.request.params.get('department_name')).toBe('Engineering');
      expect(req.request.params.get('org_unit_name')).toBe('IT');
      expect(req.request.params.get('badge_number')).toBe('EMP001');
      req.flush([mockEmployee]);
    });

    it('should return empty array when no matches found', (done) => {
      service.getEmployeesByCriteria(undefined, undefined, undefined, 'NOTFOUND')
        .subscribe(employees => {
          expect(employees).toEqual([]);
          done();
        });

      const req = httpMock.expectOne(
        req => req.url === `${baseUrl}/search`
      );
      req.flush([]);
    });
  });

  describe('createEmployee', () => {
    it('should create new employee', (done) => {
      const createdEmployee: Employee = {
        id: 2,
        ...mockEmployeeBase,
        org_unit: mockOrgUnit,
        holiday_group: mockHolidayGroup
      };

      service.createEmployee(mockEmployeeBase).subscribe(employee => {
        expect(employee).toEqual(createdEmployee);
        expect(employee.id).toBe(2);
        expect(employee.badge_number).toBe('EMP002');
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(mockEmployeeBase);
      req.flush(createdEmployee);
    });

    it('should handle validation errors', (done) => {
      const invalidEmployee: EmployeeBase = {
        ...mockEmployeeBase,
        badge_number: '' // Invalid empty badge number
      };

      service.createEmployee(invalidEmployee).subscribe(
        () => fail('should have failed with 422'),
        (error) => {
          expect(error.status).toBe(422);
          done();
        }
      );

      const req = httpMock.expectOne(baseUrl);
      req.flush('Validation error', { status: 422, statusText: 'Unprocessable Entity' });
    });

    it('should handle duplicate badge number', (done) => {
      service.createEmployee(mockEmployeeBase).subscribe(
        () => fail('should have failed with 409'),
        (error) => {
          expect(error.status).toBe(409);
          done();
        }
      );

      const req = httpMock.expectOne(baseUrl);
      req.flush('Badge number already exists', { status: 409, statusText: 'Conflict' });
    });
  });

  describe('updateEmployee', () => {
    it('should update existing employee', (done) => {
      const updatedEmployee: Employee = {
        ...mockEmployee,
        first_name: 'Updated',
        last_name: 'Name'
      };

      service.updateEmployee(1, mockEmployeeBase).subscribe(employee => {
        expect(employee).toEqual(updatedEmployee);
        expect(employee.first_name).toBe('Updated');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(mockEmployeeBase);
      req.flush(updatedEmployee);
    });

    it('should handle employee not found on update', (done) => {
      service.updateEmployee(999, mockEmployeeBase).subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Employee not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('updateEmployeeBadgeNumber', () => {
    it('should update employee badge number', (done) => {
      const updatedEmployee: Employee = {
        ...mockEmployee,
        badge_number: 'EMP999'
      };

      service.updateEmployeeBadgeNumber(1, 'EMP999').subscribe(employee => {
        expect(employee.badge_number).toBe('EMP999');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1/badge_number`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual({ badge_number: 'EMP999' });
      req.flush(updatedEmployee);
    });

    it('should handle duplicate badge number on update', (done) => {
      service.updateEmployeeBadgeNumber(1, 'EMP002').subscribe(
        () => fail('should have failed with 409'),
        (error) => {
          expect(error.status).toBe(409);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/1/badge_number`);
      req.flush('Badge number already exists', { status: 409, statusText: 'Conflict' });
    });
  });

  describe('deleteEmployee', () => {
    it('should delete employee', (done) => {
      service.deleteEmployee(1).subscribe(() => {
        expect().nothing();
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle employee not found on delete', (done) => {
      service.deleteEmployee(999).subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Employee not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('Employee interface', () => {
    it('should have correct structure with nested objects', () => {
      const employee: Employee = mockEmployee;

      expect(employee.org_unit).toBeDefined();
      expect(employee.org_unit.name).toBe('Engineering');
      expect(employee.holiday_group).toBeDefined();
      expect(employee.holiday_group?.name).toBe('US Holidays');
      expect(employee.departments).toBeDefined();
      expect(employee.departments?.length).toBe(1);
    });

    it('should allow optional manager field', () => {
      const employeeWithManager: Employee = {
        ...mockEmployee,
        manager: mockEmployee
      };

      expect(employeeWithManager.manager).toBeDefined();
      expect(employeeWithManager.manager?.badge_number).toBe('EMP001');
    });

    it('should not have email property', () => {
      const employee: Employee = mockEmployee;
      expect((employee as any).email).toBeUndefined();
    });
  });

  describe('EmployeeBase interface', () => {
    it('should use IDs for relationships', () => {
      const employeeBase: EmployeeBase = mockEmployeeBase;

      expect(employeeBase.org_unit_id).toBeDefined();
      expect(typeof employeeBase.org_unit_id).toBe('number');
      expect(employeeBase.holiday_group_id).toBeDefined();
      expect(typeof employeeBase.holiday_group_id).toBe('number');
    });

    it('should allow optional manager_id', () => {
      const employeeBase: EmployeeBase = {
        ...mockEmployeeBase,
        manager_id: 10
      };

      expect(employeeBase.manager_id).toBe(10);
    });
  });
});
