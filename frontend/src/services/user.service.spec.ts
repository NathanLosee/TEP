import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { UserService, User, UserBase, AccessResponse } from './user.service';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;
  const baseUrl = 'users';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [UserService]
    });

    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);

    // Clear localStorage before each test
    localStorage.clear();
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  describe('login', () => {
    it('should send POST request with FormData and return access token', (done) => {
      const mockResponse: AccessResponse = {
        access_token: 'test-token-12345',
        token_type: 'Bearer'
      };

      const formData = new FormData();
      formData.append('username', 'EMP001');
      formData.append('password', 'testpass123');

      service.login(formData).subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.access_token).toBe('test-token-12345');
        expect(response.token_type).toBe('Bearer');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/login`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(formData);
      req.flush(mockResponse);
    });

    it('should handle login errors', (done) => {
      const formData = new FormData();
      formData.append('username', 'INVALID');
      formData.append('password', 'wrong');

      service.login(formData).subscribe(
        () => fail('should have failed with 401'),
        (error) => {
          expect(error.status).toBe(401);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/login`);
      req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
    });
  });

  describe('refreshToken', () => {
    it('should send POST request to refresh endpoint', (done) => {
      const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZXMiOlsidXNlci5yZWFkIl0sInN1YiI6IkVNUDAwMSIsImV4cCI6MTcwMDAwMDAwMH0.signature';
      const mockResponse: AccessResponse = {
        access_token: mockToken,
        token_type: 'Bearer'
      };

      service.refreshToken().subscribe(response => {
        expect(response).toEqual(mockResponse);
        expect(response.access_token).toBe(mockToken);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/refresh`);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);
    });

    it('should handle refresh token errors', (done) => {
      service.refreshToken().subscribe(
        () => fail('should have failed with 401'),
        (error) => {
          expect(error.status).toBe(401);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/refresh`);
      req.flush('Token expired', { status: 401, statusText: 'Unauthorized' });
    });
  });

  describe('getUsers', () => {
    it('should retrieve all users', (done) => {
      const mockUsers: User[] = [
        { id: 1, badge_number: 'EMP001' },
        { id: 2, badge_number: 'EMP002' },
        { id: 3, badge_number: 'MGR001' }
      ];

      service.getUsers().subscribe(users => {
        expect(users.length).toBe(3);
        expect(users).toEqual(mockUsers);
        expect(users[0].badge_number).toBe('EMP001');
        expect(users[1].badge_number).toBe('EMP002');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/`);
      expect(req.request.method).toBe('GET');
      req.flush(mockUsers);
    });

    it('should return empty array when no users exist', (done) => {
      service.getUsers().subscribe(users => {
        expect(users).toEqual([]);
        expect(users.length).toBe(0);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/`);
      req.flush([]);
    });

    it('should handle server errors', (done) => {
      service.getUsers().subscribe(
        () => fail('should have failed'),
        (error) => {
          expect(error.status).toBe(500);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/`);
      req.flush('Server error', { status: 500, statusText: 'Internal Server Error' });
    });
  });

  describe('getUserById', () => {
    it('should retrieve user by id', (done) => {
      const mockUser: User = { id: 5, badge_number: 'EMP005' };

      service.getUserById(5).subscribe(user => {
        expect(user).toEqual(mockUser);
        expect(user.id).toBe(5);
        expect(user.badge_number).toBe('EMP005');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/5`);
      expect(req.request.method).toBe('GET');
      req.flush(mockUser);
    });

    it('should handle user not found', (done) => {
      service.getUserById(999).subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('User not found', { status: 404, statusText: 'Not Found' });
    });
  });

  describe('createUser', () => {
    it('should create new user', (done) => {
      const newUser: UserBase = {
        badge_number: 'EMP010',
        password: 'SecurePass123'
      };

      const createdUser: User = {
        id: 10,
        badge_number: 'EMP010'
      };

      service.createUser(newUser).subscribe(user => {
        expect(user).toEqual(createdUser);
        expect(user.id).toBe(10);
        expect(user.badge_number).toBe('EMP010');
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newUser);
      req.flush(createdUser);
    });

    it('should handle validation errors', (done) => {
      const invalidUser: UserBase = {
        badge_number: '',
        password: '123'
      };

      service.createUser(invalidUser).subscribe(
        () => fail('should have failed with 422'),
        (error) => {
          expect(error.status).toBe(422);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/`);
      req.flush('Validation error', { status: 422, statusText: 'Unprocessable Entity' });
    });

    it('should handle duplicate badge number', (done) => {
      const duplicateUser: UserBase = {
        badge_number: 'EMP001',
        password: 'Password123'
      };

      service.createUser(duplicateUser).subscribe(
        () => fail('should have failed with 409'),
        (error) => {
          expect(error.status).toBe(409);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/`);
      req.flush('Badge number already exists', { status: 409, statusText: 'Conflict' });
    });
  });

  describe('deleteUser', () => {
    it('should delete user by id', (done) => {
      service.deleteUser(5).subscribe(() => {
        expect().nothing();
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/5`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle user not found on delete', (done) => {
      service.deleteUser(999).subscribe(
        () => fail('should have failed with 404'),
        (error) => {
          expect(error.status).toBe(404);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/999`);
      req.flush('User not found', { status: 404, statusText: 'Not Found' });
    });

    it('should accept numeric id parameter', (done) => {
      const userId = 42;

      service.deleteUser(userId).subscribe(() => {
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/42`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });
  });

  describe('updateUserPassword', () => {
    it('should update user password', (done) => {
      const badgeNumber = 'EMP003';
      const passwordData = {
        badge_number: 'EMP003',
        password: 'OldPass123',
        new_password: 'NewPass456'
      };

      const updatedUser: User = { id: 3, badge_number: 'EMP003' };

      service.updateUserPassword(badgeNumber, passwordData).subscribe(user => {
        expect(user).toEqual(updatedUser);
        done();
      });

      const req = httpMock.expectOne(`${baseUrl}/${badgeNumber}`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(passwordData);
      req.flush(updatedUser);
    });

    it('should handle incorrect old password', (done) => {
      const passwordData = {
        badge_number: 'EMP001',
        password: 'WrongPass',
        new_password: 'NewPass456'
      };

      service.updateUserPassword('EMP001', passwordData).subscribe(
        () => fail('should have failed with 401'),
        (error) => {
          expect(error.status).toBe(401);
          done();
        }
      );

      const req = httpMock.expectOne(`${baseUrl}/EMP001`);
      req.flush('Incorrect password', { status: 401, statusText: 'Unauthorized' });
    });
  });


  describe('User interface', () => {
    it('should have correct User interface structure', () => {
      const user: User = {
        id: 1,
        badge_number: 'EMP001'
      };

      expect(user.id).toBeDefined();
      expect(user.badge_number).toBeDefined();
      expect(typeof user.badge_number).toBe('string');
    });

    it('should allow User without id (for creation)', () => {
      const user: User = {
        badge_number: 'EMP002'
      };

      expect(user.id).toBeUndefined();
      expect(user.badge_number).toBe('EMP002');
    });
  });

  describe('UserBase interface', () => {
    it('should have correct UserBase structure for creation', () => {
      const userBase: UserBase = {
        badge_number: 'EMP003',
        password: 'SecurePassword123'
      };

      expect(userBase.badge_number).toBe('EMP003');
      expect(userBase.password).toBe('SecurePassword123');
    });
  });

  describe('AccessResponse interface', () => {
    it('should have correct AccessResponse structure', () => {
      const response: AccessResponse = {
        access_token: 'token-string',
        token_type: 'Bearer'
      };

      expect(response.access_token).toBe('token-string');
      expect(response.token_type).toBe('Bearer');
    });
  });
});
