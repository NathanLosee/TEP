import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { RouterModule } from '@angular/router';
import { HasPermissionDirective } from '../directives/has-permission.directive';
import { PasswordChangeDialogComponent } from '../password-change-dialog/password-change-dialog.component';
import { UserService } from '../../services/user.service';

@Component({
  selector: 'app-nav-admin',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbarModule,
    MatButtonModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatTooltipModule,
    MatDialogModule,
    MatSnackBarModule,
    RouterModule,
    HasPermissionDirective,
  ],
  templateUrl: './nav-admin.component.html',
  styleUrl: './nav-admin.component.scss',
})
export class NavAdminComponent {
  private dialog = inject(MatDialog);
  private userService = inject(UserService);
  private snackBar = inject(MatSnackBar);

  openPasswordChangeDialog() {
    const currentBadge = this.userService.getCurrentUserBadge();
    if (!currentBadge) {
      this.showSnackBar('Unable to determine current user', 'error');
      return;
    }

    const dialogRef = this.dialog.open(PasswordChangeDialogComponent, {
      width: '500px',
      data: {
        badgeNumber: currentBadge,
        isAdmin: false, // User changing their own password
      },
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.showSnackBar('Password changed successfully', 'success');
      }
    });
  }

  private showSnackBar(
    message: string,
    type: 'success' | 'error' | 'info' = 'info'
  ) {
    this.snackBar.open(message, 'Close', {
      duration: 4000,
      panelClass: [`snack-${type}`],
    });
  }
}
