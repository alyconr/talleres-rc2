import { Component, inject } from '@angular/core';
import { CurrencyPipe } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

import { BookingState } from '../state/booking.state';
import { AvailabilityOption } from '../model/booking.models';

@Component({
  selector: 'app-booking-page',
  imports: [CurrencyPipe],
  providers: [BookingState],
  templateUrl: './booking-page.component.html',
  styleUrl: './booking-page.component.css',
})
export class BookingPageComponent {
  private readonly route = inject(ActivatedRoute);
  protected readonly state = inject(BookingState);

  constructor() {
    this.route.paramMap.subscribe((params) => {
      const tenantId = params.get('tenantId');
      if (!tenantId) {
        this.state.error.set('No encontramos el taller de esta reserva.');
        return;
      }
      this.state.setTenant(tenantId);
    });
  }

  protected onServiceSelected(event: Event): void {
    this.state.selectService((event.target as HTMLSelectElement).value);
  }

  protected onNameChanged(event: Event): void {
    this.state.setCustomerName((event.target as HTMLInputElement).value);
  }

  protected onPhoneChanged(event: Event): void {
    this.state.setCustomerPhone((event.target as HTMLInputElement).value);
  }

  protected formatSlot(slot: AvailabilityOption): string {
    return new Intl.DateTimeFormat('es-CO', {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(slot.starts_at));
  }
}
