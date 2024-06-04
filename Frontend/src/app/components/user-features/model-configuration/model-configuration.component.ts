import { Component } from '@angular/core';
import { catchError, from, of, switchMap } from 'rxjs';
import { CleaningRequest } from 'src/app/models/cleaning-request';
import { DownloadRequest } from 'src/app/models/download-request';
import { FileService } from 'src/app/services/file.service';
import { ModelOPSService } from 'src/app/services/model-ops.service';

@Component({
  selector: 'app-model-configuration',
  templateUrl: './model-configuration.component.html',
  styleUrls: ['./model-configuration.component.scss']
})
export class ModelConfigurationComponent {
  maxDepth: number = 5;
  randomState: number = 42;
  chunkSize: number = 10000

  defaultMaxDepth: number = 5;
  defaultRandomState: number = 42;
  defaultChunkSize: number = 10000;

  patientIdentifier: string = '';
  selectedEncoding: string = '';
  rowThreshold: number = 50;
  columnThreshold: number = 30;
  showCleaningSettings: boolean = false;
  openEncodingDropdown: boolean = false;
  closeEncodingDropdown: boolean = false;

  selectedScaling: string = '';
  openScalingDropdown: boolean = false;
  closeScalingDropdown: boolean = false;

  causalityColumn: string = '';

  excludedCleaningColumns: string = '';
  excludedCleaningColumnsArray: string[] = [];
  excludedTrainingColumns: string = '';
  excludedTrainingColumnsArray: string[] = [];

  showExpertSettings: boolean = false;

  openLabelsDropdown: boolean = false;
  closeLabelsDropdown: boolean = false;
  openAlgorithmDropdown: boolean = false;
  closeAlgorithmDropdown: boolean = false;

  labels: string[] = []
  filteredLabels: string[] = []
  selectedLabel: string = '';

  showTrainingNotification: boolean = false;

  constructor(private fileService: FileService, private modelOpsService: ModelOPSService) { }

  ngOnInit(): void {
    this.retrieveLabels();

    this.selectEncoding("Label Encoding");
    this.selectScaling("Standardize");
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

  updateChunkSize(event: Event): void {
    let element = event.target as HTMLInputElement;
    this.chunkSize = parseInt(element.value, 10);

    if (isNaN(this.chunkSize)) {
      this.chunkSize = 10000;
    }
  }

  updateThreshold(value: Event | number, type: 'row' | 'column'): void {
    let parsedValue: number;
    if (typeof value == "number") {
      parsedValue = value;
    }
    else {
      parsedValue = parseInt((value.target as HTMLInputElement).value, 10);
    }
    let finalValue = isNaN(parsedValue) ? 0 : Math.max(0, Math.min(100, parsedValue));
    
    switch (type) {
      case 'row': {
        this.rowThreshold = finalValue;
        break;
      }
      case 'column': {
        this.columnThreshold = finalValue;
        break;
      }
    }
  }

  parseExcludedColumns(value: string): string[] {
    console.log(value)

    let excludedColumns = []  
    excludedColumns = value.split(',').map(column => column.trim()).filter(column => column);
  
    return excludedColumns;
  }

  validateInput(): Boolean {
    if (!this.selectedLabel || !this.causalityColumn) {
      return false;
    }
  
    if (this.showCleaningSettings) {
      if (!this.patientIdentifier || !this.selectedEncoding || 
          !this.selectedScaling || this.rowThreshold == null || 
          this.columnThreshold == null) {
        return false;
      }
    }
  
    if (this.showExpertSettings) {
      if (this.maxDepth == null || this.randomState == null || this.chunkSize == null) {
        return false;
      }
    }
  
    return true;
  }

  submitConfiguration(): void {
    this.showTrainingNotification = true;
    this.excludedCleaningColumnsArray = this.parseExcludedColumns(this.excludedCleaningColumns)
    this.excludedTrainingColumnsArray = this.parseExcludedColumns(this.excludedTrainingColumns);

    console.log(this.excludedCleaningColumnsArray)
    console.log(this.excludedTrainingColumnsArray)


    this.modelOpsService.startSession().pipe(
      switchMap(sessionResponse => {
        const sessionId = sessionResponse.sessionId;
        const downloadRequest: DownloadRequest = {
          bucketName: "",
          userId: "",
          label: this.selectedLabel
        };
  
        return this.modelOpsService.downloadFiles(sessionId, downloadRequest).pipe(
          switchMap(downloadResponse => {
            if (this.showCleaningSettings) {
              const cleaningRequest: CleaningRequest = {
                input_path: downloadResponse.filePath,
                patient_identifier: this.patientIdentifier,
                encoding_method: this.selectedEncoding,
                scale_method: this.selectedScaling,
                row_threshold: this.rowThreshold,
                column_threshold: this.columnThreshold,
                excluded_columns: this.excludedCleaningColumnsArray
              };
  
              return this.modelOpsService.cleanFiles(sessionId, cleaningRequest);
            } else {
              return of(downloadResponse);
            }
          }),
          switchMap(cleaningOrDownloadResponse => {
            const trainModelRequest = {
              input_path: this.showCleaningSettings ? cleaningOrDownloadResponse.cleanedFilePath : cleaningOrDownloadResponse.file_path,
              target_column: this.causalityColumn,
              max_depth: this.showExpertSettings ? this.maxDepth : this.defaultMaxDepth,
              random_state: this.showExpertSettings ? this.randomState : this.defaultRandomState,
              chunk_size: this.showExpertSettings ? this.chunkSize : this.defaultChunkSize,
              excluded_columns: this.excludedTrainingColumnsArray,
              bucketName: "",
              label: this.selectedLabel,
              userId: "",
              patient_identifier: this.patientIdentifier
            };
  
            return this.modelOpsService.trainModel(sessionId, trainModelRequest);
          })
        );
      }),
      catchError(sessionError => {
        console.error("Session start failed", sessionError);
        return from([]);
      })
    ).subscribe({
      next: finalResponse => {
        console.log("Configuration and model training complete", finalResponse);
      },
      error: err => {
        console.error("Error configuring and training model", err);
      },
      complete: () => {
        console.log("Operation finished");
      }
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
