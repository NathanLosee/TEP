import { HttpRequest, HttpEvent, HttpHandlerFn } from '@angular/common/http';
import { Observable } from 'rxjs';

export function formDataInterceptor(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> {
  if (!(req.body instanceof FormData)) {
    return next(req);
  }
  const apiReq = req.clone({
    headers: req.headers.delete('Content-Type'),
  });
  return next(apiReq);
}
