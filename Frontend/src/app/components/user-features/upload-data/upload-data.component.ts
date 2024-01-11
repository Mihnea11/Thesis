import { Component, HostListener, Renderer2 } from '@angular/core';

@Component({
  selector: 'app-upload-data',
  templateUrl: './upload-data.component.html',
  styleUrls: ['./upload-data.component.scss']
})
export class UploadDataComponent {
  regularData: File[] = []; // This will hold the files for regular data
  explanatoryData: File | null = null; // This will hold the single file for explanatory data
  isDragOverRegular: boolean = false;
  isDragOverExplanatory: boolean = false;

  // Regular data drag events
  onDragOverRegular(event: DragEvent): void {
    event.preventDefault();
    this.isDragOverRegular = true;
  }

  onDragLeaveRegular(event: DragEvent): void {
    event.preventDefault();
    this.isDragOverRegular = false;
  }

  onFileDroppedRegular(event: any): void {
    this.regularData.push(...event.addedFiles);
    this.isDragOverRegular = false; // Reset the drag over state
  }

  // Explanatory data drag events
  onDragOverExplanatory(event: DragEvent): void {
    event.preventDefault();
    this.isDragOverExplanatory = true;
  }

  onDragLeaveExplanatory(event: DragEvent): void {
    event.preventDefault();
    this.isDragOverExplanatory = false;
  }

  onFileDroppedExplanatory(event: any): void {
    if (event.addedFiles.length > 0) {
      this.explanatoryData = event.addedFiles[0];
    }
    this.isDragOverExplanatory = false; // Reset the drag over state
  }

  // Implement the logic to handle the file upload to your server
  attachFiles(): void {
    console.log('Regular Data Files:', this.regularData);
    if (this.explanatoryData) {
      console.log('Explanatory Data File:', this.explanatoryData.name);
    }
    // Implement upload logic here
  }
}
