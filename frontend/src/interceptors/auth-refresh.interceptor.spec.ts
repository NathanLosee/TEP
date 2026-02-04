import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { HttpClient, HttpErrorResponse, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { authRefreshInterceptor, resetRefreshState } from './auth-refresh.interceptor';
import { UserService } from '../services/user.service';
import { PermissionService } from '../services/permission.service';

describe('authRefreshInterceptor', () => {
  let httpClient: HttpClient;
  let httpMock: HttpTestingController;
  let permissionService: PermissionService;
  let router: Router;

  const createMockJWT = (scopes: string[], badgeNumber: string): string => {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({ scopes, sub: badgeNumber, exp: Date.now() + 3600000 }));
    const signature = 'mock-signature';
    return `${header}.${payload}.${signature}`;
  };

  beforeEach(() => {
    resetRefreshState();

    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authRefreshInterceptor])),
        provideHttpClientTesting(),
        UserService,
        PermissionService,
        { provide: Router, useValue: routerSpy }
      ]
    });

    httpClient = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
    permissionService = TestBed.inject(PermissionService);
    router = TestBed.inject(Router);

    localStorage.clear();
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  describe('successful requests', () => {
    it('should pass through successful requests without modification', () => {
      const testData = { message: 'success' };

      httpClient.get('/api/test').subscribe(data => {
        expect(data).toEqual(testData);
      });

      const req = httpMock.expectOne('/api/test');
      expect(req.request.method).toBe('GET');
      req.flush(testData);
    });

    it('should not intercept non-401 errors', () => {
      httpClient.get('/api/test').subscribe(
        () => fail('should have failed with 404'),
        (error: HttpErrorResponse) => {
          expect(error.status).toBe(404);
        }
      );

      const req = httpMock.expectOne('/api/test');
      req.flush('Not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('401 errors without access token', () => {
    it('should not attempt refresh when no access token exists', () => {
      httpClient.get('/api/test').subscribe(
        () => fail('should have failed with 401'),
        (error: HttpErrorResponse) => {
          expect(error.status).toBe(401);
        }
      );

      const req = httpMock.expectOne('/api/test');
      req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });

      httpMock.expectNone('/users/refresh');
    });
  });

  describe('401 errors with access token', () => {
    beforeEach(() => {
      localStorage.setItem('access_token', 'expired-token');
    });

    it('should refresh token and retry original request on 401', fakeAsync(() => {
      const testData = { message: 'success' };
      const newToken = createMockJWT(['user.read'], 'EMP001');
      let result: any;

      httpClient.get('/api/test').subscribe(data => {
        result = data;
      });

      const req1 = httpMock.expectOne('/api/test');
      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReq = httpMock.expectOne(
        r => r.url === '/users/refresh'
      );
      expect(refreshReq.request.method).toBe('POST');
      refreshReq.flush({ access_token: newToken, token_type: 'Bearer' });
      tick();

      const req2 = httpMock.expectOne('/api/test');
      expect(req2.request.headers.get('Authorization'))
        .toBe(`Bearer ${newToken}`);
      req2.flush(testData);
      tick();

      expect(result).toEqual(testData);
      expect(localStorage.getItem('access_token')).toBe(newToken);
    }));

    it('should handle refresh failure by clearing storage and redirecting', fakeAsync(() => {
      permissionService.setPermissions({
        scopes: ['user.read'],
        badge_number: 'EMP001',
      });
      let errorReceived = false;

      httpClient.get('/api/test').subscribe(
        () => fail('should have failed'),
        () => { errorReceived = true; }
      );

      const req1 = httpMock.expectOne('/api/test');
      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReq = httpMock.expectOne(
        r => r.url === '/users/refresh'
      );
      refreshReq.flush('Refresh failed', {
        status: 401,
        statusText: 'Unauthorized',
      });
      tick();

      expect(errorReceived).toBeTrue();
      expect(localStorage.getItem('access_token')).toBeNull();
      expect(permissionService.getCurrentPermissions()).toBeNull();
      expect(router.navigate).toHaveBeenCalledWith(['/']);
    }));

    it('should not intercept 401 from refresh endpoint itself', () => {
      httpClient.post('/users/refresh', {}).subscribe(
        () => fail('should have failed with 401'),
        (error: HttpErrorResponse) => {
          expect(error.status).toBe(401);
        }
      );

      const req = httpMock.expectOne('/users/refresh');
      req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
    });
  });

  describe('concurrent requests', () => {
    beforeEach(() => {
      localStorage.setItem('access_token', 'expired-token');
    });

    it('should handle multiple concurrent 401 errors with single refresh', fakeAsync(() => {
      const testData1 = { message: 'success1' };
      const testData2 = { message: 'success2' };
      const newToken = createMockJWT(['user.read'], 'EMP001');
      let result1: any, result2: any;

      httpClient.get('/api/test1').subscribe(d => { result1 = d; });
      httpClient.get('/api/test2').subscribe(d => { result2 = d; });

      const req1 = httpMock.expectOne('/api/test1');
      const req2 = httpMock.expectOne('/api/test2');

      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();
      req2.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReqs = httpMock.match(
        r => r.url === '/users/refresh'
      );
      expect(refreshReqs.length).toBe(1);
      refreshReqs[0].flush({ access_token: newToken, token_type: 'Bearer' });
      tick();

      const retry1 = httpMock.expectOne('/api/test1');
      const retry2 = httpMock.expectOne('/api/test2');
      expect(retry1.request.headers.get('Authorization'))
        .toBe(`Bearer ${newToken}`);
      expect(retry2.request.headers.get('Authorization'))
        .toBe(`Bearer ${newToken}`);
      retry1.flush(testData1);
      retry2.flush(testData2);
      tick();

      expect(result1).toEqual(testData1);
      expect(result2).toEqual(testData2);
    }));

    it('should queue requests during active refresh', fakeAsync(() => {
      const newToken = createMockJWT(['user.read'], 'EMP001');
      let result1: any, result2: any;

      httpClient.get('/api/test1').subscribe(d => { result1 = d; });

      const req1 = httpMock.expectOne('/api/test1');
      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReq = httpMock.expectOne(
        r => r.url === '/users/refresh'
      );

      httpClient.get('/api/test2').subscribe(d => { result2 = d; });
      const req2 = httpMock.expectOne('/api/test2');
      req2.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      refreshReq.flush({ access_token: newToken, token_type: 'Bearer' });
      tick();

      const retry1 = httpMock.expectOne('/api/test1');
      const retry2 = httpMock.expectOne('/api/test2');
      retry1.flush({ message: 'success1' });
      retry2.flush({ message: 'success2' });
      tick();

      expect(result1).toEqual({ message: 'success1' });
      expect(result2).toEqual({ message: 'success2' });
    }));
  });

  describe('token management', () => {
    it('should update localStorage with new access token', fakeAsync(() => {
      const newToken = createMockJWT(['user.read'], 'EMP001');
      localStorage.setItem('access_token', 'old-token');

      httpClient.get('/api/test').subscribe();

      const req1 = httpMock.expectOne('/api/test');
      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReq = httpMock.expectOne(
        r => r.url === '/users/refresh'
      );
      refreshReq.flush({ access_token: newToken, token_type: 'Bearer' });
      tick();

      const req2 = httpMock.expectOne('/api/test');
      req2.flush({ message: 'success' });
      tick();

      expect(localStorage.getItem('access_token')).toBe(newToken);
    }));

    it('should add Bearer token to retried request headers', fakeAsync(() => {
      const newToken = createMockJWT(['user.read'], 'EMP001');
      localStorage.setItem('access_token', 'old-token');

      httpClient.get('/api/test').subscribe();

      const req1 = httpMock.expectOne('/api/test');
      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReq = httpMock.expectOne(
        r => r.url === '/users/refresh'
      );
      refreshReq.flush({ access_token: newToken, token_type: 'Bearer' });
      tick();

      const req2 = httpMock.expectOne('/api/test');
      expect(req2.request.headers.get('Authorization'))
        .toBe(`Bearer ${newToken}`);
      expect(req2.request.headers.has('Authorization')).toBeTrue();
      req2.flush({ message: 'success' });
      tick();
    }));
  });

  describe('permission and navigation', () => {
    it('should clear permissions on refresh failure', fakeAsync(() => {
      localStorage.setItem('access_token', 'expired-token');
      permissionService.setPermissions({
        scopes: ['user.read', 'user.write'],
        badge_number: 'EMP001',
      });
      expect(permissionService.getCurrentPermissions()).not.toBeNull();

      let errorReceived = false;

      httpClient.get('/api/test').subscribe(
        () => fail('should have failed'),
        () => { errorReceived = true; }
      );

      const req1 = httpMock.expectOne('/api/test');
      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReq = httpMock.expectOne(
        r => r.url === '/users/refresh'
      );
      refreshReq.flush('Refresh failed', {
        status: 401,
        statusText: 'Unauthorized',
      });
      tick();

      expect(errorReceived).toBeTrue();
      expect(permissionService.getCurrentPermissions()).toBeNull();
    }));

    it('should navigate to home page on refresh failure', fakeAsync(() => {
      localStorage.setItem('access_token', 'expired-token');

      httpClient.get('/api/test').subscribe(
        () => fail('should have failed'),
        () => {}
      );

      const req1 = httpMock.expectOne('/api/test');
      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReq = httpMock.expectOne(
        r => r.url === '/users/refresh'
      );
      refreshReq.flush('Refresh failed', {
        status: 401,
        statusText: 'Unauthorized',
      });
      tick();

      expect(router.navigate).toHaveBeenCalledWith(['/']);
    }));
  });

  describe('edge cases', () => {
    it('should handle POST requests with body', fakeAsync(() => {
      const newToken = createMockJWT(['user.read'], 'EMP001');
      const postData = { name: 'Test' };
      localStorage.setItem('access_token', 'expired-token');

      httpClient.post('/api/test', postData).subscribe();

      const req1 = httpMock.expectOne('/api/test');
      expect(req1.request.body).toEqual(postData);
      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReq = httpMock.expectOne(
        r => r.url === '/users/refresh'
      );
      refreshReq.flush({ access_token: newToken, token_type: 'Bearer' });
      tick();

      const req2 = httpMock.expectOne('/api/test');
      expect(req2.request.body).toEqual(postData);
      expect(req2.request.headers.get('Authorization'))
        .toBe(`Bearer ${newToken}`);
      req2.flush({ message: 'success' });
      tick();
    }));

    it('should preserve request headers during retry', fakeAsync(() => {
      const newToken = createMockJWT(['user.read'], 'EMP001');
      localStorage.setItem('access_token', 'expired-token');

      httpClient.get('/api/test', {
        headers: { 'X-Custom-Header': 'CustomValue' }
      }).subscribe();

      const req1 = httpMock.expectOne('/api/test');
      expect(req1.request.headers.get('X-Custom-Header'))
        .toBe('CustomValue');
      req1.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      tick();

      const refreshReq = httpMock.expectOne(
        r => r.url === '/users/refresh'
      );
      refreshReq.flush({ access_token: newToken, token_type: 'Bearer' });
      tick();

      const req2 = httpMock.expectOne('/api/test');
      expect(req2.request.headers.get('X-Custom-Header'))
        .toBe('CustomValue');
      expect(req2.request.headers.get('Authorization'))
        .toBe(`Bearer ${newToken}`);
      req2.flush({ message: 'success' });
      tick();
    }));
  });
});
