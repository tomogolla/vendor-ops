<script lang="ts">
  import { questionnaire } from '$lib/vendor-questionnaire';
  import WeekendMultiSelect from '$lib/WeekendMultiSelect.svelte';
  import MarketDatePicker from '$lib/MarketDatePicker.svelte';
  import type { VendorLead } from '$lib/vendor-leads';
  let { errors = {}, initial }: { errors?: Record<string, string[]>; initial?: VendorLead } = $props();
  const saved = (name: string) => initial?.[name as keyof VendorLead];
</script>

{#each questionnaire as section, index}
  <section aria-labelledby={`questionnaire-section-${index}`}>
    <h3 id={`questionnaire-section-${index}`}>{section.title}</h3>
    {#if section.description}<p class="script">{section.description}</p>{/if}
    <div class="questions">
      {#each section.questions as question}
        <div class:wide={['textarea', 'checkbox', 'multi-select', 'checkbox-group', 'multi-date'].includes(question.type)}>
          {#if ['multi-select', 'checkbox-group', 'multi-date'].includes(question.type)}
            <span class="field-label" id={`${question.name}-label`}>{question.label}</span>
          {:else}
            <label for={question.name} class:checkbox={question.type === 'checkbox'}>
              {#if question.type === 'checkbox'}<input id={question.name} name={question.name} type="checkbox" checked={Boolean(saved(question.name))} />{/if}
              {question.label}{question.required ? ' *' : ''}
            </label>
          {/if}
          {#if question.description}<p class="description" id={`${question.name}-description`}>{question.description}</p>{/if}
          {#if question.type === 'multi-date'}
            <MarketDatePicker name={question.name} initial={Array.isArray(saved(question.name)) ? saved(question.name) as string[] : []} invalid={Boolean(errors[question.name])} labelId={`${question.name}-label`} />
          {:else if question.type === 'checkbox-group'}
            <div class="checkbox-options" role="group" aria-labelledby={`${question.name}-label`} aria-describedby={question.description ? `${question.name}-description` : undefined}>
              {#each question.options ?? [] as option}
                <label class="checkbox"><input type="checkbox" name={question.name} value={option} aria-invalid={errors[question.name] ? 'true' : undefined} checked={Array.isArray(saved(question.name)) && (saved(question.name) as string[]).includes(option)} />{option}</label>
              {/each}
            </div>
          {:else if question.type === 'multi-select'}
            <WeekendMultiSelect name={question.name} options={question.options ?? []} initial={String(saved(question.name) ?? '')} invalid={Boolean(errors[question.name])} labelId={`${question.name}-label`} />
          {:else if question.type === 'select'}
            <select id={question.name} name={question.name} value={String(saved(question.name) ?? '')} aria-describedby={question.description ? `${question.name}-description` : undefined} aria-invalid={errors[question.name] ? 'true' : undefined}>
              <option value="">Not answered</option>
              {#each question.options ?? [] as option}<option value={question.name === 'offer_interest' ? option[0] : option}>{option}</option>{/each}
            </select>
          {:else if question.type === 'textarea'}
            <textarea id={question.name} name={question.name} rows="3" maxlength="10000" value={String(saved(question.name) ?? '')} aria-describedby={question.description ? `${question.name}-description` : undefined} aria-invalid={errors[question.name] ? 'true' : undefined}></textarea>
          {:else if question.type !== 'checkbox'}
            <input id={question.name} name={question.name} type={question.type} maxlength={question.max} required={question.required} min={question.type === 'number' ? 0 : undefined} step={question.type === 'number' ? '0.01' : undefined} value={question.type === 'datetime-local' ? '' : String(saved(question.name) ?? '')} aria-describedby={question.description ? `${question.name}-description` : undefined} aria-invalid={errors[question.name] ? 'true' : undefined} />
          {/if}
        </div>
      {/each}
    </div>
  </section>
{/each}

<style>
  section { margin-top: 28px; padding-top: 20px; border-top: 1px solid #dbe5f7; }
  h3 { font-size: 17px; margin: 0 0 16px; }
  .script { background: #eef4ff; border-left: 3px solid #004aad; padding: 14px; font-size: 14px; line-height: 1.6; color: #244576; }
  .questions { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .questions > div { min-width: 0; }
  .wide { grid-column: 1 / -1; }
  label, .field-label { display: block; margin-bottom: 8px; font-size: 13px; font-weight: 600; }
  .description { font-size: 13px; line-height: 1.5; color: #4c6080; margin: 0 0 8px; }
  input, select, textarea { box-sizing: border-box; width: 100%; padding: 11px 12px; border: 1px solid #99b7f5; border-radius: 7px; background: white; color: #20352f; font: inherit; font-size: 13px; }
  textarea { resize: vertical; }
  .checkbox { display: flex; align-items: center; gap: 10px; }
  .checkbox-options { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
  input[type='checkbox'] { width: 18px; height: 18px; accent-color: #004aad; flex-shrink: 0; }
  input:focus-visible, select:focus-visible, textarea:focus-visible { outline: 2px solid #004aad; outline-offset: 2px; }
  [aria-invalid='true'] { border-color: #b42318; }
  @media (max-width: 560px) { .questions { grid-template-columns: 1fr; } }
</style>
