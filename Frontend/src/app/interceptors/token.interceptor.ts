import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthenticationService } from '../services/authentication.service';
import { TokenService } from '../services/token.service';

@Injectable()
export class TokenInterceptor implements HttpInterceptor {

  constructor(public authenticationService: AuthenticationService, private tokenService: TokenService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (request.url.includes('/Login') || request.url.includes('/Register')) {
      return next.handle(request);
    }

    const accessToken = this.tokenService.getAccessToken();

    if (accessToken) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${accessToken}`
        }
      });
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          return this.tokenService.refreshAccessToken().pipe(
            switchMap((token: any) => {
              const newAccessToken = token.accessToken;
              this.tokenService.storeAccessToken(newAccessToken);
              const clonedRequest = request.clone({
                setHeaders: {
                  Authorization: `Bearer ${newAccessToken}`
                }
              });
              return next.handle(clonedRequest);
            }),
            catchError((err) => {
              this.authenticationService.logout();
              return throwError(() => err);
            })
          );
        } else {
          return throwError(() => error);
        }
      })
    );
  }
}
