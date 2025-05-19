import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { FormsModule } from '@angular/forms';
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
      <mat-card>
        <mat-card-title-group>
          <mat-card-title>Timeclock</mat-card-title>
          <mat-card-subtitle>
            <mat-icon>access_time</mat-icon>
            <mat-label>
              {{ currentDateAndTime | date : 'EEEE, MMMM d, yyyy HH:mmaa' }}
            </mat-label>
          </mat-card-subtitle>
        </mat-card-title-group>

        <mat-card-content>
          <mat-form-field>
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
        </mat-card-content>

        <mat-card-actions>
          <button
            mat-raised-button
            (click)="clockInOut()"
            [disabled]="!employeeId"
          >
            Clock In/Out
          </button>

          <button
            mat-raised-button
            (click)="checkStatus()"
            [disabled]="!employeeId"
          >
            Check Status
          </button>
        </mat-card-actions>

        <img mat-card-image src="monteVista.png" />
      </mat-card>
    </div>
  `,
  styles: `
    mat-card {
      width: 100%;
      max-width: 400px;
      padding: 1rem 1rem 0 1rem;
    }

    mat-card > * {
      display: flex;
      flex-direction: column;
      width: 100%;
      padding: 0;
    }

    mat-card-title,
    mat-card-subtitle {
      background-color: var(--sys-tertiary-container);
      color: var(--sys-on-tertiary-container);
      border-radius: 0.5rem;
    }

    mat-card-title,
    mat-card-subtitle,
    mat-card-form-field,
    button {
      width: 100%;
      margin-bottom: 1rem;
      text-align: center;
    }

    mat-icon,
    mat-card-subtitle > mat-label {
      vertical-align: middle;
    }

    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }

    mat-card-actions > .mat-mdc-button-base {
      background-color: var(--sys-tertiary-container);
      color: var(--sys-on-tertiary-container);
    }
    mat-card-actions > .mat-mdc-button-disabled {
      background-color: var(--sys-surface-container);
      color: var(--sys-on-surface-container);
    }
  `,
})
export class ClockerComponent implements OnInit, OnDestroy {
  private clockerService = inject(ClockerService);
  private subscription?: Subscription;

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
          alert(`Employee ID ${this.employeeId} has been ${response.message}`);
          this.employeeId = null; // Clear the input field
        } else {
          alert(`Error: ${response.message}`);
        }
      });
    } else {
      alert('Please enter a valid employee ID');
    }
  }

  /**
   * Check the status of the employee ID
   */
  checkStatus() {
    if (this.employeeId) {
      this.clockerService.checkStatus(this.employeeId).subscribe((response) => {
        console.log(response);
        if (response.status === 'success') {
          alert(
            `Employee ID ${this.employeeId} is currently ${
              response.message ? 'clocked in' : 'clocked out'
            }`
          );
        } else {
          alert(`Error: ${response.message}`);
        }
      });
    } else {
      alert('Please enter a valid employee ID');
    }
  }
}
