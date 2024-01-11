import { Injectable } from '@angular/core';
import { Observable, map, tap } from 'rxjs';
import { HttpClient, HttpHeaders, HttpResponse } from '@angular/common/http';
import { UserInfo } from '../utility/user-info';
import { AccessToken } from '../models/access-token';

@Injectable({
  providedIn: 'root'
})
export class TokenService {
  private tokenUrl = 'https://localhost:7010/Token';

  constructor(private http: HttpClient) { }

  validateAccessToken(tokenModel: AccessToken): Observable<HttpResponse<UserInfo>> {
    return this.http.post<UserInfo>(`${this.tokenUrl}/ValidateToken`, tokenModel, {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
      observe: 'response'
    });
  }
  
  revokeToken(): Observable<any> {
    this.clearAccessToken();
    return this.http.post(`${this.tokenUrl}/Revoke`, {}, { withCredentials: true });
  }

  refreshAccessToken(): Observable<HttpResponse<AccessToken>> {
    this.clearAccessToken();
    return this.http.post<AccessToken>(`${this.tokenUrl}/Refresh`, {}, {
      withCredentials: true,
      observe: 'response'
    }).pipe(
      tap((response: HttpResponse<AccessToken>) => {
        if (response.body) {
          this.storeAccessToken(response.body.accessToken);
        }
      })
    );
  }

  storeAccessToken(token: string): void {
    localStorage.setItem('accessToken', token);
  }

  getAccessToken(): string | null {
    return localStorage.getItem('accessToken');
  }

  clearAccessToken(): void {
    localStorage.removeItem('accessToken');
  }
}
