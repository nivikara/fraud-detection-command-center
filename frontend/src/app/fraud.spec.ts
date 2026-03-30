import { TestBed } from '@angular/core/testing';

import { Fraud } from './fraud';

describe('Fraud', () => {
  let service: Fraud;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Fraud);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
