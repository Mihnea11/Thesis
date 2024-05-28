import { Component } from '@angular/core';
import { Feature } from 'src/app/models/feature';
import { FileService } from 'src/app/services/file.service';
import { ResultsService } from 'src/app/services/results.service';

@Component({
  selector: 'app-results-display',
  templateUrl: './results-display.component.html',
  styleUrls: ['./results-display.component.scss']
})
export class ResultsDisplayComponent {
  labels: string[] = []
  filteredLabels: string[] = []
  selectedLabel: string = '';

  features: Feature[] = [];

  openDropdown: boolean = false;
  closingDropdown: boolean = false;

  activeIcon: 'features' | 'graphs' | 'stats' | null = null;

  showLoadingSpinner: boolean = false;
  errorOccurred: boolean = false;
  errorMessage: string = '';

  constructor(private fileService: FileService, private resultsService: ResultsService) {}

  ngOnInit() {
    this.retrieveLabels();
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
    if (label != this.selectedLabel) {
      this.activeIcon = null;
    }
    
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

  toggleIcon(icon: 'features' | 'graphs' | 'stats') {
    this.activeIcon = icon;

    if (icon === 'features') {
      this.loadFeatures();
    } else if (icon == 'graphs') {
      //this.callSecondMethod();
    }
    else {

    }
  }

  loadFeatures() {
    this.features = [];
    this.showLoadingSpinner = true;
    this.errorOccurred = false;

    if (this.selectedLabel) {
      this.resultsService.getExtractedFeatures(this.selectedLabel).subscribe({
        next: (data) => {
          this.features = Object.entries(data).map(([key, value]) => ({
            name: key,
            importance: value
          }));
          this.showLoadingSpinner = false;
        },
        error: (error) => {
          console.error('Error getting extracted features', error);
          this.errorOccurred = true;
          this.showLoadingSpinner = false;

          this.errorMessage = "Failed to load your data. Please try again.";
        }
      });
    } else {
      this.showLoadingSpinner = false;
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
