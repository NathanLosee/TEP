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
import { OrgUnit } from '../../../services/org-unit.service';

export interface OrgUnitFormDialogData {
  editOrgUnit?: OrgUnit | null;
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
  private formBuilder = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<OrgUnitFormDialogComponent>);
  readonly data = inject<OrgUnitFormDialogData>(MAT_DIALOG_DATA);

  orgUnitForm: FormGroup;
  isEditMode = false;
  isLoading = false;

  constructor() {
    this.orgUnitForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      holidays: this.formBuilder.array([]),
    });

    if (this.data.editOrgUnit) {
      this.isEditMode = true;
      this.orgUnitForm = this.formBuilder.group({
        name: [this.data.editOrgUnit.name, [Validators.required]],
      });
    }
  }

  getFormData(): OrgUnit {
    return {
      name: this.orgUnitForm.get('name')?.value,
    };
  }

  submitForm() {
    if (this.orgUnitForm.valid) {
      const formData = this.getFormData();
      if (this.data.editOrgUnit) {
        formData.id = this.data.editOrgUnit.id;
      }
      this.dialogRef.close(formData);
    }
  }

  cancelForm() {
    this.dialogRef.close();
  }
}
