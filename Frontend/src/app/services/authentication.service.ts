import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { User } from '../models/user';
import { UserCredentials } from '../utility/user-credentials';
import { TokenService } from './token.service';

@Injectable({
  providedIn: 'root'
})
export class AuthenticationService {
  private apiUrl = 'https://localhost:7010/Authentication';

  constructor(private http: HttpClient, private tokenService: TokenService) {}

  registerUser(user: User): Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json'
      })
    };
    
    return this.http.post(`${this.apiUrl}/Register`, user, httpOptions);
  }

  loginUser(credentials: UserCredentials, rememberMe: boolean): Observable<any> {
    const url = `${this.apiUrl}/Login?rememberMe=${rememberMe}`;
    const httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
      withCredentials: true
    };

    return this.http.post(url, credentials, httpOptions);
  }

  logout(): Observable<any> {
    this.tokenService.clearAccessToken();

    return this.tokenService.revokeToken();
  }
}
