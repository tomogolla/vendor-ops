<script lang="ts">
  import { resolve } from '$app/paths';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  let activeIndex = $state(0);
  const active = $derived(data.weekends[activeIndex]);
  const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
</script>

<svelte:head><title>Market weekends | Vendor Ops</title></svelte:head>

<section class="weekend-shell" aria-labelledby="weekend-heading">
  <div class="heading">
    <div>
      <p class="eyebrow">FALL MARKET SERIES</p>
      <h1 id="weekend-heading">Market weekends</h1>
      <p>Review bookings, booth availability, and payments for each weekend.</p>
    </div>
    <span class="capacity-note">40 booth spaces per weekend</span>
  </div>

  <div class="weekend-tabs" role="tablist" aria-label="Market weekends">
    {#each data.weekends as weekend, index}
      <button
        type="button"
        role="tab"
        aria-selected={index === activeIndex}
        aria-controls="weekend-panel"
        class:active={index === activeIndex}
        onclick={() => (activeIndex = index)}
      >
        <span>{weekend.name}</span>
        <small>{weekend.available} available</small>
      </button>
    {/each}
  </div>

  {#if active}
    <div class="weekend-layout" id="weekend-panel" role="tabpanel">
      <aside class="stats" aria-label={`${active.name} statistics`}>
        <div class="date-card">
          <span class="season">Market weekend</span>
          <h2>{active.name}</h2>
          <p>{active.available > 0 ? 'Booking available' : 'Fully booked'}</p>
        </div>
        <div class="stat-card">
          <span>Vendors booked</span>
          <strong>{active.booked}<small> / {active.capacity}</small></strong>
        </div>
        <div class="stat-card">
          <span>Booth spaces available</span>
          <strong>{active.available}</strong>
        </div>
        <div class="stat-card">
          <span>Total amount paid</span>
          <strong>{money.format(Number(active.total_paid))}</strong>
        </div>
      </aside>

      <div class="vendor-card">
        <div class="table-heading">
          <div><h2>{active.name}</h2><p>{active.booked} confirmed vendor{active.booked === 1 ? '' : 's'}</p></div>
          <span>{active.available} of {active.capacity} spaces open</span>
        </div>
        {#if active.vendors.length}
          <div class="table-scroll">
            <table>
              <thead>
                <tr><th>Booth</th><th>Brand name</th><th>Contact</th><th>Category</th><th>Email</th><th>Payment</th><th>Amount paid</th></tr>
              </thead>
              <tbody>
                {#each active.vendors as vendor, index}
                  <tr>
                    <td>{index + 1}</td>
                    <td><a href={resolve('/vendors/[vendorId=integer]', { vendorId: String(vendor.vendor_id) })}>{vendor.business_name}</a></td>
                    <td><strong>{vendor.contact_name || '—'}</strong><span>{vendor.phone_number || 'No phone'}</span></td>
                    <td>{vendor.category || '—'}</td>
                    <td><a class="email" href={`mailto:${vendor.email}`}>{vendor.email}</a></td>
                    <td><span class:paid={vendor.payment_status === 'Paid'} class="payment-status">{vendor.payment_status}</span></td>
                    <td class="amount">{money.format(Number(vendor.amount_paid))}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {:else}
          <div class="empty">
            <strong>No vendors booked yet</strong>
            <p>Approved vendors who select this weekend will appear here.</p>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</section>

<style>
  .weekend-shell { color: #25252b; }
  .heading { display: flex; justify-content: space-between; align-items: end; gap: 24px; margin-bottom: 24px; }
  .eyebrow { margin: 0 0 6px; color: #8b8e99; font-size: 10px; letter-spacing: .08em; }
  h1 { margin: 0; font-size: 25px; }
  .heading p:not(.eyebrow) { margin: 7px 0 0; color: #747783; font-size: 13px; }
  .capacity-note { padding: 8px 11px; border-radius: 5px; background: #eef3fb; color: #54709c; font-size: 11px; }
  .weekend-tabs { display: flex; overflow-x: auto; border: 1px solid #dedfe5; border-radius: 7px; padding: 0 12px; background: white; scrollbar-width: thin; }
  .weekend-tabs button { flex: 0 0 auto; min-width: 145px; border: 0; border-bottom: 2px solid transparent; padding: 13px 12px 11px; background: transparent; color: #92949e; text-align: left; font: inherit; font-size: 11px; cursor: pointer; }
  .weekend-tabs button span, .weekend-tabs button small { display: block; }
  .weekend-tabs button small { margin-top: 4px; color: #a0a3ac; font-size: 10px; }
  .weekend-tabs button.active { border-bottom-color: #fcb533; color: #25252b; font-weight: 600; }
  .weekend-tabs button:focus-visible, a:focus-visible { outline: 2px solid #004aad; outline-offset: 2px; }
  .weekend-layout { display: grid; grid-template-columns: 184px minmax(0, 1fr); gap: 20px; margin-top: 14px; align-items: start; }
  .stats { display: grid; gap: 12px; padding: 10px; border: 1px solid #dedfe5; border-radius: 7px; background: white; }
  .date-card, .stat-card { padding: 14px 12px; border: 1px solid #dedfe5; border-radius: 6px; background: #fbfcfe; }
  .date-card { background: white; }
  .season { display: inline-block; border-radius: 4px; padding: 4px 7px; background: #eef3fb; color: #54709c; font-size: 9px; }
  .date-card h2 { margin: 12px 0 5px; font-size: 14px; }
  .date-card p { margin: 0; color: #168447; font-size: 10px; }
  .stat-card span { display: block; margin-bottom: 7px; color: #9598a3; font-size: 10px; }
  .stat-card strong { font-size: 20px; }
  .stat-card strong small { color: #555967; font-size: 14px; }
  .vendor-card { min-width: 0; overflow: hidden; border: 1px solid #dedfe5; border-radius: 7px; background: white; }
  .table-heading { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px; }
  .table-heading h2 { margin: 0; font-size: 14px; }
  .table-heading p { margin: 4px 0 0; color: #92949f; font-size: 10px; }
  .table-heading > span { color: #667085; font-size: 10px; }
  .table-scroll { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; font-size: 11px; text-align: left; }
  th { padding: 12px 11px; border-top: 1px solid #dedfe5; border-bottom: 1px solid #dedfe5; background: #f5f5f6; color: #28282e; font-size: 10px; text-transform: uppercase; white-space: nowrap; }
  td { padding: 12px 11px; border-bottom: 1px solid #e5e6ea; color: #575a65; vertical-align: top; }
  td a { color: #25252b; font-weight: 600; text-decoration: none; }
  td a:hover { color: #004aad; text-decoration: underline; }
  td strong, td span { display: block; }
  td strong { color: #33343a; font-weight: 500; }
  td span { margin-top: 3px; color: #8a8d98; }
  td .email { color: #555a68; font-weight: 400; overflow-wrap: anywhere; }
  .payment-status { display: inline-block; margin: 0; border-radius: 20px; padding: 4px 7px; background: #f3f4f6; color: #737783; }
  .payment-status.paid { background: #e9f8ee; color: #178044; }
  .amount { color: #25252b; font-weight: 600; white-space: nowrap; }
  .empty { padding: 64px 24px; border-top: 1px solid #dedfe5; text-align: center; color: #8a8d98; }
  .empty strong { color: #34353b; font-size: 14px; }
  .empty p { margin: 7px 0 0; font-size: 11px; }
  @media (max-width: 900px) { .weekend-layout { grid-template-columns: 1fr; } .stats { grid-template-columns: repeat(2, 1fr); } }
  @media (max-width: 560px) { .heading { align-items: start; flex-direction: column; } .stats { grid-template-columns: 1fr; } .weekend-layout { gap: 14px; } }
</style>
