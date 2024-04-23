import { Component } from '@angular/core';
import { catchError, from, switchMap } from 'rxjs';
import { DownloadRequest } from 'src/app/models/download-request';
import { FileService } from 'src/app/services/file.service';
import { ModelOPSService } from 'src/app/services/model-ops.service';

@Component({
  selector: 'app-model-configuration',
  templateUrl: './model-configuration.component.html',
  styleUrls: ['./model-configuration.component.scss']
})
export class ModelConfigurationComponent {
  patientIdentifier: string = '';
  selectedEncoding: string = '';
  rowThreshold: number = 50;
  columnThreshold: number = 50;
  showCleaningSettings: boolean = false;
  openEncodingDropdown: boolean = false;
  closeEncodingDropdown: boolean = false;

  selectedScaling: string = '';
  openScalingDropdown: boolean = false;
  closeScalingDropdown: boolean = false;

  causalityColumn: string = '';
  excludedColumns: string = '';
  
  showExpertSettings: boolean = false;

  openLabelsDropdown: boolean = false;
  closeLabelsDropdown: boolean = false;
  openAlgorithmDropdown: boolean = false;
  closeAlgorithmDropdown: boolean = false;

  labels: string[] = []
  filteredLabels: string[] = []
  selectedLabel: string = '';

  selectedAlgorithm: string = '';

  constructor(private fileService: FileService, private modelOpsService: ModelOPSService) { }

  ngOnInit(): void {
    this.retrieveLabels();
  }

  toggleExpertSettings(): void {
    this.showExpertSettings = !this.showExpertSettings;
  }

  toggleCleaningSettings(): void {
    this.showCleaningSettings = !this.showCleaningSettings;
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
    this.closeDropdown('label');
  }

  selectAlgorithm(algorithm: string): void {
    this.selectedAlgorithm = algorithm;
    this.closeDropdown('algorithm');
  }

  selectEncoding(encoding: string): void {
    this.selectedEncoding = encoding;
    this.closeDropdown('encoding');
  }

  selectScaling(scaling: string): void {
    this.selectedScaling = scaling;
    this.closeDropdown('scaling');
  }

  closeDropdown(option: string): void {
    option = option.toLowerCase();

    switch(option) {
      case "label": {
        this.closeLabelsDropdown = true;
        setTimeout(() => {
          this.openLabelsDropdown = false;
          this.closeLabelsDropdown = false;
        }, 300);
        break;
      }
    
      case "algorithm": {
        this.closeAlgorithmDropdown = true;
        setTimeout(() => {
          this.openAlgorithmDropdown = false;
          this.closeAlgorithmDropdown = false;
        }, 300);
        break;
      }

      case "encoding": {
        this.closeEncodingDropdown = true;
        setTimeout(() => {
          this.openEncodingDropdown = false;
          this.closeEncodingDropdown = false;
        }, 300);
        break;
      }

      case "scaling": {
        this.closeScalingDropdown = true;
        setTimeout(() => {
          this.openScalingDropdown = false;
          this.closeScalingDropdown = false;
        }, 300);
        break;
      }
    }
  }

  updateThreshold(event: Event, type: 'row' | 'column'): void {
    let parsedValue = parseInt((event.target as HTMLInputElement).value, 10);
    let value = isNaN(parsedValue) ? 0 : Math.max(0, Math.min(100, parsedValue));
    
    switch (type) {
      case 'row': {
        this.rowThreshold = value;
        break;
      }
      case 'column': {
        this.columnThreshold = value;
        break;
      }
    }
  }

  submitConfiguration(): void {
    this.modelOpsService.startSession().pipe(
      switchMap(sessionResponse => {
        const sessionId = sessionResponse.sessionId;
        const downloadRequest: DownloadRequest = {
          bucketName: "",
          userId: "",
          label: this.selectedLabel
        };

        return this.modelOpsService.downloadFiles(sessionId, downloadRequest);
      }),
      catchError(sessionError => {
        console.error("Session start failed", sessionError);
        return from([]);
      })
    ).subscribe({
      next: finalResponse => {console.log("Configuration complete", finalResponse)},
      error: err => console.error("Error configurating model", err),
      complete: () => console.log("Operation finished")
    });
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
