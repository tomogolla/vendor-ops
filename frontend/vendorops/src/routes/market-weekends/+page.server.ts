import { error } from '@sveltejs/kit';
import { djangoApi } from '$lib/server/auth';
import type { PageServerLoad } from './$types';

export type WeekendVendor = {
  vendor_id: number;
  business_name: string;
  contact_name: string;
  phone_number: string;
  email: string;
  category: string;
  amount_paid: string;
  payment_status: 'Paid' | 'Unpaid';
};

export type MarketWeekend = {
  name: string;
  capacity: number;
  booked: number;
  available: number;
  total_paid: string;
  vendors: WeekendVendor[];
};

export const load: PageServerLoad = async ({ fetch }) => {
  let response: Response;
  try {
    response = await fetch(`${djangoApi()}/api/market-weekends/`);
  } catch {
    error(503, 'Unable to load market weekends. Check that Django is running.');
  }
  if (!response.ok) error(503, 'Unable to load market weekends. Please try again.');
  return await response.json() as { weekends: MarketWeekend[] };
};
