import { Component } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatIconModule,
    FormsModule,
  ],
  template: `
    <div class="login-container">
      <mat-card>
        <mat-card-title-group>
          <mat-card-title>Admin Login</mat-card-title>
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
          <mat-form-field>
            <mat-label>Password</mat-label>
            <input
              matInput
              name="password"
              type="password"
              required="true"
              [(ngModel)]="password"
            />
            @if (password) {
            <button
              matSuffix
              mat-icon-button
              aria-label="Clear"
              (click)="password = null"
            >
              <mat-icon>close</mat-icon>
            </button>
            }
          </mat-form-field>
        </mat-card-content>

        <mat-card-actions>
          <button mat-raised-button [disabled]="!employeeId || !password">
            Login
          </button>
        </mat-card-actions>
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

    mat-card-title {
      background-color: var(--sys-tertiary-container);
      color: var(--sys-on-tertiary-container);
      border-radius: 0.5rem;
    }

    mat-card-title,
    mat-card-form-field,
    button {
      width: 100%;
      margin-bottom: 1rem;
      text-align: center;
    }

    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }

    .mat-mdc-button-base {
      background-color: var(--sys-tertiary-container);
      color: var(--sys-on-tertiary-container);
    }
    .mat-mdc-button-disabled {
      background-color: var(--sys-surface-container);
      color: var(--sys-on-surface-container);
    }
  `,
})
export class LoginComponent {
  employeeId: number | null = null;
  password: string | null = null;
}
