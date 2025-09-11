import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import {
  MAT_DIALOG_DATA,
  MatDialogActions,
  MatDialogContent,
  MatDialogRef,
  MatDialogTitle,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { OrgUnit, OrgUnitService } from '../../../services/org-unit.service';

export interface OrgUnitFormDialogData {
  editOrgUnit?: OrgUnit | null;
  orgUnits?: OrgUnit[]; // For parent selection
}

@Component({
  selector: 'app-org-unit-form-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatSelectModule,
  ],
  templateUrl: './org-unit-form-dialog.component.html',
  styleUrl: './org-unit-form-dialog.component.scss',
})
export class OrgUnitFormDialogComponent {
  private fb = inject(FormBuilder);
  private orgUnitService = inject(OrgUnitService);
  private dialogRef = inject(MatDialogRef<OrgUnitFormDialogComponent>);
  public data = inject(MAT_DIALOG_DATA) as OrgUnitFormDialogData;

  orgUnitForm!: FormGroup;
  isLoading = false;
  isEditMode = false;

  orgUnits: OrgUnit[] = [];

  constructor() {
    this.isEditMode = !!this.data.editOrgUnit;
    this.initializeForm();
    this.loadFormData();
  }

  private initializeForm() {
    this.orgUnitForm = this.fb.group({
      name: [
        this.data.editOrgUnit?.name || '',
        [Validators.required],
      ],
    });
  }

  private loadFormData() {
    this.orgUnits = this.data.orgUnits || [];
  }

  get availableParents() {
    // Filter out the current org unit to prevent circular references
    if (this.isEditMode && this.data.editOrgUnit) {
      return this.orgUnits.filter(unit => unit.id !== this.data.editOrgUnit!.id);
    }
    return this.orgUnits;
  }

  submitForm() {
    if (this.orgUnitForm.valid) {
      this.isLoading = true;

      const orgUnitData = this.orgUnitForm.value;

      if (this.isEditMode && this.data.editOrgUnit) {
        this.orgUnitService
          .updateOrgUnit(this.data.editOrgUnit.id!, orgUnitData)
          .subscribe({
            next: (updatedOrgUnit) => {
              this.dialogRef.close(updatedOrgUnit);
              this.isLoading = false;
            },
            error: (error) => {
              console.error('Error updating org unit:', error);
              this.isLoading = false;
            },
          });
      } else {
        this.orgUnitService.createOrgUnit(orgUnitData).subscribe({
          next: (newOrgUnit) => {
            this.dialogRef.close(newOrgUnit);
            this.isLoading = false;
          },
          error: (error) => {
            console.error('Error creating org unit:', error);
            this.isLoading = false;
          },
        });
      }
    }
  }

  cancelForm() {
    this.dialogRef.close();
  }
}