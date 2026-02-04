import { CommonModule } from '@angular/common';
import {
  AfterViewInit,
  Component,
  ContentChildren,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  QueryList,
  SimpleChanges,
  TemplateRef,
  ViewChild,
} from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatTooltipModule } from '@angular/material/tooltip';
import { DisableIfNoPermissionDirective } from '../../../directives/has-permission.directive';
import {
  TableAction,
  TableActionEvent,
  TableColumn,
} from '../../models/table.models';

/**
 * Directive to mark a template for a specific column.
 */
import { Directive, Input as DirectiveInput } from '@angular/core';

@Directive({
  selector: '[appTableCell]',
  standalone: true,
})
export class TableCellDirective {
  @DirectiveInput('appTableCell') columnKey!: string;

  constructor(public templateRef: TemplateRef<any>) {}
}

/**
 * Generic reusable table component.
 * Supports dynamic columns, actions, sorting, and custom cell templates.
 */
@Component({
  selector: 'app-generic-table',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatSortModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    DisableIfNoPermissionDirective,
  ],
  templateUrl: './generic-table.component.html',
  styleUrl: './generic-table.component.scss',
})
export class GenericTableComponent<T = any>
  implements AfterViewInit, OnChanges
{
  /** Data to display - can be array or MatTableDataSource */
  @Input() data: T[] | MatTableDataSource<T> = [];

  /** Column definitions */
  @Input() columns: TableColumn<T>[] = [];

  /** Action button definitions */
  @Input() actions: TableAction<T>[] = [];

  /** Loading state */
  @Input() isLoading = false;

  /** Enable sorting */
  @Input() enableSort = false;

  /** CSS class for the table */
  @Input() tableClass = '';

  /** Empty state icon */
  @Input() emptyIcon = 'inbox';

  /** Empty state title */
  @Input() emptyTitle = 'No data found';

  /** Empty state message */
  @Input() emptyMessage = '';

  /** Show create button on empty state */
  @Input() showCreateOnEmpty = false;

  /** Create button text */
  @Input() createButtonText = 'Create New';

  /** Create button permission */
  @Input() createPermission?: string;

  /** Emitted when an action button is clicked */
  @Output() actionClick = new EventEmitter<TableActionEvent<T>>();

  /** Emitted when create button is clicked */
  @Output() createClick = new EventEmitter<void>();

  @ViewChild(MatSort) sort!: MatSort;

  @ContentChildren(TableCellDirective)
  cellTemplates!: QueryList<TableCellDirective>;

  /** Internal data source for the table */
  tableDataSource = new MatTableDataSource<T>([]);

  /** Map of column key to template - built lazily */
  private templateMap: Map<string, TemplateRef<any>> | null = null;

  ngAfterViewInit() {
    if (this.enableSort && this.sort) {
      this.tableDataSource.sort = this.sort;
    }
    // Template map will be built lazily on first access
  }

  /** Build the template map from ContentChildren - called lazily */
  private buildTemplateMap(): Map<string, TemplateRef<any>> {
    if (this.templateMap === null) {
      this.templateMap = new Map<string, TemplateRef<any>>();
      this.cellTemplates?.forEach((directive) => {
        this.templateMap!.set(directive.columnKey, directive.templateRef);
      });
    }
    return this.templateMap;
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['data']) {
      this.updateDataSource();
    }
  }

  private updateDataSource() {
    if (this.data instanceof MatTableDataSource) {
      this.tableDataSource = this.data;
    } else if (Array.isArray(this.data)) {
      this.tableDataSource.data = this.data;
    }

    // Re-apply sort if enabled
    if (this.enableSort && this.sort) {
      this.tableDataSource.sort = this.sort;
    }
  }

  /** Get displayed column keys including actions */
  get displayedColumnKeys(): string[] {
    const keys = this.columns.map((col) => col.key);
    if (this.actions.length > 0) {
      keys.push('actions');
    }
    return keys;
  }

  /** Check if table is empty */
  get isEmpty(): boolean {
    return this.tableDataSource.data.length === 0;
  }

  /** Get value for a cell */
  getValue(row: T, column: TableColumn<T>): any {
    if (column.getValue) {
      return column.getValue(row);
    }
    return (row as any)[column.key];
  }

  /** Get template for a column */
  getTemplate(key: string): TemplateRef<any> | null {
    return this.buildTemplateMap().get(key) || null;
  }

  /** Handle action button click */
  onActionClick(action: string, row: T, event: Event) {
    event.stopPropagation();
    this.actionClick.emit({ action, row });
  }

  /** Get status class based on status type */
  getStatusClass(row: T, column: TableColumn<T>): string {
    if (column.statusType) {
      const type = column.statusType(row);
      return `status-${type}`;
    }
    return '';
  }

  /** Get status icon */
  getStatusIcon(row: T, column: TableColumn<T>): string {
    if (column.statusIcon) {
      return column.statusIcon(row);
    }
    // Default icons based on status type
    if (column.statusType) {
      const type = column.statusType(row);
      switch (type) {
        case 'success':
          return 'check_circle';
        case 'error':
          return 'cancel';
        case 'warning':
          return 'warning';
        case 'info':
          return 'info';
      }
    }
    return 'circle';
  }
}
