import { Injectable, signal } from '@angular/core';

import { BookingApiService } from '../data-access/booking-api.service';
import {
  AvailabilityOption,
  ServiceOption,
} from '../model/booking.models';

@Injectable()
export class BookingState {
  readonly tenantId = signal('');
  readonly services = signal<ServiceOption[]>([]);
  readonly slots = signal<AvailabilityOption[]>([]);
  readonly selectedServiceId = signal('');
  readonly selectedSlot = signal('');
  readonly customerName = signal('');
  readonly customerPhone = signal('');
  readonly loading = signal(false);
  readonly error = signal('');

  constructor(private readonly api: BookingApiService) {}

  setTenant(tenantId: string): void {
    this.tenantId.set(tenantId);
    this.loadServices();
  }

  setCustomerName(name: string): void {
    this.customerName.set(name);
  }

  setCustomerPhone(phone: string): void {
    this.customerPhone.set(phone);
  }

  selectService(serviceId: string): void {
    this.selectedServiceId.set(serviceId);
    this.selectedSlot.set('');
    this.slots.set([]);
    if (!serviceId) return;

    const startsAfter = new Date();
    const endsBefore = new Date();
    endsBefore.setDate(endsBefore.getDate() + 30);
    this.loading.set(true);
    this.error.set('');
    this.api
      .listAvailability(this.tenantId(), serviceId, startsAfter, endsBefore)
      .subscribe({
        next: (slots) => {
          this.slots.set(slots);
          this.loading.set(false);
        },
        error: () => {
          this.error.set('No pudimos cargar los horarios. Intenta de nuevo.');
          this.loading.set(false);
        },
      });
  }

  selectSlot(startsAt: string): void {
    this.selectedSlot.set(startsAt);
  }

  submitBooking(): void {
    const serviceId = this.selectedServiceId();
    const startsAt = this.selectedSlot();
    const customerName = this.customerName().trim();
    const customerPhone = this.customerPhone().trim();
    if (!serviceId || !startsAt || !customerName || !customerPhone) return;

    this.loading.set(true);
    this.error.set('');
    this.api
      .createBooking(this.tenantId(), {
        service_id: serviceId,
        starts_at: startsAt,
        customer_name: customerName,
        customer_phone: customerPhone,
      })
      .subscribe({
        next: (booking) => window.location.assign(booking.checkout_url),
        error: () => {
          this.error.set('No pudimos completar la reserva. Revisa el horario e inténtalo de nuevo.');
          this.loading.set(false);
        },
      });
  }

  private loadServices(): void {
    this.loading.set(true);
    this.error.set('');
    this.api.listServices(this.tenantId()).subscribe({
      next: (services) => {
        this.services.set(services);
        this.loading.set(false);
        if (services.length === 0) this.error.set('Este taller aún no tiene servicios disponibles.');
      },
      error: () => {
        this.error.set('No pudimos cargar los servicios. Intenta de nuevo.');
        this.loading.set(false);
      },
    });
  }
}
