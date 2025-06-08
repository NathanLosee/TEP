import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subscription } from 'rxjs';

export interface AccessResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  badge_number: string;
}

/**
 * Service for handling login/logout of employees
 * @class UserService
 */
@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);

  base_url = 'users';
  access_token: string | null = null;

  /**
   * Login a user
   * @param loginData The login data to send to the server
   * @returns Whether the login was successful
   */
  login(loginData: FormData): Observable<AccessResponse> {
    return this.http.post<AccessResponse>(`${this.base_url}/login`, loginData);
  }

  /**
   * Logout a user
   * @returns Whether the logout was successful
   */
  logout(): Observable<string> {
    return this.http.get<string>(`${this.base_url}/logout`);
  }

  constructor() {}
}
