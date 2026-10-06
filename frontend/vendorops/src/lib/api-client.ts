/**
 * API Client for Phase 1.2 Backend
 * Handles all HTTP requests to the vendor ops API
 */

const API_BASE = 'http://localhost:8000/api';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  errors?: Record<string, string[]>;
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  body?: Record<string, any>;
  token?: string;
  cache?: RequestCache;
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<ApiResponse<T>> {
  const {
    method = 'GET',
    body,
    token,
    cache = 'no-cache'
  } = options;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Token ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
      cache,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        error: data.detail || data.message || `HTTP ${response.status}`,
        errors: data.errors || data,
      };
    }

    return { data };
  } catch (err) {
    return {
      error: err instanceof Error ? err.message : 'Unknown error',
    };
  }
}

// Vendor Profiles
export async function getVendorProfiles(
  token: string,
  filters?: {
    status?: string;
    owner?: number;
    search?: string;
  }
) {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);
  if (filters?.owner) params.append('owner', String(filters.owner));
  if (filters?.search) params.append('search', filters.search);

  const query = params.toString();
  const endpoint = `/vendor-profiles/${query ? '?' + query : ''}`;
  return apiRequest<any[]>(endpoint, { token });
}

export async function getVendorProfile(id: number, token: string) {
  return apiRequest<any>(`/vendor-profiles/${id}/`, { token });
}

export async function updateVendorProfile(
  id: number,
  data: Record<string, any>,
  token: string
) {
  return apiRequest(`/vendor-profiles/${id}/`, {
    method: 'PATCH',
    body: data,
    token,
  });
}

export async function qualifyVendor(id: number, reason: string, token: string) {
  return apiRequest(`/vendor-profiles/${id}/qualify/`, {
    method: 'POST',
    body: { reason },
    token,
  });
}

export async function rejectVendor(id: number, reason: string, token: string) {
  return apiRequest(`/vendor-profiles/${id}/reject/`, {
    method: 'POST',
    body: { reason },
    token,
  });
}

export async function acceptApplication(id: number, reason: string, token: string) {
  return apiRequest(`/vendor-profiles/${id}/accept_application/`, {
    method: 'POST',
    body: { reason },
    token,
  });
}

export async function findDuplicates(id: number, token: string) {
  return apiRequest(`/vendor-profiles/${id}/find_duplicates/`, {
    method: 'POST',
    token,
  });
}

export async function getFilteredVendors(filter: string, token: string) {
  return apiRequest<any[]>(`/vendors/filtered/${filter}/`, { token });
}

// Invoices
export async function getInvoices(
  token: string,
  filters?: {
    profile?: number;
    status?: string;
    market?: number;
  }
) {
  const params = new URLSearchParams();
  if (filters?.profile) params.append('profile', String(filters.profile));
  if (filters?.status) params.append('status', filters.status);
  if (filters?.market) params.append('market', String(filters.market));

  const query = params.toString();
  const endpoint = `/invoices/${query ? '?' + query : ''}`;
  return apiRequest<any[]>(endpoint, { token });
}

export async function getInvoice(id: number, token: string) {
  return apiRequest<any>(`/invoices/${id}/`, { token });
}

export async function createInvoice(data: Record<string, any>, token: string) {
  return apiRequest(`/invoices/`, {
    method: 'POST',
    body: data,
    token,
  });
}

export async function updateInvoice(
  id: number,
  data: Record<string, any>,
  token: string
) {
  return apiRequest(`/invoices/${id}/`, {
    method: 'PATCH',
    body: data,
    token,
  });
}

export async function sendInvoice(id: number, token: string) {
  return apiRequest(`/invoices/${id}/send/`, {
    method: 'POST',
    token,
  });
}

export async function recordPayment(
  invoiceId: number,
  payment: Record<string, any>,
  token: string
) {
  return apiRequest(`/invoices/${invoiceId}/record_payment/`, {
    method: 'POST',
    body: payment,
    token,
  });
}

// Payments
export async function getPayments(
  token: string,
  filters?: {
    invoice?: number;
    profile?: number;
  }
) {
  const params = new URLSearchParams();
  if (filters?.invoice) params.append('invoice', String(filters.invoice));
  if (filters?.profile) params.append('profile', String(filters.profile));

  const query = params.toString();
  const endpoint = `/payments/${query ? '?' + query : ''}`;
  return apiRequest<any[]>(endpoint, { token });
}

// Bookings
export async function getBookings(
  token: string,
  filters?: {
    profile?: number;
    market?: number;
    status?: string;
  }
) {
  const params = new URLSearchParams();
  if (filters?.profile) params.append('profile', String(filters.profile));
  if (filters?.market) params.append('market', String(filters.market));
  if (filters?.status) params.append('status', filters.status);

  const query = params.toString();
  const endpoint = `/bookings/${query ? '?' + query : ''}`;
  return apiRequest<any[]>(endpoint, { token });
}

export async function getBooking(id: number, token: string) {
  return apiRequest<any>(`/bookings/${id}/`, { token });
}

export async function checkInVendor(
  bookingId: number,
  day: 'saturday' | 'sunday',
  token: string
) {
  return apiRequest(`/bookings/${bookingId}/check_in/`, {
    method: 'POST',
    body: { day },
    token,
  });
}

// Attendance
export async function getAttendance(
  token: string,
  filters?: {
    market?: number;
  }
) {
  const params = new URLSearchParams();
  if (filters?.market) params.append('market', String(filters.market));

  const query = params.toString();
  const endpoint = `/attendance/${query ? '?' + query : ''}`;
  return apiRequest<any[]>(endpoint, { token });
}

export async function updateAttendance(
  id: number,
  data: Record<string, any>,
  token: string
) {
  return apiRequest(`/attendance/${id}/`, {
    method: 'PATCH',
    body: data,
    token,
  });
}

// Activities
export async function getActivities(
  token: string,
  filters?: {
    profile?: number;
    type?: string;
  }
) {
  const params = new URLSearchParams();
  if (filters?.profile) params.append('profile', String(filters.profile));
  if (filters?.type) params.append('type', filters.type);

  const query = params.toString();
  const endpoint = `/activities/${query ? '?' + query : ''}`;
  return apiRequest<any[]>(endpoint, { token });
}

// Markets
export async function getMarkets(
  token: string,
  filters?: {
    status?: string;
  }
) {
  const params = new URLSearchParams();
  if (filters?.status) params.append('status', filters.status);

  const query = params.toString();
  const endpoint = `/markets/${query ? '?' + query : ''}`;
  return apiRequest<any[]>(endpoint, { token });
}

export async function getMarket(id: number, token: string) {
  return apiRequest<any>(`/markets/${id}/`, { token });
}

export async function createMarket(data: Record<string, any>, token: string) {
  return apiRequest(`/markets/`, {
    method: 'POST',
    body: data,
    token,
  });
}

// Dashboard
export async function getDashboard(token: string) {
  return apiRequest<any>(`/dashboard/`, { token });
}

// Tasks
export async function getTasks(token: string, filters?: { profile?: number }) {
  const params = new URLSearchParams();
  if (filters?.profile) params.append('profile', String(filters.profile));

  const query = params.toString();
  const endpoint = `/tasks/${query ? '?' + query : ''}`;
  return apiRequest<any[]>(endpoint, { token });
}

export async function createTask(data: Record<string, any>, token: string) {
  return apiRequest(`/tasks/`, {
    method: 'POST',
    body: data,
    token,
  });
}

export async function updateTask(
  id: number,
  data: Record<string, any>,
  token: string
) {
  return apiRequest(`/tasks/${id}/`, {
    method: 'PATCH',
    body: data,
    token,
  });
}
