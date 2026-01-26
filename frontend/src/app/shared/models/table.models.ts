/**
 * Generic table models for reusable table component.
 */

/**
 * Column definition for the generic table.
 * @template T - The type of data row
 */
export interface TableColumn<T = any> {
  /** Property name or unique key for this column */
  key: string;

  /** Display header text */
  header: string;

  /** Column rendering type */
  type:
    | 'text'
    | 'chip'
    | 'chip-list'
    | 'icon-text'
    | 'status'
    | 'date'
    | 'template';

  /** Enable sorting for this column */
  sortable?: boolean;

  /** Custom value extractor function */
  getValue?: (row: T) => any;

  /** Icon name for icon-text type */
  icon?: string;

  /** Dynamic chip class function */
  chipClass?: (row: T) => string;

  /** Date format string for date type */
  dateFormat?: string;

  /** Status type for status column (success, error, warning, info) */
  statusType?: (row: T) => 'success' | 'error' | 'warning' | 'info';

  /** Status icon for status column */
  statusIcon?: (row: T) => string;
}

/**
 * Action button definition for table rows.
 * @template T - The type of data row
 */
export interface TableAction<T = any> {
  /** Material icon name */
  icon: string;

  /** Tooltip text */
  tooltip: string;

  /** Action identifier emitted on click */
  action: string;

  /** Required permission (uses disableIfNoPermission directive) */
  permission?: string;

  /** Button color */
  color?: 'primary' | 'accent' | 'warn';

  /** Dynamic disabled state function */
  disabled?: (row: T) => boolean;

  /** CSS class for the button */
  class?: string;
}

/**
 * Event emitted when an action button is clicked.
 * @template T - The type of data row
 */
export interface TableActionEvent<T = any> {
  /** Action identifier */
  action: string;

  /** The row data */
  row: T;
}
