import { Component, OnInit } from '@angular/core';
import { FileService } from 'src/app/services/file.service';

@Component({
  selector: 'app-upload-data',
  templateUrl: './upload-data.component.html',
  styleUrls: ['./upload-data.component.scss']
})
export class UploadDataComponent implements OnInit {
  regularData: File[] = [];
  explanatoryData: File | null = null;

  tooltipVisibility = {
    regularData: false,
    explanatoryData: false
  };

  isDragOverRegular: boolean = false;
  isDragOverExplanatory: boolean = false;
  openDropdown: boolean = false;
  closingDropdown: boolean = false;

  labels: string[] = []
  filteredLabels: string[] = []
  selectedLabel!: string;

  constructor(private fileService: FileService) {}

  ngOnInit(): void {
    this.retrieveLabels();
  }


  toggleTooltip(section: 'regularData' | 'explanatoryData', isVisible: boolean) {
    this.tooltipVisibility[section] = isVisible;
  }

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
    const filterValue = this.selectedLabel.toLowerCase();
    this.filteredLabels = this.labels.filter(spec =>
      spec.toLowerCase().includes(filterValue)
    );
    this.filteredLabels = this.filteredLabels.filter(spec =>
      spec.toLowerCase() !== filterValue
    );
  }

  selectLabel(label: string): void {
    this.selectedLabel = label;
    this.closeDropdown();
  }

  closeDropdown(): void {
    this.closingDropdown = true;
    setTimeout(() => {
      this.openDropdown = false;
      this.closingDropdown = false;
    }, 300);
  }

  // Implement the logic to handle the file upload to your server
  attachFiles(): void {
    console.log('Regular Data Files:', this.regularData);
    if (this.explanatoryData) {
      console.log('Explanatory Data File:', this.explanatoryData.name);
    }
    // Implement upload logic here
  }

  private retrieveLabels(): void {
    this.fileService.getLabels().subscribe({
      next: (labels) => {
        this.labels = labels;
        this.filteredLabels = labels;
      },
      error: (error) => console.error("Error fetching labels", error)
    });
  }
}
