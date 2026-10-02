<script lang="ts">
  import { tick, onMount } from "svelte";
  import VendorQuestionnaire from "$lib/VendorQuestionnaire.svelte";
  import { enhance } from "$app/forms";
  import { resolve } from "$app/paths";
  import type { SubmitFunction } from "@sveltejs/kit";

  import type { VendorLead } from "$lib/vendor-leads";

  let {
    categories,
    sources,
    onsaved,
    inline = false,
    initial,
    action,
    edit = false,
  }: { categories: string[]; sources: string[]; onsaved: () => void; inline?: boolean; initial?: VendorLead; action?: string; edit?: boolean } =
    $props();
  let dialog = $state<HTMLDialogElement>();
  let formNode: HTMLFormElement;
  const localDate = (value: string) => {
    const date = new Date(value);
    return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  };
  onMount(() => {
    if (!initial) return;
    for (const input of formNode.querySelectorAll<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>("input, select, textarea")) {
      if (!(input instanceof HTMLInputElement && input.type === 'datetime-local')) continue;
      const value = initial[input.name as keyof VendorLead];
      input.value = value == null ? '' : localDate(String(value));
    }
    followup = initial.next_followup ? localDate(initial.next_followup) : '';
  });
  let saving = $state(false);
  let errors = $state<Record<string, string[]>>({});
  let followup = $state("");
  const contacts = [
    {
      name: "instagram_handle",
      label: "Instagram handle",
      placeholder: "@instagram_handle",
      type: "text",
      max: 31,
    },
    {
      name: "business_name",
      label: "Lead Business / Brand Name",
      placeholder: "Business name",
      type: "text",
      max: 200,
    },
    {
      name: "first_name",
      label: "First name",
      placeholder: "First name",
      type: "text",
      max: 100,
    },
    {
      name: "last_name",
      label: "Last name",
      placeholder: "Last name",
      type: "text",
      max: 100,
    },
    {
      name: "email",
      label: "Email",
      placeholder: "name@example.com",
      type: "email",
      max: 254,
    },
    {
      name: "phone_number",
      label: "Phone number",
      placeholder: "+1 555 123 4567",
      type: "tel",
      max: 40,
    },
  ];

  export function open() {
    errors = {};
    dialog?.showModal();
  }

  const submit: SubmitFunction = ({ formData, formElement }) => {
    for (const input of formElement.querySelectorAll<HTMLInputElement>('input[type="datetime-local"]')) {
      formData.set(input.name, input.value ? new Date(input.value).toISOString() : "");
    }
    saving = true;
    errors = {};
    formData.set(
      "next_followup",
      followup ? new Date(followup).toISOString() : "",
    );
    return async ({ result, update }) => {
      try {
        if (result.type === "success") {
          await update({ reset: !inline });
          if (!inline) {
            followup = "";
            dialog?.close();
          }
          onsaved();
        } else if (result.type === "failure") {
          errors = (result.data?.errors as Record<string, string[]>) ?? {
            non_field_errors: ["Unable to save the lead."],
          };
        } else {
          errors = {
            non_field_errors: ["Unable to save the lead. Please try again."],
          };
        }
      } finally {
        saving = false;
        if (Object.keys(errors).length) {
          await tick();
          formNode.querySelector<HTMLElement>(".error-summary")?.focus();
        }
      }
    };
  };
</script>

{#snippet content()}
  <div class="modal-heading">
    <div>
      <p class="eyebrow"></p>
      <h2 id="lead-modal-title">{inline ? "Vendor lead details" : edit ? "Edit vendor profile" : "Add vendor lead"}</h2>
    </div>
    {#if !inline}<button
      class="close"
      type="button"
      aria-label="Close add vendor lead"
      disabled={saving}
      onclick={() => dialog?.close()}>×</button
    >{/if}
  </div>
  <form
    bind:this={formNode}
    method="POST"
    action={action ?? `${resolve("/vendors")}?/create`}
    use:enhance={submit}
  >
    <p class="hint">
      Fields marked * are required. Add at least one contact method: Instagram,
      email, or phone. Call questionnaire answers are optional so incomplete calls can be saved.
    </p>
    {#if Object.keys(errors).length}
      <div class="error-summary" role="alert" tabindex="-1">
        <strong>The lead could not be saved.</strong>
        <ul>
          {#each Object.entries(errors) as [field, messages]}{#each messages as message}<li
              >
                {field === "non_field_errors"
                  ? ""
                  : `${field.replaceAll("_", " ")}: `}{message}
              </li>{/each}{/each}
        </ul>
      </div>
    {/if}
    <fieldset disabled={saving}>
      <legend>1. Call Header &amp; Lead Details</legend>
      <div class="fields">
        {#each contacts as field}
          <label for={field.name}>
            {field.label}{field.name === "business_name" ? " *" : ""}
            <input
              id={field.name}
              name={field.name}
              type={field.type}
              placeholder={field.placeholder}
              maxlength={field.max}
              required={field.name === "business_name"}
              value={initial ? String(initial[field.name as keyof VendorLead] ?? '') : ''}
              aria-invalid={errors[field.name] ? "true" : undefined}
            />
          </label>
        {/each}
        <label for="vendor_category"
          >Vendor category *
          <select
            id="vendor_category"
            name="vendor_category"
            required
            value={initial?.vendor_category ?? ''}
            aria-invalid={errors.vendor_category ? "true" : undefined}
          >
            <option value="">Select category</option>
            {#each categories as category}<option value={category}
                >{category}</option
              >{/each}
          </select>
        </label>
        <label for="lead_source"
          >Lead source *
          <select
            id="lead_source"
            name="lead_source"
            required
            value={initial?.lead_source ?? ''}
            aria-invalid={errors.lead_source ? "true" : undefined}
          >
            <option value="">Select source</option>
            {#each sources as source}<option value={source}>{source}</option
              >{/each}
          </select>
        </label>
        <label for="interest_level"
          >Interest level *
          <select
            id="interest_level"
            name="interest_level"
            required
            value={initial?.interest_level ?? ''}
            aria-invalid={errors.interest_level ? "true" : undefined}
          >
            <option value="">Select interest level</option>
            <option value="hot">Hot</option><option value="warm">Warm</option
            ><option value="cold">Cold</option>
          </select>
        </label>
      </div>
      <VendorQuestionnaire {errors} {initial} />
      <div class="fields followup-fields">
        <label for="next_followup"
          >Next follow-up date and time
          <input
            id="next_followup"
            name="next_followup"
            type="datetime-local"
            bind:value={followup}
            aria-invalid={errors.next_followup ? "true" : undefined}
          />
          <span class="hint">Your local timezone</span>
        </label>
        <label class="full-width" for="notes"
          >Additional Rep Notes / Observations
          <textarea
            id="notes"
            name="notes"
            rows="4"
            maxlength="10000"
            placeholder="What did you discuss? Include interests and next steps."
            value={initial?.notes ?? ''}
            aria-invalid={errors.notes ? "true" : undefined}
          ></textarea>
        </label>
      </div>
    </fieldset>
    <div class="actions">
      {#if !inline}<button type="button" disabled={saving} onclick={() => dialog?.close()}
        >Cancel</button
      >{/if}
      <button class="primary" type="submit" disabled={saving}
        >{saving ? "Saving…" : inline || edit ? "Save changes" : "Save vendor lead"}</button
      >
    </div>
  </form>
{/snippet}

{#if inline}
  <div class="inline-form">{@render content()}</div>
{:else}
  <dialog bind:this={dialog} aria-labelledby="lead-modal-title" oncancel={(event) => { if (saving) event.preventDefault(); }}>
    {@render content()}
  </dialog>
{/if}

<style>
  .inline-form { color: #26262c; }
  .inline-form h2 { font-size: 16px; }
  .inline-form .hint { color: #737582; }
  .inline-form :global(input), .inline-form :global(select), .inline-form :global(textarea) { border-color: #dedfe5; }
  .inline-form .actions { position: sticky; bottom: 0; background: white; padding-bottom: 12px; }

  dialog {
    box-sizing: border-box;
    width: min(720px, calc(100% - 32px));
    max-height: calc(100dvh - 32px);
    border: 0;
    border-radius: 16px;
    padding: 28px;
    color: #004aad;
    box-shadow: 0 24px 80px #0003;
  }
  /* dialog::backdrop { background: #fff089; } */
  .modal-heading {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
  }
  .eyebrow {
    margin: 0 0 8px;
    color: #99b7f5;
    font-size: 12px;
  }
  h2 {
    margin: 0;
    font-size: 26px;
  }
  .close {
    font-size: 26px;
    padding: 0 10px;
    border: 0;
  }
  .hint {
    color: #99b7f5;
    font-size: 12px;
    line-height: 1.5;
    font-weight: 400;
  }
  form > .hint {
    margin: 16px 0 24px;
  }
  fieldset {
    border: 0;
    padding: 0;
    margin: 0;
    min-width: 0;
  }
  legend { font-size: 17px; font-weight: 700; padding: 0 0 20px; }
  .followup-fields { margin-top: 20px; }
  .fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    min-width: 0;
  }
  input,
  select,
  textarea {
    box-sizing: border-box;
    width: 100%;
    border: 1px solid #99b7f5;
    border-radius: 7px;
    padding: 11px 12px;
    background: white;
    color: #20352f;
    font: inherit;
    font-weight: 400;
  }
  textarea {
    resize: vertical;
  }
  .full-width {
    grid-column: 1 / -1;
  }
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #e2e8e4;
  }
  button {
    border: 1px solid #99b7f5;
    border-radius: 7px;
    padding: 11px 16px;
    background: white;
    color: #20352f;
    font: inherit;
    cursor: pointer;
  }
  button.primary {
    color: white;
    background: #004aad;
    border-color: #004aad;
  }
  button:disabled {
    opacity: 0.6;
    cursor: wait;
  }
  input:focus-visible,
  select:focus-visible,
  textarea:focus-visible,
  button:focus-visible {
    outline: 2px solid #37795e;
    outline-offset: 2px;
  }
  [aria-invalid="true"] {
    border-color: #b42318;
  }
  .error-summary {
    padding: 14px;
    margin-bottom: 20px;
    background: #fff0ed;
    color: #922218;
    border-radius: 8px;
    font-size: 13px;
  }
  .error-summary ul {
    margin-bottom: 0;
    padding-left: 20px;
  }
  @media (max-width: 560px) {
    dialog {
      padding: 20px;
    }
    .fields {
      grid-template-columns: 1fr;
      gap: 16px;
    }
  }
</style>
