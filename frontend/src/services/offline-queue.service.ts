import { inject, Injectable, OnDestroy } from '@angular/core';
import { BehaviorSubject, firstValueFrom, Subject } from 'rxjs';
import { TimeclockService } from './timeclock.service';

export interface QueuedPunch {
  id?: number;
  badgeNumber: string;
  clientTimestamp: string;
  status: 'pending' | 'syncing' | 'failed';
  attempts: number;
  lastError?: string;
  createdAt: string;
}

export interface SyncResult {
  badgeNumber: string;
  message: string;
  wasOffline: boolean;
}

@Injectable({ providedIn: 'root' })
export class OfflineQueueService implements OnDestroy {
  private timeclockService = inject(TimeclockService);

  private dbName = 'tap_offline_queue';
  private storeName = 'punches';
  private dbVersion = 1;
  private db: IDBDatabase | null = null;
  private isSyncing = false;
  private retryIntervalId: ReturnType<typeof setInterval> | null = null;

  pendingCount$ = new BehaviorSubject<number>(0);
  isOffline$ = new BehaviorSubject<boolean>(false);
  lastSyncResult$ = new Subject<SyncResult>();

  constructor() {
    this.initDB();
    this.setupConnectivityListeners();
  }

  ngOnDestroy(): void {
    this.stopPeriodicRetry();
  }

  private initDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, {
            keyPath: 'id',
            autoIncrement: true,
          });
        }
      };

      request.onsuccess = () => {
        this.db = request.result;
        this.updatePendingCount();
        resolve();
      };

      request.onerror = () => {
        console.error('Failed to open offline queue database:', request.error);
        reject(request.error);
      };
    });
  }

  private setupConnectivityListeners(): void {
    window.addEventListener('online', () => {
      this.isOffline$.next(false);
      this.syncAll();
    });

    window.addEventListener('offline', () => {
      this.isOffline$.next(true);
    });

    this.isOffline$.next(!navigator.onLine);
  }

  async enqueue(badgeNumber: string): Promise<QueuedPunch> {
    const punch: QueuedPunch = {
      badgeNumber,
      clientTimestamp: new Date().toISOString(),
      status: 'pending',
      attempts: 0,
      createdAt: new Date().toISOString(),
    };

    await this.addPunch(punch);
    await this.updatePendingCount();
    this.startPeriodicRetry();
    return punch;
  }

  async syncAll(): Promise<void> {
    if (this.isSyncing) return;
    this.isSyncing = true;

    try {
      const punches = await this.getAllPunches();

      for (const punch of punches) {
        if (punch.status === 'failed' && punch.attempts >= 3) {
          continue;
        }

        const success = await this.syncOne(punch);

        if (!success) {
          break;
        }
      }
    } finally {
      this.isSyncing = false;
      await this.updatePendingCount();

      const remaining = await this.getPendingPunchCount();
      if (remaining === 0) {
        this.stopPeriodicRetry();
      }
    }
  }

  private async syncOne(punch: QueuedPunch): Promise<boolean> {
    try {
      punch.status = 'syncing';
      await this.updatePunch(punch);

      const response = await firstValueFrom(
        this.timeclockService.timeclockWithTimestamp(
          punch.badgeNumber,
          punch.clientTimestamp
        )
      );

      await this.deletePunch(punch.id!);
      this.lastSyncResult$.next({
        badgeNumber: punch.badgeNumber,
        message: response.message,
        wasOffline: true,
      });
      return true;
    } catch (error: unknown) {
      punch.attempts++;

      if (this.isNetworkError(error) || this.isServerError(error)) {
        punch.status = 'pending';
        punch.lastError = this.getErrorMessage(error);
      } else {
        punch.status = 'failed';
        punch.lastError = this.getErrorMessage(error);
      }

      await this.updatePunch(punch);
      return false;
    }
  }

  private isNetworkError(error: unknown): boolean {
    if (error && typeof error === 'object' && 'status' in error) {
      const status = (error as { status: number }).status;
      return status === 0 || status === undefined;
    }
    return error instanceof TypeError;
  }

  private isServerError(error: unknown): boolean {
    if (error && typeof error === 'object' && 'status' in error) {
      const status = (error as { status: number }).status;
      return status >= 500 && status < 600;
    }
    return false;
  }

  private getErrorMessage(error: unknown): string {
    if (error && typeof error === 'object') {
      if ('message' in error) {
        return (error as { message: string }).message;
      }
      if ('error' in error) {
        const inner = (error as { error: { detail?: string } }).error;
        if (inner?.detail) return inner.detail;
      }
    }
    return 'Unknown error';
  }

  private startPeriodicRetry(): void {
    if (this.retryIntervalId) return;
    this.retryIntervalId = setInterval(() => {
      if (navigator.onLine && !this.isSyncing) {
        this.syncAll();
      }
    }, 30000);
  }

  private stopPeriodicRetry(): void {
    if (this.retryIntervalId) {
      clearInterval(this.retryIntervalId);
      this.retryIntervalId = null;
    }
  }

  async getQueuedPunches(): Promise<QueuedPunch[]> {
    return this.getAllPunches();
  }

  async clearFailed(): Promise<void> {
    const punches = await this.getAllPunches();
    for (const punch of punches) {
      if (punch.status === 'failed') {
        await this.deletePunch(punch.id!);
      }
    }
    await this.updatePendingCount();
  }

  // IndexedDB operations

  private addPunch(punch: QueuedPunch): Promise<number> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }
      const tx = this.db.transaction(this.storeName, 'readwrite');
      const store = tx.objectStore(this.storeName);
      const request = store.add(punch);
      request.onsuccess = () => {
        punch.id = request.result as number;
        resolve(punch.id);
      };
      request.onerror = () => reject(request.error);
    });
  }

  private getAllPunches(): Promise<QueuedPunch[]> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        resolve([]);
        return;
      }
      const tx = this.db.transaction(this.storeName, 'readonly');
      const store = tx.objectStore(this.storeName);
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
  }

  private updatePunch(punch: QueuedPunch): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }
      const tx = this.db.transaction(this.storeName, 'readwrite');
      const store = tx.objectStore(this.storeName);
      const request = store.put(punch);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private deletePunch(id: number): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }
      const tx = this.db.transaction(this.storeName, 'readwrite');
      const store = tx.objectStore(this.storeName);
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  private getPendingPunchCount(): Promise<number> {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        resolve(0);
        return;
      }
      const tx = this.db.transaction(this.storeName, 'readonly');
      const store = tx.objectStore(this.storeName);
      const request = store.count();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  private async updatePendingCount(): Promise<void> {
    const count = await this.getPendingPunchCount();
    this.pendingCount$.next(count);
  }
}
