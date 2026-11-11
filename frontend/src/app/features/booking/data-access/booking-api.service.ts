import { HttpClient, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import {
  AvailabilityOption,
  CreateBookingRequest,
  CreatedBooking,
  ServiceOption,
} from '../model/booking.models';

const API_BASE = '/api/v1';

@Injectable({ providedIn: 'root' })
export class BookingApiService {
  private readonly http = inject(HttpClient);

  listServices(tenantId: string): Observable<ServiceOption[]> {
    return this.http.get<ServiceOption[]>(
      `${API_BASE}/workshops/${encodeURIComponent(tenantId)}/services`,
    );
  }

  listAvailability(
    tenantId: string,
    serviceId: string,
    startsAfter: Date,
    endsBefore: Date,
  ): Observable<AvailabilityOption[]> {
    const params = new HttpParams()
      .set('service_id', serviceId)
      .set('starts_after', startsAfter.toISOString())
      .set('ends_before', endsBefore.toISOString());
    return this.http.get<AvailabilityOption[]>(
      `${API_BASE}/workshops/${encodeURIComponent(tenantId)}/availability`,
      { params },
    );
  }

  createBooking(
    tenantId: string,
    payload: CreateBookingRequest,
  ): Observable<CreatedBooking> {
    return this.http.post<CreatedBooking>(
      `${API_BASE}/workshops/${encodeURIComponent(tenantId)}/appointments`,
      payload,
    );
  }
}
