import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { FormGroup, FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { ClockerService } from './clocker.service';
import { interval, Subscription } from 'rxjs';

@Component({
    selector: 'app-clocker',
    imports: [
        DatePipe,
        MatFormFieldModule,
        MatInputModule,
        FormsModule,
        MatButtonModule,
        MatCardModule,
        MatIconModule,
    ],
    template: `
    <div class="clocker-container">
      <mat-card class="clocker-card">
        <mat-card class="title-card">
          <mat-card class="time-card">
            <mat-icon>access_time</mat-icon>
            <mat-label>
              {{ currentDateAndTime | date : 'EEEE, MMMM d, yyyy HH:mmaa' }}
            </mat-label>
          </mat-card>
          <h1 class="mat-h1">Timeclock</h1>
        </mat-card>
        <form>
          <mat-form-field class="full-width">
            <mat-label>Employee ID</mat-label>
            <input
              matInput
              name="employeeId"
              type="number"
              required="true"
              [(ngModel)]="employeeId"
            />
            @if (employeeId) {
            <button
              matSuffix
              mat-icon-button
              aria-label="Clear"
              (click)="employeeId = null"
            >
              <mat-icon>close</mat-icon>
            </button>
            }
          </mat-form-field>

          <button
            class="full-width"
            mat-raised-button
            (click)="clockInOut()"
            [disabled]="!employeeId"
          >
            Clock In/Out
          </button>

          <button class="full-width" mat-raised-button [disabled]="!employeeId">
            Check Status
          </button>
        </form>
      </mat-card>
    </div>
  `,
    styles: `
    :host {
      background: var(--mat-sys-background);
      background-color: var(--mat-sys-surface);
      color: #000000;
    }

    .clocker-container {
      display: flex;
      background-color: var(--mat-sys-surface);
      color: #000000;
      justify-content: center;
      align-items: center;
      height: 100vh;
      width: 100%;
    }

    .clocker-card {
      width: 100%;
      max-width: 400px;
      padding: 2rem;
    }

    .time-card {
      width: 100%;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    .title-card {
      width: 100%;
      margin-bottom: 1rem;
      background-color: var(--mat-sys-surface-container-highest);
      display: flex;
      justify-content: center;
      align-items: center;
    }

    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }
  `
})
export class ClockerComponent implements OnInit, OnDestroy {
  private clockerService = inject(ClockerService);
  private subscription?: Subscription;
  clockerForm!: FormGroup;

  currentDateAndTime = Date.now();
  employeeId: number | null = null;

  constructor() {
    this.employeeId = null;
  }

  ngOnInit() {
    // Update the current date and time every second
    const timer = interval(1000);
    this.subscription = timer.subscribe(() => {
      this.currentDateAndTime = Date.now();
    });
  }

  ngOnDestroy() {
    // Unsubscribe from the timer to prevent memory leaks
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  /**
   * Clock in/out for the employee ID
   */
  clockInOut() {
    if (this.employeeId) {
      this.clockerService.timeclock(this.employeeId).subscribe((response) => {
        console.log(response);
        if (response.status === 'success') {
          alert(
            `Employee ID ${this.employeeId} has been ${
              response.message ? 'clocked in' : 'clocked out'
            }`
          );
          this.employeeId = null; // Clear the input field
        } else {
          alert(`Error: ${response.message}`);
        }
      });
    } else {
      alert('Please enter a valid employee ID');
    }
  }
}
