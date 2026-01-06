import { HttpEvent, HttpHandlerFn, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

const BROWSER_UUID_KEY = 'tep_browser_uuid';

export function baseUrlInterceptor(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> {
  const headers: { [key: string]: string } = {
    Authorization: `Bearer ${localStorage.getItem('access_token')}`,
  };

  // Add browser UUID header if present in localStorage
  const browserUuid = localStorage.getItem(BROWSER_UUID_KEY);
  if (browserUuid) {
    headers['X-Device-UUID'] = browserUuid;
  }

  const apiReq = req.clone({
    url: `${environment.apiUrl}${req.url}`,
    setHeaders: headers,
  });
  return next(apiReq);
}
