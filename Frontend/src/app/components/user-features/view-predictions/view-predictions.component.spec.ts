import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewPredictionsComponent } from './view-predictions.component';

describe('ViewPredictionsComponent', () => {
  let component: ViewPredictionsComponent;
  let fixture: ComponentFixture<ViewPredictionsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ViewPredictionsComponent]
    });
    fixture = TestBed.createComponent(ViewPredictionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
