import { TestBed } from '@angular/core/testing';

import { ModelOPSService } from './model-ops.service';

describe('ModelOPSService', () => {
  let service: ModelOPSService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ModelOPSService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
