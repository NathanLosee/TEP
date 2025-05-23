import { HttpRequest, HttpEvent, HttpHandlerFn } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export function baseUrlInterceptor(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> {
  const apiReq = req.clone({ url: `${environment.apiUrl}${req.url}` });
  return next(apiReq);
}
