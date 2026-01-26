import { CommonModule } from '@angular/common';
import { Component, inject, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
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
import { MatListModule } from '@angular/material/list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Employee } from '../../../services/employee.service';

export interface ManagerSearchDialogData {
  managers: Employee[];
  currentManagerId?: number | null;
}

@Component({
  selector: 'app-manager-search-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatListModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './manager-search-dialog.component.html',
  styleUrl: './manager-search-dialog.component.scss',
})
export class ManagerSearchDialogComponent implements OnInit {
  private dialogRef = inject(MatDialogRef<ManagerSearchDialogComponent>);
  readonly data = inject<ManagerSearchDialogData>(MAT_DIALOG_DATA);

  searchTerm = '';
  filteredManagers: Employee[] = [];
  selectedManager: Employee | null = null;

  ngOnInit() {
    this.filteredManagers = [...this.data.managers];

    // Pre-select current manager if exists
    if (this.data.currentManagerId) {
      this.selectedManager = this.data.managers.find(
        m => m.id === this.data.currentManagerId
      ) || null;
    }
  }

  onSearchChange() {
    const term = this.searchTerm.toLowerCase().trim();

    if (!term) {
      this.filteredManagers = [...this.data.managers];
      return;
    }

    this.filteredManagers = this.data.managers.filter(manager => {
      const fullName = `${manager.first_name} ${manager.last_name}`.toLowerCase();
      const badge = manager.badge_number.toLowerCase();
      return fullName.includes(term) || badge.includes(term);
    });
  }

  selectManager(manager: Employee) {
    this.selectedManager = manager;
  }

  isSelected(manager: Employee): boolean {
    return this.selectedManager?.id === manager.id;
  }

  clearSelection() {
    this.selectedManager = null;
  }

  confirmSelection() {
    this.dialogRef.close(this.selectedManager);
  }

  cancel() {
    this.dialogRef.close();
  }
}
