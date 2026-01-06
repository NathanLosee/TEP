import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { HolidayGroupService, HolidayGroup, Holiday } from './holiday-group.service';
import { Employee } from './employee.service';

describe('HolidayGroupService', () => {
  let service: HolidayGroupService;
  let httpMock: HttpTestingController;
  const baseUrl = 'holiday_groups';

  // Mock data
  const mockRecurringHoliday: Holiday = {
    name: 'New Year\'s Day',
    start_date: new Date('2026-01-01'),
    end_date: new Date('2026-01-01'),
    is_recurring: true,
    recurrence_type: 'fixed',
    recurrence_month: 1,
    recurrence_day: 1,
    recurrence_week: null,
    recurrence_weekday: null
  };

  const mockOneTimeHoliday: Holiday = {
    name: 'Company Anniversary',
    start_date: new Date('2025-03-15'),
    end_date: new Date('2025-03-15'),
    is_recurring: false,
    recurrence_type: null,
    recurrence_month: null,
    recurrence_day: null,
    recurrence_week: null,
    recurrence_weekday: null
  };

  const mockHolidayGroup: HolidayGroup = {
    id: 1,
    name: 'US Holidays',
    holidays: [mockRecurringHoliday, mockOneTimeHoliday]
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [HolidayGroupService]
    });

    service = TestBed.inject(HolidayGroupService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('getHolidayGroups', () => {
    it('should retrieve all holiday groups', (done) => {
      const mockGroups: HolidayGroup[] = [
        mockHolidayGroup,
        {
          id: 2,
          name: 'UK Holidays',
          holidays: [mockRecurringHoliday]
        }
      ];

      service.getHolidayGroups().subscribe(groups => {
        expect(groups.length).toBe(2);
        expect(groups).toEqual(mockGroups);
        expect(groups[0].name).toBe('US Holidays');
        expect(groups[1].name).toBe('UK Holidays');
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('GET');
      req.flush(mockGroups);
    });

    it('should return empty array when no holiday groups exist', (done) => {
      service.getHolidayGroups().subscribe(groups => {
        expect(groups).toEqual([]);
        expect(groups.length).toBe(0);
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush([]);
    });

    it('should handle server errors', (done) => {
      service.getHolidayGroups().subscribe(
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

  describe('getHolidayGroupById', () => {
    it('should retrieve holiday group by id', (done) => {
      service.getHolidayGroupById(1).subscribe(group => {
        expect(group).toEqual(mockHolidayGroup);
        expect(group.id).toBe(1);
        expect(group.name).toBe('US Holidays');
        expect(group.holidays.length).toBe(2);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockHolidayGroup);
    });

    it('should retrieve holiday group with recurring holidays', (done) => {
      const groupWithRecurring: HolidayGroup = {
        id: 1,
        name: 'Federal Holidays',
        holidays: [mockRecurringHoliday]
      };

      service.getHolidayGroupById(1).subscribe(group => {
        expect(group.holidays[0].is_recurring).toBe(true);
        expect(group.holidays[0].recurrence_type).toBe('fixed');
        expect(group.holidays[0].recurrence_month).toBe(1);
        expect(group.holidays[0].recurrence_day).toBe(1);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      req.flush(groupWithRecurring);
    });

    it('should retrieve holiday group with one-time holidays', (done) => {
      const groupWithOneTime: HolidayGroup = {
        id: 2,
        name: 'Special Events',
        holidays: [mockOneTimeHoliday]
      };

      service.getHolidayGroupById(2).subscribe(group => {
        expect(group.holidays[0].is_recurring).toBe(false);
        expect(group.holidays[0].recurrence_type).toBeNull();
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/2`);
      req.flush(groupWithOneTime);
    });

    it('should handle holiday group not found', (done) => {
      service.getHolidayGroupById(999).subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Holiday group not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('getEmployeesByHolidayGroup', () => {
    it('should retrieve employees by holiday group id', (done) => {
      const mockEmployees: Employee[] = [
        {
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
          org_unit: { id: 1, name: 'Engineering', description: '' }
        } as Employee
      ];

      service.getEmployeesByHolidayGroup(1).subscribe(employees => {
        expect(employees.length).toBe(1);
        expect(employees[0].badge_number).toBe('EMP001');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1/employees`);
      expect(req.request.method).toBe('GET');
      req.flush(mockEmployees);
    });

    it('should return empty array when no employees in holiday group', (done) => {
      service.getEmployeesByHolidayGroup(1).subscribe(employees => {
        expect(employees).toEqual([]);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1/employees`);
      req.flush([]);
    });

    it('should handle holiday group not found', (done) => {
      service.getEmployeesByHolidayGroup(999).subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/999/employees`);
      req.flush('Holiday group not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('createHolidayGroup', () => {
    it('should create new holiday group with recurring holidays', (done) => {
      const newGroup: HolidayGroup = {
        name: 'New Holidays',
        holidays: [mockRecurringHoliday]
      };

      const createdGroup: HolidayGroup = {
        id: 3,
        ...newGroup
      };

      service.createHolidayGroup(newGroup).subscribe(group => {
        expect(group).toEqual(createdGroup);
        expect(group.id).toBe(3);
        expect(group.name).toBe('New Holidays');
        expect(group.holidays[0].is_recurring).toBe(true);
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newGroup);
      req.flush(createdGroup);
    });

    it('should create new holiday group with one-time holidays', (done) => {
      const newGroup: HolidayGroup = {
        name: 'Special Events',
        holidays: [mockOneTimeHoliday]
      };

      const createdGroup: HolidayGroup = {
        id: 4,
        ...newGroup
      };

      service.createHolidayGroup(newGroup).subscribe(group => {
        expect(group.holidays[0].is_recurring).toBe(false);
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush(createdGroup);
    });

    it('should create empty holiday group', (done) => {
      const emptyGroup: HolidayGroup = {
        name: 'Empty Group',
        holidays: []
      };

      const createdGroup: HolidayGroup = {
        id: 5,
        ...emptyGroup
      };

      service.createHolidayGroup(emptyGroup).subscribe(group => {
        expect(group.holidays.length).toBe(0);
        done();
      });

      const req = httpMock.expectOne(baseUrl);
      req.flush(createdGroup);
    });

    it('should handle validation errors', (done) => {
      const invalidGroup: HolidayGroup = {
        name: '',
        holidays: []
      };

      service.createHolidayGroup(invalidGroup).subscribe(
        () => fail('should have failed with 422'),
        (error) => {
          expect(error.status).toBe(422);
          done();
        }
      );

      const req = httpMock.expectOne(baseUrl);
      req.flush('Validation error', { status: 422, statusText: 'Unprocessable Entity' });
    });

    it('should handle duplicate name', (done) => {
      service.createHolidayGroup(mockHolidayGroup).subscribe(
        () => fail('should have failed with 409'),
        (error) => {
          expect(error.status).toBe(409);
          done();
        }
      );

      const req = httpMock.expectOne(baseUrl);
      req.flush('Holiday group name already exists', { status: 409, statusText: 'Conflict' });
    });
  });

  describe('updateHolidayGroup', () => {
    it('should update existing holiday group', (done) => {
      const updatedGroup: HolidayGroup = {
        ...mockHolidayGroup,
        name: 'Updated US Holidays'
      };

      service.updateHolidayGroup(1, updatedGroup).subscribe(group => {
        expect(group.name).toBe('Updated US Holidays');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(updatedGroup);
      req.flush(updatedGroup);
    });

    it('should update holidays in group', (done) => {
      const updatedGroup: HolidayGroup = {
        ...mockHolidayGroup,
        holidays: [mockRecurringHoliday]
      };

      service.updateHolidayGroup(1, updatedGroup).subscribe(group => {
        expect(group.holidays.length).toBe(1);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      req.flush(updatedGroup);
    });

    it('should handle holiday group not found on update', (done) => {
      service.updateHolidayGroup(999, mockHolidayGroup).subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Holiday group not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('deleteHolidayGroup', () => {
    it('should delete holiday group', (done) => {
      service.deleteHolidayGroup(1).subscribe(() => {
        expect().nothing();
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle holiday group not found on delete', (done) => {
      service.deleteHolidayGroup(999).subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('Holiday group not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('Holiday interface', () => {
    it('should support recurring fixed holidays', () => {
      const holiday: Holiday = {
        name: 'Christmas',
        start_date: new Date('2025-12-25'),
        end_date: new Date('2025-12-25'),
        is_recurring: true,
        recurrence_type: 'fixed',
        recurrence_month: 12,
        recurrence_day: 25,
        recurrence_week: null,
        recurrence_weekday: null
      };

      expect(holiday.is_recurring).toBe(true);
      expect(holiday.recurrence_type).toBe('fixed');
      expect(holiday.recurrence_month).toBe(12);
      expect(holiday.recurrence_day).toBe(25);
    });

    it('should support recurring relative holidays', () => {
      const holiday: Holiday = {
        name: 'Thanksgiving',
        start_date: new Date('2025-11-27'),
        end_date: new Date('2025-11-27'),
        is_recurring: true,
        recurrence_type: 'relative',
        recurrence_month: 11,
        recurrence_day: null,
        recurrence_week: 4,
        recurrence_weekday: 3 // Thursday
      };

      expect(holiday.is_recurring).toBe(true);
      expect(holiday.recurrence_type).toBe('relative');
      expect(holiday.recurrence_week).toBe(4);
      expect(holiday.recurrence_weekday).toBe(3);
    });

    it('should support one-time holidays', () => {
      const holiday: Holiday = mockOneTimeHoliday;

      expect(holiday.is_recurring).toBe(false);
      expect(holiday.recurrence_type).toBeNull();
      expect(holiday.recurrence_month).toBeNull();
      expect(holiday.recurrence_day).toBeNull();
    });

    it('should support multi-day holidays', () => {
      const holiday: Holiday = {
        name: 'Year-End Closure',
        start_date: new Date('2025-12-26'),
        end_date: new Date('2025-12-31'),
        is_recurring: false,
        recurrence_type: null,
        recurrence_month: null,
        recurrence_day: null,
        recurrence_week: null,
        recurrence_weekday: null
      };

      const duration = (holiday.end_date.getTime() - holiday.start_date.getTime()) / (1000 * 60 * 60 * 24) + 1;
      expect(duration).toBe(6);
    });
  });

  describe('HolidayGroup interface', () => {
    it('should support mixed holiday types', () => {
      const group: HolidayGroup = {
        id: 1,
        name: 'Mixed Holidays',
        holidays: [mockRecurringHoliday, mockOneTimeHoliday]
      };

      expect(group.holidays.length).toBe(2);
      expect(group.holidays[0].is_recurring).toBe(true);
      expect(group.holidays[1].is_recurring).toBe(false);
    });

    it('should allow creation without id', () => {
      const group: HolidayGroup = {
        name: 'New Group',
        holidays: []
      };

      expect(group.id).toBeUndefined();
      expect(group.name).toBe('New Group');
    });
  });
});
