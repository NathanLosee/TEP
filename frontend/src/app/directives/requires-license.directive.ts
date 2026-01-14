import {
  Directive,
  TemplateRef,
  ViewContainerRef,
  OnInit,
  OnDestroy,
  inject,
} from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { LicenseService } from '../../services/license.service';

/**
 * Structural directive to hide elements that require an active license
 * Usage: *requiresLicense
 *
 * Elements marked with this directive will only be shown if an active license is present.
 */
@Directive({
  selector: '[requiresLicense]',
  standalone: true,
})
export class RequiresLicenseDirective implements OnInit, OnDestroy {
  private licenseService = inject(LicenseService);
  private templateRef = inject(TemplateRef<any>);
  private viewContainer = inject(ViewContainerRef);
  private destroy$ = new Subject<void>();

  ngOnInit() {
    this.licenseService.isLicensed$()
      .pipe(takeUntil(this.destroy$))
      .subscribe((isLicensed) => {
        this.updateView(isLicensed);
      });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private updateView(isLicensed: boolean) {
    if (isLicensed) {
      // Show the element
      if (this.viewContainer.length === 0) {
        this.viewContainer.createEmbeddedView(this.templateRef);
      }
    } else {
      // Hide the element
      this.viewContainer.clear();
    }
  }
}
