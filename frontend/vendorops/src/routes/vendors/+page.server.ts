import { getVendorProfiles } from '$lib/api-client';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies, url }) => {
  const token = cookies.get('auth_token');
  if (!token) return { status: 401, error: 'Not authenticated' };

  const status = url.searchParams.get('status');
  const search = url.searchParams.get('search');

  try {
    const res = await getVendorProfiles(token, { status: status || undefined, search: search || undefined });
    return { vendors: res.data || [], status, search };
  } catch (error) {
    return { error: 'Failed to load vendors', vendors: [], status, search };
  }
};
