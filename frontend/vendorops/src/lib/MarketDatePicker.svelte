<script lang="ts">
  let { name, initial = [], invalid = false, labelId }: {
    name: string; initial?: string[]; invalid?: boolean; labelId: string;
  } = $props();
  let dates = $derived(initial.length ? [...initial] : ['']);
</script>

<div class="date-picker" role="group" aria-labelledby={labelId}>
  {#each dates as date, index}
    <div class="date-row">
      <input type="date" {name} value={date} aria-label={`Target market date ${index + 1}`} aria-invalid={invalid ? 'true' : undefined} onchange={(event) => { dates = dates.map((value, i) => i === index ? event.currentTarget.value : value); }} />
      <button type="button" aria-label={`Remove market date ${index + 1}`} onclick={() => { dates = dates.length === 1 ? [''] : dates.filter((_, i) => i !== index); }}>Remove</button>
    </div>
  {/each}
  <button type="button" disabled={dates.length >= 100} onclick={() => { dates = [...dates, '']; }}>+ Add date</button>
</div>

<style>
  .date-picker { display: grid; gap: 10px; }
  .date-row { display: flex; gap: 8px; }
  input { min-width: 0; flex: 1; border: 1px solid #99b7f5; border-radius: 7px; padding: 11px 12px; font: inherit; font-size: 13px; background: white; color: #20352f; }
  button { border: 1px solid #99b7f5; border-radius: 7px; padding: 8px 12px; font: inherit; font-size: 13px; background: white; color: #004aad; cursor: pointer; justify-self: start; }
  button:disabled { opacity: .6; cursor: default; }
  [aria-invalid='true'] { border-color: #b42318; }
  input:focus-visible, button:focus-visible { outline: 2px solid #004aad; outline-offset: 2px; }
</style>
