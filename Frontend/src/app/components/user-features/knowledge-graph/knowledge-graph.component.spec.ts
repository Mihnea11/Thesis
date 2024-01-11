import { ComponentFixture, TestBed } from '@angular/core/testing';

import { KnowledgeGraphComponent } from './knowledge-graph.component';

describe('KnowledgeGraphComponent', () => {
  let component: KnowledgeGraphComponent;
  let fixture: ComponentFixture<KnowledgeGraphComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [KnowledgeGraphComponent]
    });
    fixture = TestBed.createComponent(KnowledgeGraphComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
