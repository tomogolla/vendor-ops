<script lang="ts">
  import { enhance } from "$app/forms";
  import { resolve } from "$app/paths";
  import type { SubmitFunction } from "@sveltejs/kit";
  import AddVendorLeadModal from "$lib/AddVendorLeadModal.svelte";
  import CreateInvoiceModal from "$lib/CreateInvoiceModal.svelte";
  import ApproveVendorInvoiceModal from "$lib/ApproveVendorInvoiceModal.svelte";
  import VendorEmailSequenceModal from "$lib/VendorEmailSequenceModal.svelte";
  import TabPanel from "$lib/TabPanel.svelte";
  import InvoicesList from "$lib/InvoicesList.svelte";
  import { vendorEmailTemplates } from "$lib/vendor-email-templates";
  import type { PageData } from "./$types";

  let { data }: { data: PageData } = $props();
  let saving = $state(false);
  let notice = $state("");
  let saveError = $state("");
  let createInvoiceModal: CreateInvoiceModal;
  let invoiceModal: ApproveVendorInvoiceModal;
  let sequenceEmailModal: VendorEmailSequenceModal;
  let editModal: AddVendorLeadModal;
  let mounted = $state(false);
  $effect(() => {
    mounted = true;
  });

  const documents = [
    { name: "vendor_contract", label: "Vendor contract" },
    { name: "coi", label: "COI (Certificate of Insurance)" },
    { name: "info_packet", label: "Info packet" },
  ] as const;
  const backHref = $derived(
    data.lead.funnel_stage === "new_application"
      ? resolve("/applications")
      : resolve("/vendors"),
  );
  const backLabel = $derived(
    data.lead.funnel_stage === "new_application" ? "Applications" : "Vendors",
  );
  const contactName = $derived(
    data.lead.vendor_contact_name ||
      [data.lead.first_name, data.lead.last_name].filter(Boolean).join(" ") ||
      "—",
  );
  const decisionLabel = $derived(
    data.lead.application_decision === "pending"
      ? "Under review"
      : data.lead.application_decision,
  );

  const save: SubmitFunction = () => {
    saving = true;
    notice = "";
    saveError = "";
    return async ({ result, update }) => {
      try {
        if (result.type === "success") {
          await update({ reset: false });
          notice =
            result.data?.section === "documents"
              ? "Document checklist saved."
              : "Application decision saved.";
        } else {
          saveError = "Unable to save changes. Please try again.";
        }
      } finally {
        saving = false;
      }
    };
  };
</script>

<svelte:head
  ><title>{data.lead.business_name} | Vendor profile</title></svelte:head
>

<a class="back" href={backHref}>← {backLabel}</a>
<div class="profile-heading">
  <div>
    <p class="eyebrow">VENDOR LEAD / APPLICANT PROFILE</p>
    <h1>{data.lead.business_name}</h1>
  </div>
  <span
    class="status"
    class:accepted={data.lead.application_decision === "accepted"}
    >{decisionLabel}</span
  >
</div>
{#if notice}<p class="notice" role="status">{notice}</p>{/if}
{#if saveError}<p class="error" role="alert">{saveError}</p>{/if}

<div class="profile-grid">
  <section class="card application-card">
    <TabPanel tabs={[
      { id: 'overview', label: 'Overview' },
      { id: 'invoices', label: 'Invoices' },
      { id: 'communication', label: 'Communication' },
      { id: 'documents', label: 'Documents & Contracts' },
      { id: 'bookings', label: 'Bookings & Payments' },
    ]} let:active>

      {#if active === 'overview'}
        <div class="tab-section">
          <div class="card-heading">
            <h2>
              SUBMITTED APPLICATION: {data.lead.business_name}
            </h2>
            <button
              class="edit"
              type="button"
              aria-label="Edit vendor profile"
              onclick={() => editModal.open()}>✎</button
            >
          </div>
          <dl>
      <div>
        <dt>Business name</dt>
        <dd>{data.lead.business_name}</dd>
      </div>
      <div>
        <dt>Reference links</dt>
        <dd>
          {data.lead.instagram_handle
            ? `Instagram: @${data.lead.instagram_handle}`
            : "No Instagram supplied"}
        </dd>
      </div>
      <div>
        <dt>Vendor contact name</dt>
        <dd>{contactName}</dd>
      </div>
      <div>
        <dt>Email</dt>
        <dd>{data.lead.email || "—"}</dd>
      </div>
      <div>
        <dt>Phone</dt>
        <dd>{data.lead.phone_number || "—"}</dd>
      </div>
      <div>
        <dt>Category / medium</dt>
        <dd>{data.lead.vendor_category || "—"}</dd>
      </div>
      <div>
        <dt>Call date & time</dt>
        <dd>
          {data.lead.call_at && mounted
            ? new Date(data.lead.call_at).toLocaleString()
            : "—"}
        </dd>
      </div>
      <div>
        <dt>About brand</dt>
        <dd>{data.lead.notes || "—"}</dd>
      </div>
      <div>
        <dt>Call outcome</dt>
        <dd>{data.lead.call_outcome || "—"}</dd>
      </div>
      <div>
        <dt>Business commitment</dt>
        <dd>{data.lead.business_commitment || "—"}</dd>
      </div>
      <div>
        <dt>Objectives for joining The Good Flea</dt>
        <dd>{data.lead.primary_goals || "—"}</dd>
      </div>
      <div>
        <dt>Long-term vision & closing checklist</dt>
        <dd>{data.lead.long_term_outlook || "—"}</dd>
      </div>
      <div>
        <dt>Markets & frequency</dt>
        <dd>{data.lead.markets_and_frequency || "—"}</dd>
      </div>
      <div>
        <dt>Requested dates</dt>
        <dd>
          {data.lead.agreed_weekend_dates
            ? data.lead.agreed_weekend_dates.replaceAll(" | ", ", ")
            : "—"}
        </dd>
      </div>
      <div>
        <dt>Additional rep notes</dt>
        <dd class="notes">
          {data.lead.offer_concerns || data.lead.application_challenges || "—"}
        </dd>
      </div>
    </dl>
        </div>
      {/if}

      {#if active === 'invoices'}
        <div class="tab-section">
          <InvoicesList lead={data.lead} />
        </div>
      {/if}

      {#if active === 'communication'}
        <div class="tab-section">
          <p class="empty-state">Communication history will appear here.</p>
        </div>
      {/if}

      {#if active === 'documents'}
        <div class="tab-section">
          {#key data.lead.id}
            <form method="POST" action="?/update" use:enhance={save}>
              <input type="hidden" name="section" value="documents" />
              <fieldset disabled={saving}>
                <div class="documents-checklist">
                  {#each documents as document}
                    <label class="check">
                      <input
                        type="checkbox"
                        name={document.name}
                        checked={data.lead[document.name]}
                      />
                      {document.label}
                    </label>
                  {/each}
                </div>
                <button class="secondary save-documents" type="submit">
                  {saving ? 'Saving…' : 'Save checklist'}
                </button>
              </fieldset>
            </form>
          {/key}
        </div>
      {/if}

      {#if active === 'bookings'}
        <div class="tab-section">
          <p class="empty-state">Booking and payment information will appear here.</p>
        </div>
      {/if}

    </TabPanel>
  </section>

  <aside class="review-column" aria-label="Application review">
    <section class="card rubric">
      <h2>EVALUATION RUBRIC</h2>
      <div class="score">
        <span>Vendor interest score</span><strong
          >{data.lead.offer_interest
            ? `${data.lead.offer_interest}.0 / 5.0`
            : "Not scored"}</strong
        >
      </div>
      <p>
        {data.lead.offer_concerns ||
          data.lead.application_challenges ||
          "No reviewer notes entered."}
      </p>
    </section>

    <section class="card sequence-card" aria-labelledby="sequence-title">
      <h2 id="sequence-title">EMAIL SEQUENCE ACTIONS</h2>
      <div class="sequence-list">
        {#each vendorEmailTemplates as template}
          <button
            class="sequence-template"
            type="button"
            disabled={!data.lead.email}
            onclick={() => sequenceEmailModal.open(template)}
          >
            <span class="sequence-dot" aria-hidden="true">✉</span>
            <span>{template.title}</span>
            <span class="sequence-arrow" aria-hidden="true">→</span>
          </button>
        {/each}
      </div>
      {#if !data.lead.email}<p class="muted email-required">Add a vendor email before drafting a sequence message.</p>{/if}
    </section>

    <section class="card decision-card">
      <h2>DECISION ACTIONS</h2>
      <button
        class="primary"
        type="button"
        disabled={!!data.invoice || !data.lead.email}
        onclick={() => createInvoiceModal.open()}
      >
        {data.invoice ? "Approved · invoice sent" : "Accept application"}
      </button>
      {#if !data.lead.email}<p class="muted email-required">
          Add a vendor email before approval.
        </p>{/if}
      <form method="POST" action="?/update" use:enhance={save}>
        <input type="hidden" name="section" value="decision" />
        <fieldset disabled={saving || !!data.invoice}>
          <div class="decision-options">
            <button
              class="secondary"
              name="application_decision"
              value="waitlisted"
              aria-pressed={data.lead.application_decision === "waitlisted"}
              >Waitlist</button
            >
            <button
              class="secondary"
              name="application_decision"
              value="declined"
              aria-pressed={data.lead.application_decision === "declined"}
              >Decline</button
            >
          </div>
        </fieldset>
      </form>
      {#if data.invoice}
        <div class="sent-invoice">
          <strong>Invoice {data.invoice.number}</strong><span
            >{data.invoice.currency}
            {data.invoice.amount} · Due {data.invoice.due_date}</span
          ><span>Sent to {data.invoice.recipient_email}</span>
        </div>
      {/if}
    </section>

  </aside>
</div>

<AddVendorLeadModal
  bind:this={editModal}
  edit
  initial={data.lead}
  categories={data.categories}
  sources={data.sources}
  action="?/update"
  onsaved={() => {
    notice = "Vendor profile saved.";
    saveError = "";
  }}
/>
<CreateInvoiceModal
  bind:this={createInvoiceModal}
  lead={data.lead}
  onsent={() => {
    notice = "Invoice sent and vendor approved.";
    saveError = "";
  }}
/>
<ApproveVendorInvoiceModal
  bind:this={invoiceModal}
  lead={data.lead}
  onsent={() => {
    notice = "Invoice sent and vendor approved.";
    saveError = "";
  }}
/>
<VendorEmailSequenceModal
  bind:this={sequenceEmailModal}
  businessName={data.lead.business_name}
  recipient={data.lead.email}
  onsent={() => {
    notice = "Sequence email sent to the vendor.";
    saveError = "";
  }}
/>

<style>
  .back {
    color: #004aad;
    text-decoration: none;
    font-size: 11px;
  }
  .profile-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin: 18px 0 22px;
  }
  .eyebrow {
    margin: 0 0 5px;
    color: #9698a3;
    font-size: 9px;
    letter-spacing: 0.08em;
  }
  h1 {
    margin: 0;
    color: #25252b;
    font-size: 22px;
  }
  .status {
    border-radius: 5px;
    padding: 6px 10px;
    background: #e2f2fb;
    color: #09689d;
    font-size: 10px;
    text-transform: capitalize;
  }
  .status.accepted {
    background: #dcfce7;
    color: #166534;
  }
  .profile-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.36fr) minmax(290px, 1fr);
    gap: 20px;
    align-items: start;
  }
  .card {
    border: 1px solid #dedfe5;
    border-radius: 8px;
    padding: 16px;
    background: white;
    color: #565966;
  }
  .application-card {
    min-height: 720px;
  }
  .card-heading {
    display: flex;
    justify-content: space-between;
    align-items: start;
    gap: 16px;
  }
  h2 {
    margin: 0 0 16px;
    color: #232329;
    font-size: 13px;
  }
  .edit {
    width: auto;
    border: 0;
    padding: 0 2px;
    background: transparent;
    color: #0059bd;
    font-size: 23px;
  }
  dl {
    margin: 0;
  }
  dl > div {
    margin-bottom: 13px;
  }
  dt {
    margin-bottom: 4px;
    color: #999ba5;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
  }
  dd {
    margin: 0;
    font-size: 11px;
    line-height: 1.5;
    white-space: pre-wrap;
  }
  dd.notes {
    border: 1px solid #dedfe5;
    border-radius: 6px;
    padding: 10px;
    background: #fbfbfc;
  }
  .review-column {
    display: grid;
    gap: 18px;
    position: sticky;
    top: 20px;
  }
  .score {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    font-size: 11px;
  }
  .score strong {
    border-radius: 4px;
    padding: 4px 7px;
    background: #dcfce7;
    color: #168348;
    font-size: 10px;
  }
  .rubric p {
    margin: 12px 0 0;
    border: 1px solid #dedfe5;
    border-radius: 6px;
    padding: 10px;
    background: #fafafb;
    color: #92949e;
    font-size: 10px;
    line-height: 1.5;
  }
  fieldset {
    border: 0;
    padding: 0;
    margin: 0;
  }
  button {
    width: 100%;
    border-radius: 6px;
    padding: 10px 12px;
    font: inherit;
    font-size: 11px;
    cursor: pointer;
  }
  .primary {
    border: 1px solid #004aad;
    background: #004aad;
    color: white;
    font-weight: 600;
  }
  .secondary {
    border: 1px solid #dedfe5;
    background: white;
    color: #303039;
  }
  .decision-options {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 8px;
  }
  .sequence-list {
    display: grid;
    gap: 6px;
  }
  .sequence-template {
    display: grid;
    grid-template-columns: 18px minmax(0, 1fr) 14px;
    align-items: center;
    gap: 8px;
    border: 1px solid transparent;
    padding: 7px 5px;
    background: white;
    color: #565966;
    text-align: left;
    line-height: 1.35;
  }
  .sequence-template:not(:disabled):hover {
    border-color: #d9e5f5;
    background: #f6f9fd;
  }
  .sequence-template:disabled {
    color: #9698a3;
  }
  .sequence-dot {
    color: #0059bd;
    font-size: 14px;
  }
  .sequence-arrow {
    color: #818390;
    text-align: right;
  }
  .check {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 11px 0;
    font-size: 11px;
  }
  input[type="checkbox"] {
    width: 15px;
    height: 15px;
    margin: 0;
    accent-color: #004aad;
  }
  .save-documents {
    margin-top: 12px;
  }
  .muted {
    color: #818390;
    font-size: 10px;
  }
  .email-required {
    margin: 8px 0 0;
  }
  .sent-invoice {
    display: grid;
    gap: 5px;
    margin-top: 14px;
    border-radius: 6px;
    padding: 11px;
    background: #eaf5ee;
    color: #235a38;
    font-size: 10px;
  }
  button[aria-pressed="true"] {
    box-shadow: 0 0 0 2px #83ade7;
  }
  button:disabled {
    opacity: 0.6;
    cursor: wait;
  }
  button:focus-visible,
  input:focus-visible,
  a:focus-visible {
    outline: 2px solid #004aad;
    outline-offset: 3px;
  }
  .notice,
  .error {
    border-radius: 6px;
    padding: 11px;
    font-size: 11px;
  }
  .notice {
    background: #e7f7ec;
    color: #21663a;
  }
  .error {
    background: #fff0ed;
    color: #922218;
  }
  .tab-section {
    animation: fadeIn 0.15s ease-in;
  }
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  .empty-state {
    text-align: center;
    color: #818390;
    padding: 40px 20px;
    font-size: 13px;
  }
  .documents-checklist {
    display: grid;
    gap: 8px;
  }
  @media (max-width: 1000px) {
    .profile-grid {
      grid-template-columns: 1fr;
    }
    .review-column {
      position: static;
    }
  }
</style>
