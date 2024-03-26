import { Component } from '@angular/core';
import { FileService } from 'src/app/services/file.service';

@Component({
  selector: 'app-model-configuration',
  templateUrl: './model-configuration.component.html',
  styleUrls: ['./model-configuration.component.scss']
})
export class ModelConfigurationComponent {
  causalityColumn: string = '';
  excludedColumns: string = '';
  
  showExpertSettings: boolean = false;
  showCleaningSettings: boolean = false;

  openLabelsDropdown: boolean = false;
  closeLabelsDropdown: boolean = false;
  openAlgorithmDropdown: boolean = false;
  closeAlgorithmDropdown: boolean = false;

  labels: string[] = []
  filteredLabels: string[] = []
  selectedLabel: string = '';

  selectedAlgorithm: string = '';

  constructor(private fileService: FileService) { }

  ngOnInit(): void {
    this.retrieveLabels();
  }
  
  onSubmit(): void {

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
