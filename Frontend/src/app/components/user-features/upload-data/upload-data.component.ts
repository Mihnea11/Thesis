import { Component, OnInit, Query } from '@angular/core';
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
  selectedLabel: string = '';

  showUploadNotification: boolean = false;

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

  attachFiles(): void {
    const totalFiles = this.regularData.length + (this.explanatoryData ? 1 : 0);

    if (totalFiles > 0) {
      this.showUploadNotification = true;

      this.fileService.startUploadSession(totalFiles).subscribe({
        next: (sessionResponse) => {
          const sessionId = sessionResponse.sessionId;
          console.log(sessionId)

          this.regularData.forEach(file => {
            this.fileService.uploadFiles(sessionId, file, this.selectedLabel).subscribe({
              next: (response) => console.log('Upload successful', response),
              error: (error) => console.log('Error uploading file', error)
            });
          });

          if (this.explanatoryData) {
            this.fileService.uploadFiles(sessionId, this.explanatoryData, this.selectedLabel, true).subscribe({
              next: (response) => console.log('Upload successful for explanatory file', response),
              error: (error) => console.error('Error uploading explanatory file', error)
            })
          }
        },
        error: (error) => console.error('Error starting upload session', error)
      });
    }
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
