<script lang="ts">
  import { enhance } from "$app/forms";
  import type { SubmitFunction } from "@sveltejs/kit";
  import { tick } from "svelte";
  import type { VendorEmailTemplate } from "$lib/vendor-email-templates";

  let { businessName, recipient, onsent }: {
    businessName: string;
    recipient: string;
    onsent: () => void;
  } = $props();
  let dialog = $state<HTMLDialogElement>();
  let selected = $state<VendorEmailTemplate | null>(null);
  let subject = $state("");
  let body = $state("");
  let sending = $state(false);
  let errors = $state<Record<string, string[]>>({});

  export function open(template: VendorEmailTemplate) {
    selected = template;
    subject = template.subject;
    body = template.body.replaceAll("[Vendor Name]", businessName);
    errors = {};
    dialog?.showModal();
  }

  const submit: SubmitFunction = () => {
    sending = true;
    errors = {};
    return async ({ result, update }) => {
      try {
        if (result.type === "success") {
          await update();
          dialog?.close();
          onsent();
        } else if (result.type === "failure") {
          errors = (result.data?.errors as Record<string, string[]>) ?? {
            non_field_errors: ["Unable to send the email."],
          };
          await tick();
          dialog?.querySelector<HTMLElement>(".error-summary")?.focus();
        } else {
          errors = { non_field_errors: ["Unable to send the email. Please try again."] };
        }
      } finally {
        sending = false;
      }
    };
  };
</script>

<dialog bind:this={dialog} aria-labelledby="sequence-email-title" oncancel={(event) => { if (sending) event.preventDefault(); }}>
  {#if selected}
    <div class="heading">
      <div>
        <p class="eyebrow">THE GOOD FLEA · EMAIL SEQUENCE</p>
        <h2 id="sequence-email-title">{selected.title}</h2>
      </div>
      <button type="button" class="close" aria-label="Close email draft" disabled={sending} onclick={() => dialog?.close()}>×</button>
    </div>

    {#if Object.keys(errors).length}
      <div class="error-summary" role="alert" tabindex="-1">
        <strong>The email was not sent.</strong>
        <ul>{#each Object.entries(errors) as [field, messages]}{#each messages as message}<li>{field === "non_field_errors" ? "" : `${field.replaceAll("_", " ")}: `}{message}</li>{/each}{/each}</ul>
      </div>
    {/if}

    <form method="POST" action="?/sendSequenceEmail" use:enhance={submit}>
      <input type="hidden" name="template_id" value={selected.id} />
      <div class="recipient"><span>To</span><strong>{recipient || "No vendor email on file"}</strong></div>
      <fieldset disabled={sending}>
        <label for="sequence-subject">Subject
          <input id="sequence-subject" name="subject" bind:value={subject} maxlength="255" required />
        </label>
        <label for="sequence-body">Message
          <textarea id="sequence-body" name="body" bind:value={body} maxlength="10000" required rows="12"></textarea>
        </label>
      </fieldset>
      <section class="preview" aria-label="Email preview">
        <div class="preview-heading"><strong>Preview</strong><span>{businessName}</span></div>
        <p class="preview-subject">{subject || "No subject"}</p>
        <pre>{body || "No message"}</pre>
      </section>
      <div class="actions">
        <button type="button" disabled={sending} onclick={() => dialog?.close()}>Cancel</button>
        <button class="send" type="submit" disabled={sending || !recipient}>{sending ? "Sending…" : "Send email"}</button>
      </div>
    </form>
  {/if}
</dialog>

<style>
  dialog { box-sizing: border-box; width: min(700px, calc(100% - 32px)); max-height: calc(100dvh - 32px); overflow: auto; border: 1px solid #d8dce4; border-radius: 8px; padding: 24px; color: #26262c; box-shadow: 0 24px 70px #15243755; }
  dialog::backdrop { background: #182637aa; }
  .heading { display: flex; justify-content: space-between; gap: 16px; align-items: start; margin-bottom: 16px; }
  .eyebrow { margin: 0 0 7px; color: #818390; font-size: 10px; }
  h2 { margin: 0; font-size: 18px; }
  .recipient { display: grid; grid-template-columns: 42px 1fr; gap: 10px; margin-bottom: 16px; padding: 10px 12px; border: 1px solid #dedfe5; border-radius: 6px; background: #f8f9fb; font-size: 12px; }
  .recipient span { color: #818390; }
  .recipient strong { overflow-wrap: anywhere; }
  fieldset { display: grid; gap: 14px; border: 0; padding: 0; margin: 0; }
  label { display: grid; gap: 6px; font-size: 12px; font-weight: 600; }
  input, textarea { box-sizing: border-box; width: 100%; border: 1px solid #cbd1da; border-radius: 6px; padding: 9px 10px; color: #26262c; background: white; font: inherit; font-size: 12px; font-weight: 400; }
  textarea { min-height: 170px; resize: vertical; line-height: 1.5; }
  .preview { margin-top: 16px; border: 1px solid #dedfe5; border-radius: 6px; overflow: hidden; }
  .preview-heading { display: flex; justify-content: space-between; gap: 12px; padding: 9px 11px; background: #fff2bc; color: #39352a; font-size: 11px; }
  .preview-heading span { overflow-wrap: anywhere; }
  .preview-subject { margin: 0; padding: 11px; border-bottom: 1px solid #e7e8ec; color: #26262c; font-size: 12px; font-weight: 700; overflow-wrap: anywhere; }
  pre { max-height: 230px; overflow: auto; margin: 0; padding: 12px; color: #4f5360; font: inherit; font-size: 12px; line-height: 1.5; white-space: pre-wrap; overflow-wrap: anywhere; }
  .actions { display: flex; justify-content: end; gap: 9px; border-top: 1px solid #e4e6eb; padding-top: 16px; margin-top: 18px; }
  button { width: auto; border: 1px solid #d0d4db; border-radius: 6px; padding: 9px 14px; background: white; color: #26262c; font: inherit; font-size: 12px; cursor: pointer; }
  button.send { border-color: #004aad; background: #004aad; color: white; font-weight: 600; }
  button.close { border: 0; padding: 0 4px; font-size: 24px; }
  button:disabled { opacity: .55; cursor: wait; }
  button:focus-visible, input:focus-visible, textarea:focus-visible { outline: 2px solid #004aad; outline-offset: 2px; }
  .error-summary { margin-bottom: 14px; padding: 11px; border-radius: 6px; background: #fff0ed; color: #922218; font-size: 12px; }
  .error-summary ul { margin-bottom: 0; padding-left: 20px; }
  @media (max-width: 560px) { dialog { padding: 17px; } }
</style>