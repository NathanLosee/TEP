import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatToolbarModule } from '@angular/material/toolbar';
import { TimeclockService } from '../../services/timeclock.service';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-timeclock',
  standalone: true,
  imports: [
    DatePipe,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatToolbarModule,
    MatIconModule,
  ],
  templateUrl: './timeclock.component.html',
  styleUrl: './timeclock.component.scss',
})
export class TimeclockComponent implements OnInit, OnDestroy {
  private timeclockService = inject(TimeclockService);
  private subscription?: Subscription;

  currentDateAndTime = Date.now();
  badgeNumber: string | null = null;

  constructor() {
    this.badgeNumber = null;
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
    if (this.badgeNumber) {
      this.timeclockService
        .timeclock(this.badgeNumber)
        .subscribe((response) => {
          console.log(response);
          if (response.status === 'success') {
            alert(`Employee ${this.badgeNumber} has been ${response.message}`);
            this.badgeNumber = null; // Clear the input field
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
    if (this.badgeNumber) {
      this.timeclockService
        .checkStatus(this.badgeNumber)
        .subscribe((response) => {
          console.log(response);
          if (response.status === 'success') {
            alert(
              `Employee ${this.badgeNumber} is currently ${
                response.message ? 'clocked in' : 'clocked out'
              }`
            );
          } else {
            alert(`Error: ${response.message}`);
          }
        });
    } else {
      alert('Please enter a valid employee badge number');
    }
  }
}
