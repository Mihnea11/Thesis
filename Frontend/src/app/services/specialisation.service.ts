import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Specialisation } from '../models/specialisation';

@Injectable({
  providedIn: 'root'
})
export class SpecialisationService {
  private apiUrl = 'https://localhost:7010/Specialisation';

  constructor(private http: HttpClient) { }

  addSpecialisation(specialisation: Specialisation): Observable<Specialisation> {
    return this.http.post<Specialisation>(this.apiUrl, specialisation);
  }

  getSpecialisation(id: string): Observable<Specialisation> {
    return this.http.get<Specialisation>(`${this.apiUrl}/${id}`);
  }

  getSpecialisationByName(name: string): Observable<Specialisation> {
    return this.http.get<Specialisation>(`${this.apiUrl}/by ${name}`);
  }

  getAllSpecialisations(): Observable<Specialisation[]> {
    return this.http.get<Specialisation[]>(this.apiUrl);
  }

  updateSpecialisation(id: string, specialisation: Specialisation): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, specialisation);
  }

  deleteSpecialisation(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`);
  }
}
