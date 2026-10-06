<script lang="ts">
  import { enhance } from "$app/forms";
  import { resolve } from "$app/paths";
  import type { SubmitFunction } from "@sveltejs/kit";
  import type { PageData, ActionData } from "./$types";

  let { data, form }: { data: PageData; form: ActionData | null } = $props();
  let uploading = $state(false);
  let picker: HTMLInputElement;
  const upload: SubmitFunction = () => {
    uploading = true;
    return async ({ update }) => {
      await update();
      uploading = false;
      if (picker) picker.value = "";
    };
  };
  const contact = (lead: PageData["applications"][number]) =>
    lead.vendor_contact_name ||
    [lead.first_name, lead.last_name].filter(Boolean).join(" ") ||
    "—";
</script>

<svelte:head><title>Application pipeline | Vendor Ops</title></svelte:head>

<section class="pipeline" aria-labelledby="pipeline-title">
  <div class="heading">
    <div><h3 id="pipeline-title">Application pipeline</h3></div>
  </div>

  <div class="import-card">
    <form
      method="POST"
      action="?/importCsv"
      enctype="multipart/form-data"
      use:enhance={upload}
    >
      <label class="import-button" class:disabled={uploading}>
        <input
          bind:this={picker}
          name="file"
          type="file"
          accept=".csv,text/csv"
          required
          disabled={uploading}
          onchange={(event) => event.currentTarget.form?.requestSubmit()}
        />
        {uploading ? "Importing…" : "Import vendors CSV"}
      </label>
      <span
        >Required columns: Business name and Instagram. Maximum 5,000 rows or 2
        MB.</span
      >
    </form>
    {#if form?.importErrors?.length}<div class="alert error" role="alert">
        {form.importErrors.join(" ")}
      </div>{/if}
    {#if form?.importResult}
      <div class="alert success" role="status">
        Imported {form.importResult.created.length}; skipped {form.importResult
          .skipped.length} duplicate{form.importResult.skipped.length === 1
          ? ""
          : "s"}; {form.importResult.errors.length} row error{form.importResult
          .errors.length === 1
          ? ""
          : "s"}.
      </div>
      {#if form.importResult.errors.length}
        <details>
          <summary>View row errors</summary>
          <ul>
            {#each form.importResult.errors as issue}<li>
                Row {issue.row}: {issue.message}
              </li>{/each}
          </ul>
        </details>
      {/if}
    {/if}
  </div>

  {#if data.loadError}
    <p class="alert error" role="alert">{data.loadError}</p>
  {:else}
    <div class="applications-card">
      <div class="table-title">
        <h2>New applications</h2>
        <span>{data.applications.length}</span>
      </div>
      {#if data.applications.length}
        <div class="table-scroll">
          <table>
            <thead
              ><tr
                ><th>Business name</th><th>Email</th><th>Phone</th><th
                  >Decision state</th
                ><th>Source</th><th>Date entered</th><th>Instagram</th><th
                  >Dates booked</th
                ></tr
              ></thead
            >
            <tbody>
              {#each data.applications as application (application.id)}
                <tr>
                  <td
                    ><a
                      class="business"
                      href={resolve("/vendors/[vendorId=integer]", {
                        vendorId: String(application.id),
                      })}>{application.business_name}</a
                    ><small>{contact(application)}</small></td
                  >
                  <td>{application.email || "—"}</td>
                  <td>{application.phone_number || "—"}</td>
                  <td
                    ><span class="review-state"
                      >{application.application_decision === "pending"
                        ? "Under review"
                        : application.application_decision}</span
                    ></td
                  >
                  <td>{application.lead_source}</td>
                  <td
                    >{new Intl.DateTimeFormat("en-GB", {
                      timeZone: "Africa/Nairobi",
                    }).format(new Date(application.created_at))}</td
                  >
                  <td
                    >{application.instagram_handle
                      ? `@${application.instagram_handle}`
                      : "—"}</td
                  >
                  <td
                    >{application.agreed_weekend_dates
                      ? application.agreed_weekend_dates.replaceAll(" | ", ", ")
                      : "—"}</td
                  >
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {:else}
        <div class="empty">
          <strong>No new applications</strong>
          <p>Import a CSV to add applications to the review queue.</p>
        </div>
      {/if}
    </div>
  {/if}
</section>

<style>
  .pipeline {
    color: #25252b;
  }
  .heading {
    margin-bottom: 22px;
  }
  .heading h3 {
    margin: 0;
    font-size: 16px;
  }
  .import-card {
    margin-bottom: 24px;
    padding: 11px;
    border: 1px solid #dedfe5;
    border-radius: 7px;
    background: white;
  }
  .import-card form {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
  }
  .import-card form > span {
    color: #8b8e98;
    font-size: 10px;
  }
  .import-button {
    display: inline-block;
    border-radius: 6px;
    padding: 11px 15px;
    background: #004aad;
    color: white;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
  }
  .import-button input {
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0;
  }
  .import-button.disabled {
    opacity: 0.6;
    cursor: wait;
  }
  .applications-card {
    padding: 7px;
    border: 1px solid #dedfe5;
    border-radius: 7px;
    background: #f4f4f5;
  }
  .table-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 2px 12px;
  }
  .table-title h2 {
    margin: 0;
    font-size: 12px;
  }
  .table-title span {
    padding-right: 5px;
    font-size: 10px;
  }
  .table-scroll {
    overflow-x: auto;
    border: 1px solid #dedfe5;
    border-radius: 7px;
    background: white;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 10px;
  }
  th {
    padding: 13px 11px;
    background: #f4f4f5;
    color: #25252b;
    font-size: 10px;
    text-transform: uppercase;
    white-space: nowrap;
  }
  td {
    padding: 12px 11px;
    border-top: 1px solid #dedfe5;
    color: #626570;
    vertical-align: top;
    max-width: 160px;
    overflow-wrap: anywhere;
  }
  .business {
    color: #25252b;
    font-size: 11px;
    font-weight: 600;
    text-decoration: none;
  }
  .business:hover {
    color: #004aad;
    text-decoration: underline;
  }
  td small {
    display: block;
    margin-top: 4px;
    color: #9a9ca5;
  }
  .review-state {
    display: inline-block;
    border-radius: 4px;
    padding: 4px 8px;
    background: #e2f2fb;
    color: #09689d;
    font-weight: 600;
    text-transform: capitalize;
    white-space: nowrap;
  }
  .alert {
    margin-top: 10px;
    border-radius: 5px;
    padding: 10px 12px;
    font-size: 11px;
  }
  .alert.success {
    background: #e8f7ed;
    color: #21683b;
  }
  .alert.error {
    background: #fff0ed;
    color: #922218;
  }
  details {
    margin-top: 10px;
    font-size: 11px;
    color: #7a3a25;
  }
  .empty {
    padding: 56px 20px;
    border: 1px solid #dedfe5;
    border-radius: 7px;
    background: white;
    text-align: center;
    color: #8a8d98;
  }
  .empty strong {
    color: #34353b;
    font-size: 13px;
  }
  .empty p {
    margin: 7px 0 0;
    font-size: 11px;
  }
  a:focus-visible,
  .import-button:focus-within {
    outline: 2px solid #004aad;
    outline-offset: 3px;
  }
</style>
