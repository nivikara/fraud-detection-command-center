import { Component, ChangeDetectorRef , NgZone } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FraudService } from './fraud';
import { CommonModule } from '@angular/common';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent {
  // --- 1. Variables ---
  chart: any = null;
  results: any[] = []; 
  selectedFile: File | null = null;
  selectedFileName: string = '';
  amount: number = 0;
  time: number = 0;
  transactionType: string = 'PAYMENT'; 
  oldBalance: number = 0;
  result: string = '';
  file!: File;

  // --- 2. Constructor ---
  constructor(
    private fraudService: FraudService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  // --- 3. Methods ---
  
  // Handles File Selection
  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.selectedFileName = file.name;
    }
  }

  // 🟢 1. The Single Prediction Fix
  checkFraud() {
    // Pack up all 4 variables
    const data = {
      amount: this.amount,
      time: this.time,
      type: this.transactionType,
      oldbalance: this.oldBalance
    };

    this.fraudService.checkFraud(data).subscribe({
      next: (res: any) => {
        // 🔥 FORCE Angular to notice the result instantly
        this.ngZone.run(() => {
          this.result = res.result;
          this.cdr.detectChanges(); 
        });
      },
      error: (err) => {
        alert('Analysis Failed: Check console for details.');
        console.error(err);
      }
    });
  }

  // 🟢 2. The Batch Upload Fix
  upload() {
    if (!this.selectedFile) {
      alert('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.fraudService.uploadDataset(formData).subscribe({
      next: (response: any) => {
        // 🔥 FORCE Angular to notice the result instantly
        this.ngZone.run(() => {
          let rawData = response.results ? response.results : response;

          // Keep all 5 pieces of data for the table
          this.results = rawData.map((item: any) => ({
            amount: item.amount,
            time: item.time,
            type: item.type,
            oldbalance: item.oldbalance,
            result: item.result 
          }));
          
          let fraudCount = this.results.filter((r: any) => r.result === 'Fraud').length;
          let safeCount = this.results.length - fraudCount;
          
          this.cdr.detectChanges(); 
          
          // Delay the chart drawing by 10ms so the canvas HTML has time to load
          setTimeout(() => {
            this.generateChart(safeCount, fraudCount);
          }, 10);
        });
      },
      error: (error) => {
        console.error('There was an error uploading the file:', error);
        alert('Upload failed. Check the console for details.');
      }
    });
  }

  // Handles Chart Generation
  generateChart(safe: number, fraud: number) {
    const canvas = document.getElementById('fraudChart') as HTMLCanvasElement;
    if (!canvas) return;

    if (this.chart) this.chart.destroy(); 

    this.chart = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: ['Safe Transactions', 'Fraudulent Alerts'],
        datasets: [{
          data: [safe, fraud],
          backgroundColor: ['#e6ffe6', '#ffe6e6'], 
          borderColor: ['#28a745', '#dc3545'],     
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    });
  }
}