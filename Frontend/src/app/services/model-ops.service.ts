import { HttpClient, HttpHeaderResponse, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DownloadRequest } from '../models/download-request';

@Injectable({
  providedIn: 'root'
})
export class ModelOPSService {
  private baseUrl = "https://localhost:7010/ModelOPS"

  constructor(private http: HttpClient) { }

  startSession(): Observable<any> {
    return this.http.post(`${this.baseUrl}/StartSession`, {});
  }

  downloadFiles(sessionId: string, request: DownloadRequest): Observable<any> {
    const headers = new HttpHeaders({"Content-Type": "application/json"});
    return this.http.post(`${this.baseUrl}/DownloadFiles/${sessionId}`, request, {headers});
  }
}
