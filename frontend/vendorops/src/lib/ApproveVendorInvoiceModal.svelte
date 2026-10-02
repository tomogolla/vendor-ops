<script lang="ts">
  import { enhance } from '$app/forms';
  import type { SubmitFunction } from '@sveltejs/kit';
  import { tick } from 'svelte';
  import type { VendorLead } from '$lib/vendor-leads';

  let { lead, onsent }: { lead: VendorLead; onsent: () => void } = $props();
  let dialog = $state<HTMLDialogElement>();
  let sending = $state(false);
  let errors = $state<Record<string, string[]>>({});

  export function open() {
    errors = {};
    dialog?.showModal();
  }

  const submit: SubmitFunction = () => {
    sending = true;
    errors = {};
    return async ({ result, update }) => {
      try {
        if (result.type === 'success') {
          await update();
          dialog?.close();
          onsent();
        } else if (result.type === 'failure') {
          errors = (result.data?.errors as Record<string, string[]>) ?? { non_field_errors: ['Unable to send the invoice.'] };
          await tick();
          dialog?.querySelector<HTMLElement>('.error-summary')?.focus();
        } else {
          errors = { non_field_errors: ['Unable to send the invoice. Please try again.'] };
        }
      } finally {
        sending = false;
      }
    };
  };
</script>

<dialog bind:this={dialog} aria-labelledby="approve-invoice-title" oncancel={(event) => { if (sending) event.preventDefault(); }}>
  <div class="heading">
    <div>
      <p class="eyebrow">THE GOOD FLEA · VENDOR APPLICATION</p>
      <h2 id="approve-invoice-title">Approve vendor and send invoice</h2>
    </div>
    <button type="button" class="close" aria-label="Close invoice modal" disabled={sending} onclick={() => dialog?.close()}>×</button>
  </div>
  <p class="intro">Review the booking and invoice details before emailing {lead.business_name}. Sending this invoice approves the application.</p>

  {#if Object.keys(errors).length}
    <div class="error-summary" role="alert" tabindex="-1">
      <strong>The invoice was not sent.</strong>
      <ul>{#each Object.entries(errors) as [field, messages]}{#each messages as message}<li>{field === 'non_field_errors' ? '' : `${field.replaceAll('_', ' ')}: `}{message}</li>{/each}{/each}</ul>
    </div>
  {/if}

  <form method="POST" action="?/approveInvoice" use:enhance={submit}>
    <div class="summary">
      <div><span>From</span><strong>booking@thegoodflea.com</strong></div>
      <div><span>To</span><strong>{lead.email || 'No vendor email on file'}</strong></div>
      <div><span>Business</span><strong>{lead.business_name}</strong></div>
      <div><span>Agreed weekends</span><strong>{lead.agreed_weekend_dates ? lead.agreed_weekend_dates.replaceAll(' | ', ', ') : 'To be confirmed'}</strong></div>
    </div>
    <fieldset disabled={sending}>
      <div class="fields">
        <label for="invoice-amount">Invoice amount (USD) *
          <input id="invoice-amount" name="amount" type="number" min="0" step="0.01" inputmode="decimal" placeholder="0.00" required aria-invalid={errors.amount ? 'true' : undefined} />
        </label>
        <label for="invoice-due">Due date *
          <input id="invoice-due" name="due_date" type="date" required aria-invalid={errors.due_date ? 'true' : undefined} />
        </label>
        <label class="full" for="invoice-link">Secure invoice link *
          <input id="invoice-link" name="invoice_link" type="url" maxlength="2048" pattern="https://.*" placeholder="https://payments.example.com/invoice/…" required aria-invalid={errors.invoice_link ? 'true' : undefined} />
        </label>
      </div>
    </fieldset>
    <p class="send-note">An invoice number is assigned when the email is sent. The approval is saved only if the mail backend reports success.</p>
    <div class="actions">
      <button type="button" disabled={sending} onclick={() => dialog?.close()}>Cancel</button>
      <button class="send" type="submit" disabled={sending || !lead.email}>{sending ? 'Sending…' : 'Send invoice & approve'}</button>
    </div>
  </form>
</dialog>

<style>
  dialog { box-sizing: border-box; width: min(620px, calc(100% - 32px)); max-height: calc(100dvh - 32px); border: 0; border-radius: 12px; padding: 24px; color: #26262c; box-shadow: 0 24px 70px #15243755; }
  dialog::backdrop { background: #182637aa; }
  .heading { display: flex; justify-content: space-between; gap: 16px; align-items: start; }
  .eyebrow { margin: 0 0 8px; color: #818390; font-size: 11px; letter-spacing: .05em; }
  h2 { margin: 0; font-size: 21px; }
  .intro, .send-note { color: #666b77; font-size: 13px; line-height: 1.5; }
  .intro { margin: 14px 0 20px; }
  .summary { display: grid; gap: 12px; padding: 16px; border: 1px solid #dedfe5; border-radius: 8px; background: #f8f9fb; margin-bottom: 20px; }
  .summary div { display: grid; grid-template-columns: 130px 1fr; gap: 10px; font-size: 12px; }
  .summary span { color: #818390; }
  .summary strong { overflow-wrap: anywhere; font-weight: 600; }
  fieldset { border: 0; padding: 0; margin: 0; }
  .fields { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  label { display: flex; flex-direction: column; gap: 7px; font-size: 12px; font-weight: 600; }
  .full { grid-column: 1 / -1; }
  input { box-sizing: border-box; width: 100%; padding: 10px 12px; border: 1px solid #cbd1da; border-radius: 6px; color: #26262c; background: white; font: inherit; font-size: 13px; font-weight: 400; }
  [aria-invalid='true'] { border-color: #b42318; }
  .send-note { margin: 16px 0; }
  .actions { display: flex; justify-content: end; gap: 10px; border-top: 1px solid #e4e6eb; padding-top: 18px; }
  button { border: 1px solid #d0d4db; border-radius: 6px; padding: 10px 16px; background: white; color: #26262c; font: inherit; font-size: 12px; cursor: pointer; }
  button.send { border-color: #004aad; background: #004aad; color: white; font-weight: 600; }
  button.close { border: 0; font-size: 25px; padding: 0 5px; }
  button:disabled { opacity: .55; cursor: wait; }
  button:focus-visible, input:focus-visible { outline: 2px solid #004aad; outline-offset: 2px; }
  .error-summary { background: #fff0ed; color: #922218; border-radius: 6px; padding: 12px; font-size: 12px; margin-bottom: 16px; }
  .error-summary ul { margin-bottom: 0; padding-left: 20px; }
  @media (max-width: 560px) { dialog { padding: 18px; } .fields { grid-template-columns: 1fr; } .summary div { grid-template-columns: 1fr; gap: 3px; } }
</style>
