import {
  Directive,
  Input,
  TemplateRef,
  ViewContainerRef,
  OnInit,
  OnDestroy,
  inject,
  ElementRef,
  Renderer2
} from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { PermissionService } from '../../services/permission.service';

/**
 * Structural directive to show/hide elements based on user permissions
 * Usage: *hasPermission="'employee.read'"
 * Usage with multiple: *hasPermission="['employee.read', 'employee.update']"
 * Usage with mode: *hasPermission="'employee.read'; mode: 'disable'"
 */
@Directive({
  selector: '[hasPermission]',
  standalone: true,
})
export class HasPermissionDirective implements OnInit, OnDestroy {
  private permissionService = inject(PermissionService);
  private templateRef = inject(TemplateRef<any>);
  private viewContainer = inject(ViewContainerRef);
  private destroy$ = new Subject<void>();

  @Input() hasPermission: string | string[] = [];
  @Input() hasPermissionMode: 'hide' | 'disable' = 'hide';
  @Input() hasPermissionRequireAll: boolean = false;

  ngOnInit() {
    this.permissionService.permissions$
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.updateView();
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private updateView() {
    const permissions = Array.isArray(this.hasPermission)
      ? this.hasPermission
      : [this.hasPermission];

    const hasPermission = this.hasPermissionRequireAll
      ? this.permissionService.hasAllPermissions(permissions)
      : this.permissionService.hasAnyPermission(permissions);

    if (this.hasPermissionMode === 'hide') {
      // Hide/show the element
      if (hasPermission) {
        if (this.viewContainer.length === 0) {
          this.viewContainer.createEmbeddedView(this.templateRef);
        }
      } else {
        this.viewContainer.clear();
      }
    } else {
      // Disable the element
      if (this.viewContainer.length === 0) {
        this.viewContainer.createEmbeddedView(this.templateRef);
      }
      // Note: For disable mode, we need to use an attribute directive instead
      // This will be handled by the HasPermissionDisableDirective
    }
  }
}

/**
 * Attribute directive to disable elements based on user permissions
 * Usage: [disableIfNoPermission]="'employee.update'"
 * Usage with multiple: [disableIfNoPermission]="['employee.update', 'employee.delete']"
 */
@Directive({
  selector: '[disableIfNoPermission]',
  standalone: true,
})
export class DisableIfNoPermissionDirective implements OnInit, OnDestroy {
  private permissionService = inject(PermissionService);
  private elementRef = inject(ElementRef);
  private renderer = inject(Renderer2);
  private destroy$ = new Subject<void>();

  @Input() disableIfNoPermission: string | string[] = [];
  @Input() disableIfNoPermissionRequireAll: boolean = false;

  ngOnInit() {
    this.permissionService.permissions$
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => {
        this.updateDisabledState();
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private updateDisabledState() {
    const permissions = Array.isArray(this.disableIfNoPermission)
      ? this.disableIfNoPermission
      : [this.disableIfNoPermission];

    const hasPermission = this.disableIfNoPermissionRequireAll
      ? this.permissionService.hasAllPermissions(permissions)
      : this.permissionService.hasAnyPermission(permissions);

    const element = this.elementRef.nativeElement;

    if (!hasPermission) {
      // Disable the element
      this.renderer.setAttribute(element, 'disabled', 'true');
      this.renderer.addClass(element, 'permission-disabled');
      this.renderer.setStyle(element, 'opacity', '0.5');
      this.renderer.setStyle(element, 'cursor', 'not-allowed');
      this.renderer.setStyle(element, 'pointer-events', 'none');
    } else {
      // Enable the element
      this.renderer.removeAttribute(element, 'disabled');
      this.renderer.removeClass(element, 'permission-disabled');
      this.renderer.removeStyle(element, 'opacity');
      this.renderer.removeStyle(element, 'cursor');
      this.renderer.removeStyle(element, 'pointer-events');
    }
  }
}
