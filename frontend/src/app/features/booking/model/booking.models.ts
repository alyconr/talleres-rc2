export interface ServiceOption {
  id: string;
  name: string;
  duration_minutes: number;
  deposit_amount: number;
  currency: string;
}

export interface AvailabilityOption {
  starts_at: string;
  ends_at: string;
}

export interface CreateBookingRequest {
  service_id: string;
  starts_at: string;
  customer_name: string;
  customer_phone: string;
}

export interface CreatedBooking {
  appointment_id: string;
  status: string;
  checkout_url: string;
}
