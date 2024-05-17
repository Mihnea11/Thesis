import { HttpClient, HttpHeaderResponse, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DownloadRequest } from '../models/download-request';
import { CleaningRequest } from '../models/cleaning-request';
import { TrainRequest } from '../models/train-request';

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

  cleanFiles(sessionId: string, request: CleaningRequest): Observable<any> {
    const headers = new HttpHeaders({"Content-Type": "application/json"});
    return this.http.post(`${this.baseUrl}/CleanFiles/${sessionId}`, request, {headers});
  }

  trainModel(sessionId: string, request: TrainRequest): Observable<any> {
    const headers = new HttpHeaders({"Content-Type": "application/json"});
    return this.http.post(`${this.baseUrl}/TrainModel/${sessionId}`, request, {headers});
  }
}
