import { getDashboard, getFilteredVendors } from '$lib/api-client';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies }) => {
  const token = cookies.get('auth_token');

  if (!token) {
    return { status: 401, error: 'Not authenticated' };
  }

  try {
    const [dashboardRes, awaitingPaymentRes, qualifiedRes] = await Promise.all([
      getDashboard(token),
      getFilteredVendors('awaiting-payment', token),
      getFilteredVendors('qualified-no-invoice', token),
    ]);

    return {
      dashboard: dashboardRes.data || {},
      awaitingPayment: awaitingPaymentRes.data || [],
      qualifiedNoInvoice: qualifiedRes.data || [],
    };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Failed to load',
      dashboard: {},
      awaitingPayment: [],
      qualifiedNoInvoice: [],
    };
  }
};
