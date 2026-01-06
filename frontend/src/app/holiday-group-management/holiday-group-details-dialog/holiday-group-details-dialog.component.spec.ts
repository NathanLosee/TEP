import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { HolidayGroupDetailsDialogComponent } from './holiday-group-details-dialog.component';
import { HolidayGroup } from '../../../services/holiday-group.service';
import { By } from '@angular/platform-browser';

describe('HolidayGroupDetailsDialogComponent', () => {
  let component: HolidayGroupDetailsDialogComponent;
  let fixture: ComponentFixture<HolidayGroupDetailsDialogComponent>;

  const mockDialogRef = jasmine.createSpyObj('MatDialogRef', ['close']);

  const mockHolidayGroupWithRecurring: HolidayGroup = {
    id: 1,
    name: 'US Holidays',
    holidays: [
      {
        name: 'New Year\'s Day',
        start_date: new Date('2026-01-01'),
        end_date: new Date('2026-01-01'),
        is_recurring: true,
        recurrence_type: 'fixed',
        recurrence_month: 1,
        recurrence_day: 1,
        recurrence_week: null,
        recurrence_weekday: null
      },
      {
        name: 'Thanksgiving',
        start_date: new Date('2026-11-26'),
        end_date: new Date('2026-11-26'),
        is_recurring: true,
        recurrence_type: 'relative',
        recurrence_month: 11,
        recurrence_day: null,
        recurrence_week: 4,
        recurrence_weekday: 3 // Thursday
      }
    ]
  };

  const mockHolidayGroupWithOneTime: HolidayGroup = {
    id: 2,
    name: 'Special Events',
    holidays: [
      {
        name: 'Company Anniversary',
        start_date: new Date('2025-03-15'),
        end_date: new Date('2025-03-15'),
        is_recurring: false,
        recurrence_type: null,
        recurrence_month: null,
        recurrence_day: null,
        recurrence_week: null,
        recurrence_weekday: null
      },
      {
        name: 'Summer Conference',
        start_date: new Date('2025-07-10'),
        end_date: new Date('2025-07-12'),
        is_recurring: false,
        recurrence_type: null,
        recurrence_month: null,
        recurrence_day: null,
        recurrence_week: null,
        recurrence_weekday: null
      }
    ]
  };

  function createComponent(holidayGroup: HolidayGroup) {
    TestBed.configureTestingModule({
      imports: [HolidayGroupDetailsDialogComponent],
      providers: [
        { provide: MAT_DIALOG_DATA, useValue: { holidayGroup } },
        { provide: MatDialogRef, useValue: mockDialogRef }
      ]
    });

    fixture = TestBed.createComponent(HolidayGroupDetailsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  describe('component creation', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithRecurring);
    });

    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should display holiday group name in title', () => {
      const titleElement = fixture.debugElement.query(By.css('h2[mat-dialog-title]'));
      expect(titleElement.nativeElement.textContent).toContain('US Holidays');
    });

    it('should have access to holiday group data', () => {
      expect(component.holidayGroup).toEqual(mockHolidayGroupWithRecurring);
    });
  });

  describe('recurring holidays display', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithRecurring);
    });

    it('should display recurring badge for recurring holidays', () => {
      const recurringBadges = fixture.debugElement.queryAll(By.css('.recurring-badge'));
      expect(recurringBadges.length).toBe(2);
    });

    it('should show recurrence pattern for recurring holidays', () => {
      const patterns = fixture.debugElement.queryAll(By.css('.recurrence-pattern'));
      expect(patterns.length).toBe(2);
    });

    it('should display current year date for recurring holidays', () => {
      const currentYearDates = fixture.debugElement.queryAll(By.css('.current-year-date'));
      expect(currentYearDates.length).toBe(2);
    });

    it('should not show one-time date display for recurring holidays', () => {
      const oneTimeDates = fixture.debugElement.queryAll(By.css('.one-time-dates'));
      expect(oneTimeDates.length).toBe(0);
    });
  });

  describe('one-time holidays display', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithOneTime);
    });

    it('should not display recurring badge for one-time holidays', () => {
      const recurringBadges = fixture.debugElement.queryAll(By.css('.recurring-badge'));
      expect(recurringBadges.length).toBe(0);
    });

    it('should show date range for one-time holidays', () => {
      const oneTimeDates = fixture.debugElement.queryAll(By.css('.one-time-dates'));
      expect(oneTimeDates.length).toBe(2);
    });

    it('should display duration chip for one-time holidays', () => {
      const durationChips = fixture.debugElement.queryAll(By.css('.duration-chip'));
      expect(durationChips.length).toBe(2);
    });

    it('should not show recurrence pattern for one-time holidays', () => {
      const patterns = fixture.debugElement.queryAll(By.css('.recurrence-pattern'));
      expect(patterns.length).toBe(0);
    });
  });

  describe('getRecurrenceDescription', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithRecurring);
    });

    it('should return fixed recurrence description', () => {
      const fixedHoliday = mockHolidayGroupWithRecurring.holidays[0];
      const description = component.getRecurrenceDescription(fixedHoliday);
      expect(description).toBe('Every January 1');
    });

    it('should return relative recurrence description', () => {
      const relativeHoliday = mockHolidayGroupWithRecurring.holidays[1];
      const description = component.getRecurrenceDescription(relativeHoliday);
      expect(description).toBe('Fourth Thursday of November');
    });

    it('should return empty string for non-recurring holidays', () => {
      const oneTimeHoliday = mockHolidayGroupWithOneTime.holidays[0];
      const description = component.getRecurrenceDescription(oneTimeHoliday);
      expect(description).toBe('');
    });
  });

  describe('getCurrentYearDate', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithRecurring);
    });

    it('should calculate current year date for fixed recurring holiday', () => {
      const fixedHoliday = mockHolidayGroupWithRecurring.holidays[0];
      const currentYearDate = component.getCurrentYearDate(fixedHoliday);

      expect(currentYearDate).not.toBeNull();
      expect(currentYearDate?.getMonth()).toBe(0); // January
      expect(currentYearDate?.getDate()).toBe(1);
      expect(currentYearDate?.getFullYear()).toBe(component.currentYear);
    });

    it('should calculate current year date for relative recurring holiday', () => {
      const relativeHoliday = mockHolidayGroupWithRecurring.holidays[1];
      const currentYearDate = component.getCurrentYearDate(relativeHoliday);

      expect(currentYearDate).not.toBeNull();
      expect(currentYearDate?.getMonth()).toBe(10); // November
      expect(currentYearDate?.getFullYear()).toBe(component.currentYear);
    });

    it('should return null for non-recurring holidays', () => {
      const oneTimeHoliday = mockHolidayGroupWithOneTime.holidays[0];
      const currentYearDate = component.getCurrentYearDate(oneTimeHoliday);

      expect(currentYearDate).toBeNull();
    });
  });

  describe('getNthWeekdayOfMonth', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithRecurring);
    });

    it('should calculate first weekday of month', () => {
      // First Monday of January 2026
      const date = component['getNthWeekdayOfMonth'](2026, 0, 0, 1);
      expect(date.getDay()).toBe(1); // Monday
      expect(date.getMonth()).toBe(0); // January
      expect(date.getDate()).toBeLessThanOrEqual(7);
    });

    it('should calculate fourth weekday of month', () => {
      // Fourth Thursday of November 2026
      const date = component['getNthWeekdayOfMonth'](2026, 10, 3, 4);
      expect(date.getDay()).toBe(4); // Thursday (JS uses 0=Sunday)
      expect(date.getMonth()).toBe(10); // November
      expect(date.getDate()).toBeGreaterThan(21);
      expect(date.getDate()).toBeLessThanOrEqual(28);
    });

    it('should calculate last weekday of month', () => {
      // Last Monday of May 2026
      const date = component['getNthWeekdayOfMonth'](2026, 4, 0, 5);
      expect(date.getDay()).toBe(1); // Monday
      expect(date.getMonth()).toBe(4); // May
      expect(date.getDate()).toBeGreaterThan(24);
    });
  });

  describe('getDurationDays', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithOneTime);
    });

    it('should calculate 1 day for single-day holiday', () => {
      const singleDayHoliday = mockHolidayGroupWithOneTime.holidays[0];
      const duration = component.getDurationDays(singleDayHoliday);
      expect(duration).toBe(1);
    });

    it('should calculate multiple days for multi-day holiday', () => {
      const multiDayHoliday = mockHolidayGroupWithOneTime.holidays[1];
      const duration = component.getDurationDays(multiDayHoliday);
      expect(duration).toBe(3); // July 10-12 = 3 days
    });

    it('should include both start and end dates in calculation', () => {
      const holiday = {
        name: 'Test',
        start_date: new Date('2025-12-26'),
        end_date: new Date('2025-12-31'),
        is_recurring: false,
        recurrence_type: null,
        recurrence_month: null,
        recurrence_day: null,
        recurrence_week: null,
        recurrence_weekday: null
      };
      const duration = component.getDurationDays(holiday);
      expect(duration).toBe(6); // Dec 26-31 = 6 days
    });
  });

  describe('date handling', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithOneTime);
    });

    it('should handle Date objects in getStartDate', () => {
      const holiday = mockHolidayGroupWithOneTime.holidays[0];
      const startDate = component.getStartDate(holiday);
      expect(startDate instanceof Date).toBe(true);
    });

    it('should handle Date objects in getEndDate', () => {
      const holiday = mockHolidayGroupWithOneTime.holidays[0];
      const endDate = component.getEndDate(holiday);
      expect(endDate instanceof Date).toBe(true);
    });

    it('should handle string dates by converting to Date objects', () => {
      const holiday = {
        name: 'Test',
        start_date: '2025-01-01' as any,
        end_date: '2025-01-01' as any,
        is_recurring: false,
        recurrence_type: null,
        recurrence_month: null,
        recurrence_day: null,
        recurrence_week: null,
        recurrence_weekday: null
      };
      const startDate = component.getStartDate(holiday);
      expect(startDate instanceof Date).toBe(true);
    });
  });

  describe('empty holiday group', () => {
    const emptyHolidayGroup: HolidayGroup = {
      id: 3,
      name: 'Empty Group',
      holidays: []
    };

    beforeEach(() => {
      createComponent(emptyHolidayGroup);
    });

    it('should display no holidays message', () => {
      const noHolidaysElement = fixture.debugElement.query(By.css('.no-holidays'));
      expect(noHolidaysElement).toBeTruthy();
      expect(noHolidaysElement.nativeElement.textContent).toContain('No holidays defined');
    });

    it('should not display holiday items', () => {
      const holidayItems = fixture.debugElement.queryAll(By.css('.holiday-item'));
      expect(holidayItems.length).toBe(0);
    });
  });

  describe('mixed holiday types', () => {
    const mixedHolidayGroup: HolidayGroup = {
      id: 4,
      name: 'Mixed Holidays',
      holidays: [
        {
          name: 'Christmas',
          start_date: new Date('2026-12-25'),
          end_date: new Date('2026-12-25'),
          is_recurring: true,
          recurrence_type: 'fixed',
          recurrence_month: 12,
          recurrence_day: 25,
          recurrence_week: null,
          recurrence_weekday: null
        },
        {
          name: 'Company Event',
          start_date: new Date('2025-06-15'),
          end_date: new Date('2025-06-15'),
          is_recurring: false,
          recurrence_type: null,
          recurrence_month: null,
          recurrence_day: null,
          recurrence_week: null,
          recurrence_weekday: null
        }
      ]
    };

    beforeEach(() => {
      createComponent(mixedHolidayGroup);
    });

    it('should display both recurring and one-time holidays', () => {
      const holidayItems = fixture.debugElement.queryAll(By.css('.holiday-item'));
      expect(holidayItems.length).toBe(2);
    });

    it('should show recurring badge only for recurring holiday', () => {
      const recurringBadges = fixture.debugElement.queryAll(By.css('.recurring-badge'));
      expect(recurringBadges.length).toBe(1);
    });

    it('should show duration chip only for one-time holiday', () => {
      const durationChips = fixture.debugElement.queryAll(By.css('.duration-chip'));
      expect(durationChips.length).toBe(1);
    });
  });

  describe('constants', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithRecurring);
    });

    it('should have weekday names', () => {
      expect(component.weekdayNames.length).toBe(7);
      expect(component.weekdayNames[0]).toBe('Monday');
      expect(component.weekdayNames[6]).toBe('Sunday');
    });

    it('should have week numbers', () => {
      expect(component.weekNumbers.length).toBe(5);
      expect(component.weekNumbers[0]).toBe('First');
      expect(component.weekNumbers[4]).toBe('Last');
    });

    it('should have month names', () => {
      expect(component.monthNames.length).toBe(12);
      expect(component.monthNames[0]).toBe('January');
      expect(component.monthNames[11]).toBe('December');
    });

    it('should have current year', () => {
      expect(component.currentYear).toBe(new Date().getFullYear());
    });
  });

  describe('UI elements', () => {
    beforeEach(() => {
      createComponent(mockHolidayGroupWithRecurring);
    });

    it('should display close button', () => {
      const closeButton = fixture.debugElement.query(By.css('button[mat-dialog-close]'));
      expect(closeButton).toBeTruthy();
      expect(closeButton.nativeElement.textContent).toContain('Close');
    });

    it('should display calendar icon in title', () => {
      const titleIcon = fixture.debugElement.query(By.css('h2[mat-dialog-title] mat-icon'));
      expect(titleIcon).toBeTruthy();
      expect(titleIcon.nativeElement.textContent).toContain('event');
    });

    it('should apply holiday-item styling', () => {
      const holidayItems = fixture.debugElement.queryAll(By.css('.holiday-item'));
      holidayItems.forEach(item => {
        expect(item.nativeElement.classList.contains('holiday-item')).toBe(true);
      });
    });
  });
});
