import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';

export interface ReleaseInfo {
  version: string;
  tag_name: string;
  published_at: string;
  release_notes: string;
  download_url: string;
  asset_name: string;
  asset_size: number;
}

export interface UpdateStatus {
  current_version: string;
  latest_version: string | null;
  update_available: boolean;
  last_checked: string | null;
  download_progress: number | null;
  downloaded_file: string | null;
  state: 'idle' | 'checking' | 'downloading' | 'ready' | 'applying' | 'error';
  error: string | null;
  backup_available: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class UpdateService {
  private readonly baseUrl = '/updater';
  private updateAvailableSubject = new BehaviorSubject<boolean>(false);
  private statusSubject = new BehaviorSubject<UpdateStatus | null>(null);

  updateAvailable$ = this.updateAvailableSubject.asObservable();
  status$ = this.statusSubject.asObservable();

  constructor(private http: HttpClient) {}

  checkForUpdate(): Observable<ReleaseInfo> {
    return this.http.get<ReleaseInfo>(`${this.baseUrl}/check`).pipe(
      tap(release => {
        this.updateAvailableSubject.next(true);
      })
    );
  }

  getStatus(): Observable<UpdateStatus> {
    return this.http.get<UpdateStatus>(`${this.baseUrl}/status`).pipe(
      tap(status => {
        this.statusSubject.next(status);
        this.updateAvailableSubject.next(status.update_available);
      })
    );
  }

  downloadUpdate(): Observable<{ status: string; file: string; version: string }> {
    return this.http.post<{ status: string; file: string; version: string }>(
      `${this.baseUrl}/download`, {}
    );
  }

  applyUpdate(): Observable<{ status: string; message: string }> {
    return this.http.post<{ status: string; message: string }>(
      `${this.baseUrl}/apply`, {}
    );
  }

  rollbackUpdate(): Observable<{ status: string; message: string }> {
    return this.http.post<{ status: string; message: string }>(
      `${this.baseUrl}/rollback`, {}
    );
  }

  clearUpdateAvailable(): void {
    this.updateAvailableSubject.next(false);
  }
}
