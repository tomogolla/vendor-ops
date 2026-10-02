import { questionnaire } from '$lib/vendor-questionnaire';

export function leadPayload(form: FormData) {
		const fields = ['instagram_handle', 'business_name', 'first_name', 'last_name', 'email', 'phone_number', 'vendor_category', 'lead_source', 'interest_level', 'next_followup', 'notes'];
		const payload: Record<string, string | boolean | null> = Object.fromEntries(fields.map((field) => [field, String(form.get(field) ?? '').trim() || (field === 'next_followup' ? null : '')]));
        for (const question of questionnaire.flatMap((section) => section.questions)) {
            const value = String(form.get(question.name) ?? '').trim();
            payload[question.name] = question.type === 'checkbox'
                ? form.has(question.name)
                : value || (question.type === 'datetime-local' || question.name === 'offer_interest' ? null : '');
        }
    return payload;
}
