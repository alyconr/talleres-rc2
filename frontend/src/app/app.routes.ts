import { Routes } from '@angular/router';
import { BookingPageComponent } from './features/booking';

export const routes: Routes = [
  { path: 'workshops/:tenantId/book', component: BookingPageComponent },
  { path: '', pathMatch: 'full', redirectTo: 'workshops/demo/book' },
];
