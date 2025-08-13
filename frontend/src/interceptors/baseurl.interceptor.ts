import { HttpEvent, HttpHandlerFn, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export function baseUrlInterceptor(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> {
  const apiReq = req.clone({
    url: `${environment.apiUrl}${req.url}`,
    setHeaders: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
    },
  });
  return next(apiReq);
}
