import { questionnaire } from '$lib/vendor-questionnaire';

export function leadPayload(form: FormData) {
		const fields = ['instagram_handle', 'business_name', 'first_name', 'last_name', 'email', 'phone_number', 'vendor_category', 'lead_source', 'interest_level', 'next_followup', 'notes', 'agreed_weekend_dates'];
		const payload: Record<string, string | string[] | boolean | null> = Object.fromEntries(fields.map((field) => [field, String(form.get(field) ?? '').trim() || (field === 'next_followup' ? null : '')]));
        for (const question of questionnaire.flatMap((section) => section.questions)) {
            const value = String(form.get(question.name) ?? '').trim();
            payload[question.name] = question.type === 'checkbox-group' || question.type === 'multi-date'
                ? form.getAll(question.name).map(String).map((item) => item.trim()).filter(Boolean)
                : question.type === 'checkbox'
                ? form.has(question.name)
                : value || (['datetime-local', 'date', 'number'].includes(question.type) ? null : '');
        }
    return payload;
}
