import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ResultsService {
  private baseUrl = 'https://localhost:7010/ModelOPS/Results'

  constructor(private http: HttpClient) { }

  getExtractedFeatures(label: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/Features/${label}`);
  }

  getGeneratedGraphics(label: string, start: number, count: number): Observable<string[]> {
    return this.http.get<string[]>(`${this.baseUrl}/Graphics/${label}/${start}:${count}`);
  }
}
