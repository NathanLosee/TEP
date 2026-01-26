import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../environments/environment';

export interface SystemSettings {
  id: number;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  company_name: string;
  has_logo: boolean;
  logo_filename: string | null;
  logo_updated_at?: number; // Cache buster timestamp
}

export interface SystemSettingsUpdate {
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  company_name?: string;
}

@Injectable({
  providedIn: 'root'
})
export class SystemSettingsService {
  private readonly baseUrl = '/system-settings';
  private settings$ = new BehaviorSubject<SystemSettings | null>(null);

  // Default colors matching Angular Material M3 dark theme
  // These match --sys-primary, --sys-secondary, --sys-tertiary from the compiled SCSS theme
  static readonly DEFAULT_PRIMARY = '#02E600';
  static readonly DEFAULT_SECONDARY = '#BBCBB2';
  static readonly DEFAULT_ACCENT = '#CDCD00';

  constructor(private http: HttpClient) {}

  /**
   * Get current system settings
   */
  getSettings(): Observable<SystemSettings> {
    return this.http.get<SystemSettings>(this.baseUrl).pipe(
      tap(settings => this.settings$.next(settings))
    );
  }

  /**
   * Get cached settings (observable)
   */
  getSettings$(): Observable<SystemSettings | null> {
    return this.settings$.asObservable();
  }

  /**
   * Get cached settings (value)
   */
  getCachedSettings(): SystemSettings | null {
    return this.settings$.value;
  }

  /**
   * Update system settings
   */
  updateSettings(update: SystemSettingsUpdate): Observable<SystemSettings> {
    return this.http.put<SystemSettings>(this.baseUrl, update).pipe(
      tap(settings => this.settings$.next(settings))
    );
  }

  /**
   * Upload a new logo
   */
  uploadLogo(file: File): Observable<SystemSettings> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<SystemSettings>(`${this.baseUrl}/logo`, formData).pipe(
      tap(settings => {
        // Add cache buster timestamp
        this.settings$.next({
          ...settings,
          logo_updated_at: Date.now()
        });
      })
    );
  }

  /**
   * Get logo URL with cache busting.
   * Uses the full API URL since this is used in <img> tags which don't go through HttpClient interceptors.
   */
  getLogoUrl(cacheBuster?: number): string {
    // Use full URL for img src tags (they don't go through HttpClient interceptors)
    const base = `${environment.apiUrl}${this.baseUrl}/logo`;
    // Add cache buster to force reload when logo changes
    const ts = cacheBuster || this.settings$.value?.logo_updated_at || Date.now();
    return `${base}?t=${ts}`;
  }

  /**
   * Delete the logo
   */
  deleteLogo(): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/logo`).pipe(
      tap(() => {
        const current = this.settings$.value;
        if (current) {
          this.settings$.next({
            ...current,
            has_logo: false,
            logo_filename: null
          });
        }
      })
    );
  }

  /**
   * Apply theme colors to CSS variables.
   *
   * If the colors match the defaults, we skip applying custom CSS variables
   * and let Angular Material's compiled SCSS theme handle it natively.
   * This ensures the exact M3 tonal palette is used.
   *
   * For custom colors, we generate an approximate tonal palette.
   */
  applyTheme(settings: SystemSettings): void {
    const root = document.documentElement;

    // Check if using default colors (case-insensitive comparison)
    const isDefaultPrimary = settings.primary_color.toUpperCase() === SystemSettingsService.DEFAULT_PRIMARY;
    const isDefaultSecondary = settings.secondary_color.toUpperCase() === SystemSettingsService.DEFAULT_SECONDARY;
    const isDefaultAccent = settings.accent_color.toUpperCase() === SystemSettingsService.DEFAULT_ACCENT;

    // If all colors are defaults, clear any custom overrides and let SCSS theme handle it
    if (isDefaultPrimary && isDefaultSecondary && isDefaultAccent) {
      this.clearCustomTheme();
      return;
    }

    // Apply custom colors only for non-default values
    if (!isDefaultPrimary) {
      const primaryPalette = this.generateTonalPalette(settings.primary_color);
      root.style.setProperty('--sys-primary', primaryPalette.tone80);
      root.style.setProperty('--sys-on-primary', primaryPalette.tone20);
      root.style.setProperty('--sys-primary-container', primaryPalette.tone30);
      root.style.setProperty('--sys-on-primary-container', primaryPalette.tone90);
      root.style.setProperty('--app-primary-base', settings.primary_color);
    }

    if (!isDefaultSecondary) {
      const secondaryPalette = this.generateTonalPalette(settings.secondary_color);
      root.style.setProperty('--sys-secondary', secondaryPalette.tone80);
      root.style.setProperty('--sys-on-secondary', secondaryPalette.tone20);
      root.style.setProperty('--sys-secondary-container', secondaryPalette.tone30);
      root.style.setProperty('--sys-on-secondary-container', secondaryPalette.tone90);
      root.style.setProperty('--app-secondary-base', settings.secondary_color);
    }

    if (!isDefaultAccent) {
      const tertiaryPalette = this.generateTonalPalette(settings.accent_color);
      root.style.setProperty('--sys-tertiary', tertiaryPalette.tone80);
      root.style.setProperty('--sys-on-tertiary', tertiaryPalette.tone20);
      root.style.setProperty('--sys-tertiary-container', tertiaryPalette.tone30);
      root.style.setProperty('--sys-on-tertiary-container', tertiaryPalette.tone90);
      root.style.setProperty('--app-tertiary-base', settings.accent_color);
    }
  }

  /**
   * Clear any custom theme overrides, reverting to the SCSS-defined theme.
   */
  clearCustomTheme(): void {
    const root = document.documentElement;
    const properties = [
      '--sys-primary', '--sys-on-primary', '--sys-primary-container', '--sys-on-primary-container',
      '--sys-secondary', '--sys-on-secondary', '--sys-secondary-container', '--sys-on-secondary-container',
      '--sys-tertiary', '--sys-on-tertiary', '--sys-tertiary-container', '--sys-on-tertiary-container',
      '--app-primary-base', '--app-secondary-base', '--app-tertiary-base'
    ];
    properties.forEach(prop => root.style.removeProperty(prop));
  }

  /**
   * Generate a tonal palette from a base color.
   * Material Design 3 uses a 13-tone scale (0-100).
   * For dark theme, we use higher tones for the main color.
   */
  private generateTonalPalette(hex: string) {
    return {
      tone0: '#000000',
      tone10: this.adjustTone(hex, 10),
      tone20: this.adjustTone(hex, 20),
      tone30: this.adjustTone(hex, 30),
      tone40: this.adjustTone(hex, 40),
      tone50: hex, // Base color is approximately tone 50
      tone60: this.adjustTone(hex, 60),
      tone70: this.adjustTone(hex, 70),
      tone80: this.adjustTone(hex, 80),
      tone90: this.adjustTone(hex, 90),
      tone95: this.adjustTone(hex, 95),
      tone99: this.adjustTone(hex, 99),
      tone100: '#FFFFFF',
    };
  }

  /**
   * Adjust color to a specific tone (0-100 scale).
   * Tone 0 = black, Tone 100 = white, Tone 50 = base color
   */
  private adjustTone(hex: string, tone: number): string {
    const rgb = this.hexToRgb(hex);

    if (tone <= 50) {
      // Darken: blend towards black
      const factor = tone / 50;
      return this.rgbToHex(
        Math.round(rgb.r * factor),
        Math.round(rgb.g * factor),
        Math.round(rgb.b * factor)
      );
    } else {
      // Lighten: blend towards white
      const factor = (tone - 50) / 50;
      return this.rgbToHex(
        Math.round(rgb.r + (255 - rgb.r) * factor),
        Math.round(rgb.g + (255 - rgb.g) * factor),
        Math.round(rgb.b + (255 - rgb.b) * factor)
      );
    }
  }

  private hexToRgb(hex: string): { r: number; g: number; b: number } {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 0, g: 0, b: 0 };
  }

  private rgbToHex(r: number, g: number, b: number): string {
    return '#' + [r, g, b].map(x => {
      const hex = x.toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  }
}
