import { leadPayload } from '$lib/server/lead-payload';
import { fail } from '@sveltejs/kit';
import { djangoApi } from '$lib/server/auth';
import type { Actions, PageServerLoad } from './$types';
import type { LeadData } from '$lib/vendor-leads';

const endpoint = () => `${djangoApi()}/api/vendor-leads/`;

export const load: PageServerLoad = async ({ fetch }) => {
	try {
		const response = await fetch(endpoint());
		if (!response.ok) throw new Error('Could not load vendor leads');
		const data: LeadData = await response.json();
		return { ...data, loadError: '' };
	} catch {
		return { leads: [], categories: [], sources: [], loadError: 'Unable to load vendor leads. Check that the Django server is running, then refresh.' };
	}
};

export const actions: Actions = {
	create: async ({ request, fetch }) => {
		const form = await request.formData();
		const payload = leadPayload(form);
		try {
			const response = await fetch(endpoint(), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});
			if (response.status === 400) {
				const errors: Record<string, string[]> = await response.json();
				return fail(400, { success: false, errors });
			}
			if (!response.ok) throw new Error('Save failed');
			return { success: true, errors: {} as Record<string, string[]> };
		} catch {
			return fail(503, { success: false, errors: { non_field_errors: ['Unable to save the lead. Please try again.'] } });
		}
	}
};
