<script lang="ts">
	import { resolve } from '$app/paths';
  import VendorQuestionnaireAnswers from "$lib/VendorQuestionnaireAnswers.svelte";
  import AddVendorLeadModal from "$lib/AddVendorLeadModal.svelte";
  import type { PageData } from "./$types";

  let { data }: { data: PageData } = $props();
  let modal: AddVendorLeadModal;
  let saved = $state(false);
  let mounted = $state(false);
  $effect(() => {
    mounted = true;
  });
</script>

<svelte:head><title>Vendors | Vendor Ops</title></svelte:head>

<div class="page-heading">
  <button
    class="add-button"
    disabled={!mounted || !!data.loadError}
    onclick={() => {
      saved = false;
      modal.open();
    }}>+ Add vendor lead</button
  >
</div>
{#if saved}<p class="success" role="status">Vendor lead saved.</p>{/if}
{#if data.loadError}
  <p class="error" role="alert">{data.loadError}</p>
{:else}
  <section class="lead-list" aria-label="Vendor leads">
    {#if data.leads.length === 0}
      <div class="empty">
        <h3>Start with a conversation</h3>
        <p>
          Add your first vendor lead to track their interest and next follow-up.
        </p>
      </div>
    {:else}
      <div class="table-scroll">
        <table>
          <thead
            ><tr
              ><th>Business / contact</th><th>Contact details</th><th
                >Category</th
              ><th>Source</th><th>Interest</th><th>Next follow-up</th><th
                >Conversation notes</th
              ></tr
            ></thead
          >
          <tbody>
            {#each data.leads as lead (lead.id)}
              <tr>
                <td
                  ><a class="profile-link" href={resolve('/vendors/[vendorId=integer]', { vendorId: String(lead.id) })}>{lead.business_name}</a><small
                    >{lead.vendor_contact_name ||
                      [lead.first_name, lead.last_name]
                        .filter(Boolean)
                        .join(" ")}</small
                  ></td
                >
                <td
                  >{#if lead.instagram_handle}<span
                      >@{lead.instagram_handle}</span
                    >{/if}{#if lead.email}<span>{lead.email}</span
                    >{/if}{#if lead.phone_number}<span>{lead.phone_number}</span
                    >{/if}</td
                >
                <td>{lead.vendor_category}</td><td>{lead.lead_source}</td>
                <td
                  ><span
                    class="badge"
                    class:hot={lead.interest_level === "hot"}
                    class:warm={lead.interest_level === "warm"}
                    >{lead.interest_level}</span
                  ></td
                >
                <td
                  >{lead.next_followup
                    ? mounted
                      ? new Date(lead.next_followup).toLocaleString()
                      : "Loading time…"
                    : "Not scheduled"}</td
                >
                <td class="notes"
                  >{lead.notes || "—"}<VendorQuestionnaireAnswers
                    {lead}
                    localTime={mounted}
                  /></td
                >
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </section>
{/if}
<AddVendorLeadModal
  bind:this={modal}
  categories={data.categories}
  sources={data.sources}
  onsaved={() => (saved = true)}
/>

<style>
	.profile-link { color: #004aad; font-weight: 600; text-decoration: underline; text-underline-offset: 3px; }
  .page-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 28px;
  }
  .add-button {
    background: #004aad;
    color: white;
    border: 0;
    border-radius: 8px;
    padding: 13px 18px;
    font: inherit;
    font-size: 14px;
    cursor: pointer;
  }
  .add-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .add-button:focus-visible {
    outline: 2px solid #004aad;
    outline-offset: 3px;
  }
  .lead-list {
    background: white;
    border: 1px solid #dfe7e1;
    border-radius: 12px;
    overflow: hidden;
  }
  .empty {
    padding: 40px 24px 56px;
    text-align: center;
    color: #607269;
  }
  .empty h3 {
    color: #20352f;
  }
  .table-scroll {
    overflow-x: auto;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 10px;
  }
  th,
  td {
    padding: 16px;
    border-top: 1px solid #e6ece7;
    vertical-align: top;
    min-width: 120px;
  }
  th {
    background: #f7f9f7;
    font-size: 12px;
    color: #607269;
  }
  td span,
  small {
    display: block;
    margin-top: 4px;
  }
  td {
    overflow-wrap: anywhere;
    max-width: 260px;
  }
  small {
    color: #607269;
  }
  .badge {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 20px;
    background: #e7effa;
    color: #27568d;
    text-transform: capitalize;
  }
  .badge.hot {
    background: #ffebe5;
    color: #9d3320;
  }
  .badge.warm {
    background: #fff2d7;
    color: #855800;
  }
  .notes {
    white-space: pre-wrap;
    min-width: 180px;
  }
  .success,
  .error {
    padding: 14px 18px;
    border-radius: 8px;
  }
  .success {
    background: #e5f4e5;
    color: #235328;
  }
  .error {
    background: #fff0ed;
    color: #922218;
  }
</style>
