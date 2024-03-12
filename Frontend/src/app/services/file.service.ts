import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, from, concatMap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class FileService {
  private apiUrl = 'https://localhost:7010/File';

  constructor(private http: HttpClient) { }

  getLabels(): Observable<string[]> {
    return this.http.get<string[]>(`${this.apiUrl}/Labels`);
  }

  startUploadSession(totalFiles: number): Observable<any> {
    const body = { TotalFiles: totalFiles };
    return this.http.post(`${this.apiUrl}/StartUpload`, body);
  }

  uploadFiles(sessionId: string, file: File, label: string, isExplanatory: boolean = false): Observable<any> {
    const chunkSize = 5 * 1024 * 1024;
    let start = 0;
    const totalChunks = Math.ceil(file.size / chunkSize);
    const fileName = isExplanatory ? 'explanatory_file.csv' : file.name;
  
    const uploadObservable = new Observable(observer => {
      const uploadChunk = (chunkIndex: number) => {
        const end = start + chunkSize < file.size ? start + chunkSize : file.size;
        const chunk = file.slice(start, end);
        const formData = new FormData();
        formData.append('ChunkFile', chunk, fileName);
        formData.append('FileName', fileName);
        formData.append('ChunkIndex', chunkIndex.toString());
        formData.append('TotalChunks', totalChunks.toString());
        formData.append('Label', label);
  
        this.http.post(`${this.apiUrl}/Upload/${sessionId}`, formData).subscribe({
          next: (response) => {
            observer.next(response);
            if (end < file.size) {
              start += chunkSize;
              uploadChunk(chunkIndex + 1);
            } else {
              observer.complete();
            }
          },
          error: (error) => observer.error(error)
        });
      };
  
      uploadChunk(0);
    });
  
    return uploadObservable;
  }
}
