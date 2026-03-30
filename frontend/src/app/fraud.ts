import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class FraudService {
  private apiUrl = 'http://127.0.0.1:5000'; 

  constructor(private http: HttpClient) {}

  // Your existing quick-check method
  checkFraud(data: any) {
    return this.http.post(`${this.apiUrl}/predict`, data);
  }

  // NEW METHOD: Handles the file upload
  uploadDataset(formData: FormData) {
    return this.http.post(`${this.apiUrl}/upload`, formData);
  }
}