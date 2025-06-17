import { Component, OnInit, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import {
  FormsModule,
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators,
} from "@angular/forms";
import { MatTableModule } from "@angular/material/table";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatInputModule } from "@angular/material/input";
import { MatSelectModule } from "@angular/material/select";
import { MatDialogModule, MatDialog } from "@angular/material/dialog";
import { MatSnackBarModule, MatSnackBar } from "@angular/material/snack-bar";
import { MatChipsModule } from "@angular/material/chips";
import { MatTooltipModule } from "@angular/material/tooltip";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";

interface OrgUnit {
  id: number;
  name: string;
  description?: string;
  employee_count?: number;
  location?: string;
  manager_name?: string;
  employees?: any[];
}

@Component({
  selector: "app-org-unit-management",
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatDialogModule,
    MatSnackBarModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: "./org-unit-management.component.html",
  styleUrl: "./org-unit-management.component.scss",
})
export class OrgUnitManagementComponent implements OnInit {
  private fb = inject(FormBuilder);
  private dialog = inject(MatDialog);
  private snackBar = inject(MatSnackBar);

  orgUnits: OrgUnit[] = [];
  filteredOrgUnits: OrgUnit[] = [];
  displayedColumns: string[] = [
    "name",
    "location",
    "employee_count",
    "manager",
    "actions",
  ];

  searchForm: FormGroup;
  addOrgUnitForm: FormGroup;
  editForm: FormGroup;
  isLoading = false;
  showAddForm = false;
  showEditForm = false;
  showEmployeeList = false;
  selectedOrgUnit: OrgUnit | null = null;

  constructor() {
    this.searchForm = this.fb.group({
      searchTerm: [""],
      location: [""],
    });

    this.addOrgUnitForm = this.fb.group({
      name: ["", [Validators.required, Validators.minLength(2)]],
      description: [""],
      location: [""],
      manager_name: [""],
    });

    this.editForm = this.fb.group({
      name: ["", [Validators.required, Validators.minLength(2)]],
      description: [""],
      location: [""],
      manager_name: [""],
    });
  }

  ngOnInit() {
    this.loadOrgUnits();
    this.setupSearchForm();
  }

  setupSearchForm() {
    this.searchForm.valueChanges.subscribe(() => {
      this.filterOrgUnits();
    });
  }

  loadOrgUnits() {
    this.isLoading = true;
    // Simulate API call - replace with actual service call
    setTimeout(() => {
      this.orgUnits = this.generateMockOrgUnits();
      this.filteredOrgUnits = [...this.orgUnits];
      this.isLoading = false;
    }, 1000);
  }

  filterOrgUnits() {
    const filters = this.searchForm.value;

    this.filteredOrgUnits = this.orgUnits.filter((unit) => {
      const searchTerm = filters.searchTerm?.toLowerCase() || "";
      const matchesSearch =
        !searchTerm ||
        unit.name.toLowerCase().includes(searchTerm) ||
        unit.description?.toLowerCase().includes(searchTerm) ||
        unit.location?.toLowerCase().includes(searchTerm);

      const matchesLocation =
        !filters.location ||
        unit.location?.toLowerCase().includes(filters.location.toLowerCase());

      return matchesSearch && matchesLocation;
    });
  }

  toggleAddForm() {
    this.showAddForm = !this.showAddForm;
    if (!this.showAddForm) {
      this.addOrgUnitForm.reset();
    }
  }

  addOrgUnit() {
    if (this.addOrgUnitForm.valid) {
      const formValue = this.addOrgUnitForm.value;
      const newOrgUnit: OrgUnit = {
        id: this.orgUnits.length + 1,
        name: formValue.name,
        description: formValue.description,
        location: formValue.location,
        manager_name: formValue.manager_name,
        employee_count: 0,
      };

      this.orgUnits.push(newOrgUnit);
      this.filterOrgUnits();
      this.addOrgUnitForm.reset();
      this.showAddForm = false;
      this.showSnackBar(
        `Org Unit "${newOrgUnit.name}" created successfully`,
        "success",
      );
    }
  }

  // Action methods for buttons
  viewEmployees(orgUnit: OrgUnit) {
    this.selectedOrgUnit = orgUnit;
    this.showEmployeeList = true;
    this.showEditForm = false;
  }

  editOrgUnit(orgUnit: OrgUnit) {
    this.selectedOrgUnit = orgUnit;
    this.showEditForm = true;
    this.showEmployeeList = false;

    // Initialize edit form with org unit data
    this.editForm.patchValue({
      name: orgUnit.name,
      description: orgUnit.description || "",
      location: orgUnit.location || "",
      manager_name: orgUnit.manager_name || "",
    });
  }

  deleteOrgUnit(orgUnit: OrgUnit) {
    const confirmDelete = confirm(
      `Are you sure you want to delete ${orgUnit.name}? This action cannot be undone.`,
    );

    if (confirmDelete) {
      this.isLoading = true;

      // Remove org unit from the array (simulating API call)
      setTimeout(() => {
        const index = this.orgUnits.findIndex((unit) => unit.id === orgUnit.id);
        if (index > -1) {
          this.orgUnits.splice(index, 1);
          this.filterOrgUnits();
          this.showSnackBar(
            `${orgUnit.name} has been deleted successfully`,
            "success",
          );
        }
        this.isLoading = false;
      }, 1000);
    }
  }

  saveOrgUnit() {
    if (this.editForm && this.editForm.valid && this.selectedOrgUnit) {
      this.isLoading = true;

      const formData = this.editForm.value;

      // Update org unit data (simulating API call)
      setTimeout(() => {
        const index = this.orgUnits.findIndex(
          (unit) => unit.id === this.selectedOrgUnit!.id,
        );
        if (index > -1) {
          this.orgUnits[index] = {
            ...this.orgUnits[index],
            name: formData.name,
            description: formData.description,
            location: formData.location,
            manager_name: formData.manager_name,
          };
          this.filterOrgUnits();
          this.showSnackBar("Org Unit updated successfully", "success");
          this.cancelAction();
        }
        this.isLoading = false;
      }, 1000);
    }
  }

  cancelAction() {
    this.showEditForm = false;
    this.showEmployeeList = false;
    this.selectedOrgUnit = null;
    this.editForm?.reset();
  }

  // Statistics methods
  getTotalEmployees(): number {
    return this.orgUnits.reduce(
      (total, unit) => total + (unit.employee_count || 0),
      0,
    );
  }

  getTotalLocations(): number {
    const locations = new Set(
      this.orgUnits.map((unit) => unit.location).filter((loc) => loc),
    );
    return locations.size;
  }

  getUniqueLocations(): number {
    return this.getTotalLocations();
  }

  private showSnackBar(
    message: string,
    type: "success" | "error" | "info" = "info",
  ) {
    this.snackBar.open(message, "Close", {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }

  private generateMockOrgUnits(): OrgUnit[] {
    return [
      {
        id: 1,
        name: "Corporate Office",
        description: "Main corporate office",
        location: "New York",
        manager_name: "John Smith",
        employee_count: 15,
      },
      {
        id: 2,
        name: "Manufacturing Plant",
        description: "Production facility",
        location: "Detroit",
        manager_name: "Jane Doe",
        employee_count: 25,
      },
      {
        id: 3,
        name: "IT Department",
        description: "Information Technology",
        location: "New York",
        manager_name: "Mike Johnson",
        employee_count: 12,
      },
      {
        id: 4,
        name: "Quality Control",
        description: "Quality assurance team",
        location: "Detroit",
        manager_name: "Sarah Wilson",
        employee_count: 8,
      },
      {
        id: 5,
        name: "Sales & Marketing",
        description: "Sales and marketing division",
        location: "Chicago",
        manager_name: "Tom Brown",
        employee_count: 10,
      },
      {
        id: 6,
        name: "Research & Development",
        description: "Product development",
        location: "San Francisco",
        manager_name: "Lisa Anderson",
        employee_count: 18,
      },
    ];
  }
}
