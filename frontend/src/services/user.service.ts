import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

/**
 * Service for handling login/logout of employees
 * @class UserService
 */
@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  base_url = 'users';

  /**
   * Login a user
   * @param loginData The login data to send to the server
   * @returns Whether the login was successful
   */
  login(loginData: FormData): Observable<string> {
    return this.http.post<string>(`${this.base_url}/login`, loginData, {
      headers: {
        'Content-Type': 'application/json',
      },
      withCredentials: true,
    });
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
