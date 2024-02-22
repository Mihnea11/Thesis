import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FileService {
  private apiUrl = 'https://localhost:7010/File';

  constructor(private http: HttpClient) { }

  getLabels(): Observable<string[]> {
    return this.http.get<string[]>(`${this.apiUrl}/Labels`);
  }

  uploadFiles(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/Upload`, formData)
  }
}
