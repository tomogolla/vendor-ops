import { fail } from '@sveltejs/kit';
import { djangoApi } from '$lib/server/auth';
import type { VendorLead } from '$lib/vendor-leads';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
  try {
    const response = await fetch(`${djangoApi()}/api/applications/`);
    if (!response.ok) throw new Error('Applications unavailable');
    return { ...(await response.json() as { applications: VendorLead[] }), loadError: '' };
  } catch {
    return { applications: [], loadError: 'Unable to load applications. Check that Django is running, then refresh.' };
  }
};

export const actions: Actions = {
  importCsv: async ({ request, fetch }) => {
    const incoming = await request.formData();
    const file = incoming.get('file');
    if (!(file instanceof File) || file.size === 0) {
      return fail(400, { importResult: null, importErrors: ['Choose a CSV file to upload.'] });
    }
    const payload = new FormData();
    payload.set('file', file);
    try {
      const response = await fetch(`${djangoApi()}/api/applications/import-csv/`, { method: 'POST', body: payload });
      const result = await response.json();
      if (!response.ok) {
        return fail(response.status, { importResult: null, importErrors: result.file ?? result.non_field_errors ?? ['Unable to import the CSV.'] });
      }
      return { importResult: result as ImportResult, importErrors: [] as string[] };
    } catch {
      return fail(503, { importResult: null, importErrors: ['Unable to reach the import service. Please try again.'] });
    }
  }
};

type ImportResult = {
  created: Array<{ id: number; instagram_handle: string }>;
  skipped: Array<{ row: number; instagram_handle: string; reason: string }>;
  errors: Array<{ row: number; message: string }>;
};
