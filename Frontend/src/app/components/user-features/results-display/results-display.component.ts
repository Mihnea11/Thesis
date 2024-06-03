import { Component, OnInit } from '@angular/core';
import { Feature } from 'src/app/models/feature';
import { FileService } from 'src/app/services/file.service';
import { ResultsService } from 'src/app/services/results.service';

@Component({
  selector: 'app-results-display',
  templateUrl: './results-display.component.html',
  styleUrls: ['./results-display.component.scss']
})
export class ResultsDisplayComponent implements OnInit {
  labels: string[] = [];
  filteredLabels: string[] = [];
  selectedLabel: string = '';

  features: Feature[] = [];
  accuracy: string = '';

  openDropdown: boolean = false;
  closingDropdown: boolean = false;

  activeIcon: 'features' | 'graphs' | 'stats' | null = null;

  showLoadingSpinner: boolean = false;
  errorOccurred: boolean = false;
  errorMessage: string = '';

  images: string[] = [];
  hasMore: boolean = true;
  nearBottom: boolean = false;
  start: number = 0;
  count: number = 8;

  fullscreenImage: string | null = null;
  lastScrollTime: number = 0;
  throttleDuration: number = 300;

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
    } else if (icon === 'graphs') {
      this.loadGraphs();
    }
    // Handle other icons if needed
  }

  loadFeatures() {
    this.features = [];
    this.showLoadingSpinner = true;
    this.errorOccurred = false;

    if (this.selectedLabel) {
      this.resultsService.getExtractedFeatures(this.selectedLabel).subscribe({
        next: (data) => {
          Object.entries(data).forEach(([key, value]) => {
            if (key === 'Accuracy') {
              this.accuracy = `${value}%`;
            } else {
              this.features.push({name: key, importance: value});
            }
          });
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

  onScroll() {
    const now = Date.now();
    if (now - this.lastScrollTime > this.throttleDuration) {
      this.lastScrollTime = now;
      this.loadMoreImages();
    }
  }

  loadGraphs() {
    this.images = [];
    this.hasMore = true;
    this.start = 0;
    this.showLoadingSpinner = true;
    this.errorOccurred = false;

    this.loadMoreImages();
  }

  loadMoreImages(): void {
    if (this.hasMore && this.selectedLabel) {
      this.resultsService.getGeneratedGraphics(this.selectedLabel, this.start, this.count).subscribe({
        next: (newImages) => {
          this.images = [...this.images, ...newImages];
          this.start += this.count;
          if (newImages.length < this.count) {
            this.hasMore = false;
          }
          this.showLoadingSpinner = false;
        },
        error: (error) => {
          console.error('Error fetching images:', error);
          this.hasMore = false;
          this.showLoadingSpinner = false;
          this.errorOccurred = true;
          this.errorMessage = "Failed to load your images. Please try again.";
        }
      });
    }
  }

  openFullscreen(image: string): void {
    this.fullscreenImage = image;
  }

  closeFullscreen(): void {
    this.fullscreenImage = null;
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
