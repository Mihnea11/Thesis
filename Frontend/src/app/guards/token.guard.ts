import { CanActivateFn, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';
import { TokenService } from '../services/token.service';
import { inject } from '@angular/core';
import { catchError, map, of, switchMap } from 'rxjs';
import { AccessToken } from '../models/access-token';

export const tokenGuard: CanActivateFn = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => {
  const tokenService = inject(TokenService);
  const router = inject(Router);

  const attemptTokenRefresh = () => {
    return tokenService.refreshAccessToken().pipe(
      map(refreshResp => refreshResp.status === 200),
      catchError(() => of(router.createUrlTree(['/sign-in'])))
    );
  };

  const accessTokenString = tokenService.getAccessToken();
  if (accessTokenString) {
    const accessToken: AccessToken = { accessToken: accessTokenString };
    return tokenService.validateAccessToken(accessToken).pipe(
      map(resp => resp.status === 200),
      catchError(() => attemptTokenRefresh())
    );
  } 
  else {
    return attemptTokenRefresh();
  }
};
