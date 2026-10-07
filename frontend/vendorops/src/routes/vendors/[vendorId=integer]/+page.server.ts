import { error, fail } from '@sveltejs/kit';
import { leadPayload } from '$lib/server/lead-payload';
import { djangoApi } from '$lib/server/auth';
import type { VendorLead } from '$lib/vendor-leads';
import type { Actions, PageServerLoad } from './$types';

const endpoint = (id: string) => `${djangoApi()}/api/vendor-leads/${id}/`;

export const load: PageServerLoad = async ({ params, fetch }) => {
  let response: Response;
  try { response = await fetch(endpoint(params.vendorId)); }
  catch { error(503, 'Unable to load this lead. Check that Django is running.'); }
  if (response.status === 404) error(404, 'Vendor lead not found.');
  if (!response.ok) error(503, 'Unable to load this lead. Please try again.');
  return await response.json() as { lead: VendorLead; invoice: ApprovalInvoice | null; categories: string[]; sources: string[] };
};

type ApprovalInvoice = {
  number: string;
  recipient_email: string;
  amount: string;
  currency: string;
  due_date: string;
  invoice_link: string;
  weekend_dates: string;
  sent_at: string;
};

export const actions: Actions = {
  approveInvoice: async ({ params, request, fetch }) => {
    const form = await request.formData();
    const payload = Object.fromEntries(['amount', 'due_date', 'invoice_link'].map((field) => [field, String(form.get(field) ?? '').trim()]));
    try {
      const response = await fetch(`${endpoint(params.vendorId)}approve-invoice/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      });
      if ([400, 409, 502, 503].includes(response.status)) {
        return fail(response.status, { success: false, errors: await response.json() as Record<string, string[]> });
      }
      if (!response.ok) throw new Error('Invoice send failed');
      return { success: true, errors: {} as Record<string, string[]> };
    } catch {
      return fail(503, { success: false, errors: { non_field_errors: ['Unable to reach the invoice service. Please try again.'] } });
    }
  },
  sendSequenceEmail: async ({ params, request, fetch }) => {
    const form = await request.formData();
    const payload = Object.fromEntries(['template_id', 'subject', 'body'].map((field) => [field, String(form.get(field) ?? '').trim()]));
    try {
      const response = await fetch(`${endpoint(params.vendorId)}email-sequence/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
      });
      if ([400, 404, 502, 503].includes(response.status)) {
        return fail(response.status, { success: false, errors: await response.json() as Record<string, string[]> });
      }
      if (!response.ok) throw new Error('Sequence email send failed');
      return { success: true, errors: {} as Record<string, string[]> };
    } catch {
      return fail(503, { success: false, errors: { non_field_errors: ['Unable to reach the email service. Please try again.'] } });
    }
  },
  update: async ({ params, request, fetch }) => {
    const form = await request.formData();
    const section = String(form.get('section') ?? 'lead');
    let payload: Record<string, unknown>;
    if (section === 'documents') {
      payload = Object.fromEntries(['vendor_contract', 'coi', 'info_packet'].map((key) => [key, form.has(key)]));
    } else if (section === 'decision') {
      const decision = String(form.get('application_decision'));
      if (!['accepted', 'waitlisted', 'declined'].includes(decision)) {
        return fail(400, { success: false, section, errors: { application_decision: ['Choose a valid decision.'] } });
      }
      payload = { application_decision: decision };
    } else if (section === 'lead') {
      payload = leadPayload(form);
    } else {
      return fail(400, { success: false, section, errors: { non_field_errors: ['Unknown profile section.'] } });
    }
    try {
      const response = await fetch(endpoint(params.vendorId), { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
      if (response.status === 400 || response.status === 409) return fail(response.status, { success: false, section, errors: await response.json() as Record<string, string[]> });
      if (!response.ok) throw new Error('Save failed');
      return { success: true, section, errors: {} as Record<string, string[]> };
    } catch {
      return fail(503, { success: false, section, errors: { non_field_errors: ['Unable to save changes. Please try again.'] } });
    }
  }
};
