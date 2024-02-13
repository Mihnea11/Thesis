import { Component, HostListener, Renderer2 } from '@angular/core';
import { Label } from 'src/app/models/label';

@Component({
  selector: 'app-upload-data',
  templateUrl: './upload-data.component.html',
  styleUrls: ['./upload-data.component.scss']
})
export class UploadDataComponent {
  regularData: File[] = [];
  explanatoryData: File | null = null;

  isDragOverRegular: boolean = false;
  isDragOverExplanatory: boolean = false;
  openDropdown: boolean = false;
  closingDropdown: boolean = false;

  labels: Label[] = []
  filteredLabels: Label[] = []
  selectedLabel!: Label;

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
    this.isDragOverRegular = false;
  }

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
    this.isDragOverExplanatory = false;
  }

  filterLabels(): void {

  }

  selectLabel(label: Label): void {

  }

  closeDropdown(): void {

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
