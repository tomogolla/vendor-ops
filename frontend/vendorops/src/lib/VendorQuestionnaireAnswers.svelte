<script lang="ts">
  import { questionnaire } from '$lib/vendor-questionnaire';
  import type { VendorLead } from '$lib/vendor-leads';
  let { lead, localTime = false }: { lead: VendorLead; localTime?: boolean } = $props();
  function answer(name: string) {
    const value = lead[name as keyof VendorLead];
    if (typeof value === 'boolean') return value ? 'Checked' : 'Not checked';
    if (value === '' || value == null) return 'Not answered';
    if (name === 'call_at') return localTime ? new Date(String(value)).toLocaleString() : String(value);
    if (name === 'offer_interest') return `${value} / 5`;
    if (name === 'agreed_weekend_dates') return String(value).split(' | ').join('\n');
    return String(value);
  }
</script>

<details>
  <summary>View call questionnaire</summary>
  {#each questionnaire as section}
    <h3>{section.title}</h3>
    <dl>
      {#each section.questions as question}<dt>{question.label}</dt><dd>{answer(question.name)}</dd>{/each}
    </dl>
  {/each}
  <p><strong>Additional Rep Notes / Observations</strong></p>
  <p>{lead.notes || 'Not answered'}</p>
</details>

<style>
  details { white-space: normal; min-width: 220px; margin-top: 12px; }
  summary { cursor: pointer; color: #004aad; font-weight: 600; }
  summary:focus-visible { outline: 2px solid #004aad; outline-offset: 3px; }
  h3 { font-size: 14px; margin-top: 20px; }
  dt { font-weight: 600; margin-top: 12px; }
  dd { margin: 4px 0 0; white-space: pre-wrap; }
</style>
