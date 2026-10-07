<script lang="ts">
  import { enhance } from '$app/forms';
  import type { SubmitFunction } from '@sveltejs/kit';
  import { tick } from 'svelte';
  import type { VendorLead } from '$lib/vendor-leads';

  interface BoothSize {
    id: number;
    width: number;
    length: number;
    base_price: string;
    description: string;
    is_active: boolean;
  }

  interface AddOn {
    id: number;
    name: string;
    price_per_weekend: string;
    description: string;
    is_active: boolean;
  }

  interface Discount {
    id: number;
    discount_type: 'percentage' | 'fixed';
    value: string;
    description: string;
    is_active: boolean;
  }

  interface LineItem {
    item_type: 'booth_size' | 'add_on' | 'discount';
    description: string;
    quantity: number;
    unit_price: string;
    booth_size?: number;
    add_on?: number;
  }

  let { lead, onsent }: { lead: VendorLead; onsent: () => void } = $props();
  let dialog = $state<HTMLDialogElement>();
  let step = $state(1);
  let loading = $state(false);
  let submitting = $state(false);
  let errors = $state<Record<string, string[]>>({});

  let boothSizes = $state<BoothSize[]>([]);
  let addOns = $state<AddOn[]>([]);
  let discounts = $state<Discount[]>([]);
  let availableWeekends = $state<string[]>([]);

  let selectedBoothSizes = $state<{ id: number; count: number }[]>([]);
  let selectedWeekends = $state<string[]>([]);
  let selectedAddOns = $state<{ id: number; count: number }[]>([]);
  let selectedDiscount = $state<number | null>(null);
  let dueDate = $state('');
  let invoiceLink = $state('');

  let lineItems = $derived.by(() => {
    const items: LineItem[] = [];

    selectedBoothSizes.forEach(({ id, count }) => {
      const booth = boothSizes.find(b => b.id === id);
      if (booth) {
        for (let i = 0; i < count; i++) {
          items.push({
            item_type: 'booth_size',
            description: `${booth.width}ft x ${booth.length}ft booth`,
            quantity: 1,
            unit_price: booth.base_price,
            booth_size: id,
          });
        }
      }
    });

    selectedAddOns.forEach(({ id, count }) => {
      const addon = addOns.find(a => a.id === id);
      if (addon) {
        items.push({
          item_type: 'add_on',
          description: addon.name,
          quantity: count * selectedWeekends.length,
          unit_price: addon.price_per_weekend,
          add_on: id,
        });
      }
    });

    return items;
  });

  let subtotal = $derived.by(() => {
    return lineItems.reduce((sum, item) => {
      return sum + (parseFloat(item.unit_price) * item.quantity);
    }, 0);
  });

  let discountAmount = $derived.by(() => {
    if (!selectedDiscount) return 0;
    const discount = discounts.find(d => d.id === selectedDiscount);
    if (!discount) return 0;
    const value = parseFloat(discount.value);
    return discount.discount_type === 'percentage' ? subtotal * (value / 100) : value;
  });

  let total = $derived(Math.max(0, subtotal - discountAmount));

  export function open() {
    errors = {};
    step = 1;
    selectedBoothSizes = [];
    selectedWeekends = lead.agreed_weekend_dates?.split(' | ').filter(Boolean) || [];
    selectedAddOns = [];
    selectedDiscount = null;
    dueDate = '';
    invoiceLink = '';
    loadProducts();
    dialog?.showModal();
  }

  async function loadProducts() {
    loading = true;
    try {
      const [boothRes, addOnsRes, discountsRes] = await Promise.all([
        fetch('/api/booth-sizes/'),
        fetch('/api/add-ons/'),
        fetch('/api/discounts/'),
      ]);

      if (boothRes.ok) boothSizes = await boothRes.json();
      if (addOnsRes.ok) addOns = await addOnsRes.json();
      if (discountsRes.ok) discounts = await discountsRes.json();

      if (!availableWeekends.length && lead.agreed_weekend_dates) {
        availableWeekends = lead.agreed_weekend_dates.split(' | ').filter(Boolean);
      }
    } finally {
      loading = false;
    }
  }

  function incrementBoothSize(id: number) {
    const existing = selectedBoothSizes.find(b => b.id === id);
    if (existing) {
      existing.count++;
    } else {
      selectedBoothSizes = [...selectedBoothSizes, { id, count: 1 }];
    }
  }

  function decrementBoothSize(id: number) {
    selectedBoothSizes = selectedBoothSizes
      .map(b => b.id === id ? { ...b, count: b.count - 1 } : b)
      .filter(b => b.count > 0);
  }

  function toggleWeekend(weekend: string) {
    if (selectedWeekends.includes(weekend)) {
      selectedWeekends = selectedWeekends.filter(w => w !== weekend);
    } else {
      selectedWeekends = [...selectedWeekends, weekend];
    }
  }

  function incrementAddOn(id: number) {
    const existing = selectedAddOns.find(a => a.id === id);
    if (existing) {
      existing.count++;
    } else {
      selectedAddOns = [...selectedAddOns, { id, count: 1 }];
    }
  }

  function decrementAddOn(id: number) {
    selectedAddOns = selectedAddOns
      .map(a => a.id === id ? { ...a, count: a.count - 1 } : a)
      .filter(a => a.count > 0);
  }

  function canAdvance(): boolean {
    if (step === 1) return selectedBoothSizes.length > 0;
    if (step === 2) return selectedWeekends.length > 0;
    if (step === 3) return true;
    if (step === 4) return true;
    return true;
  }

  async function createAndSendInvoice() {
    submitting = true;
    errors = {};

    try {
      const invoiceRes = await fetch(`/api/vendor-leads/${lead.id}/invoices/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          due_date: dueDate,
          invoice_link: invoiceLink,
          weekend_dates: selectedWeekends.join(' | '),
          line_items: [],
        }),
      });

      if (!invoiceRes.ok) {
        const data = await invoiceRes.json();
        errors = data || { non_field_errors: ['Failed to create invoice'] };
        return;
      }

      const invoice = await invoiceRes.json();

      for (const item of lineItems) {
        const itemRes = await fetch(`/api/vendor-leads/${lead.id}/invoices/${invoice.id}/line-items/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(item),
        });

        if (!itemRes.ok) {
          const data = await itemRes.json();
          errors = data || { non_field_errors: ['Failed to add line item'] };
          return;
        }
      }

      const sendRes = await fetch(`/api/vendor-leads/${lead.id}/invoices/${invoice.id}/send/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!sendRes.ok) {
        const data = await sendRes.json();
        errors = data || { non_field_errors: ['Failed to send invoice'] };
        return;
      }

      dialog?.close();
      onsent();
    } catch (e) {
      errors = { non_field_errors: ['An error occurred. Please try again.'] };
    } finally {
      submitting = false;
    }
  }
</script>

<dialog bind:this={dialog} aria-labelledby="create-invoice-title" oncancel={(event) => { if (submitting) event.preventDefault(); }}>
  <div class="heading">
    <div>
      <p class="eyebrow">INVOICE BUILDER · STEP {step} OF 5</p>
      <h2 id="create-invoice-title">Create and send invoice</h2>
    </div>
    <button type="button" class="close" aria-label="Close invoice modal" disabled={submitting} onclick={() => dialog?.close()}>×</button>
  </div>

  {#if Object.keys(errors).length}
    <div class="error-summary" role="alert" tabindex="-1">
      <strong>Unable to complete action.</strong>
      <ul>{#each Object.entries(errors) as [field, messages]}{#each messages as message}<li>{field === 'non_field_errors' ? '' : `${field.replaceAll('_', ' ')}: `}{message}</li>{/each}{/each}</ul>
    </div>
  {/if}

  <div class="steps-progress">
    {#each [1, 2, 3, 4, 5] as s}
      <div class="step-dot" class:active={step === s} class:completed={step > s}>
        <span>{s}</span>
      </div>
      {#if s < 5}<div class="step-line" class:active={step > s}></div>{/if}
    {/each}
  </div>

  <!-- Step 1: Booth Sizes -->
  {#if step === 1}
    <div class="step-content">
      <h3>Select booth size(s)</h3>
      <p class="step-intro">Choose which booth sizes {lead.business_name} will occupy.</p>

      {#if loading}
        <p class="loading">Loading booth sizes...</p>
      {:else if boothSizes.length === 0}
        <p class="empty">No booth sizes available.</p>
      {:else}
        <div class="booth-grid">
          {#each boothSizes as booth}
            <div class="booth-card">
              <div class="booth-header">
                <strong>{booth.width}ft × {booth.length}ft</strong>
                <span class="booth-price">${parseFloat(booth.base_price).toFixed(2)}</span>
              </div>
              {#if booth.description}<p class="booth-desc">{booth.description}</p>{/if}
              <div class="booth-selector">
                <button
                  type="button"
                  class="btn-counter"
                  disabled={!selectedBoothSizes.find(b => b.id === booth.id)}
                  onclick={() => decrementBoothSize(booth.id)}
                >−</button>
                <span class="booth-count">{selectedBoothSizes.find(b => b.id === booth.id)?.count || 0}</span>
                <button
                  type="button"
                  class="btn-counter"
                  onclick={() => incrementBoothSize(booth.id)}
                >+</button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}

  <!-- Step 2: Weekends -->
  {#if step === 2}
    <div class="step-content">
      <h3>Choose market dates</h3>
      <p class="step-intro">Select which weekends {lead.business_name} will attend.</p>

      {#if availableWeekends.length === 0}
        <p class="empty">No market dates available. Add agreed weekend dates to the vendor profile.</p>
      {:else}
        <div class="weekend-grid">
          {#each availableWeekends as weekend}
            <label class="weekend-option">
              <input
                type="checkbox"
                checked={selectedWeekends.includes(weekend)}
                onchange={() => toggleWeekend(weekend)}
              />
              <span>{weekend}</span>
            </label>
          {/each}
        </div>
      {/if}
    </div>
  {/if}

  <!-- Step 3: Add-ons -->
  {#if step === 3}
    <div class="step-content">
      <h3>Select add-on services</h3>
      <p class="step-intro">Optional: Add rental items or services (per weekend).</p>

      {#if addOns.length === 0}
        <p class="empty">No add-ons available.</p>
      {:else}
        <div class="addon-grid">
          {#each addOns as addon}
            <div class="addon-card">
              <div class="addon-header">
                <strong>{addon.name}</strong>
                <span class="addon-price">${parseFloat(addon.price_per_weekend).toFixed(2)}/wknd</span>
              </div>
              {#if addon.description}<p class="addon-desc">{addon.description}</p>{/if}
              <div class="addon-selector">
                <button
                  type="button"
                  class="btn-counter"
                  disabled={!selectedAddOns.find(a => a.id === addon.id)}
                  onclick={() => decrementAddOn(addon.id)}
                >−</button>
                <span class="addon-count">{selectedAddOns.find(a => a.id === addon.id)?.count || 0}</span>
                <button
                  type="button"
                  class="btn-counter"
                  onclick={() => incrementAddOn(addon.id)}
                >+</button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}

  <!-- Step 4: Discounts -->
  {#if step === 4}
    <div class="step-content">
      <h3>Apply discount (optional)</h3>
      <p class="step-intro">Choose a discount code or apply none.</p>

      {#if discounts.length === 0}
        <p class="empty">No discounts available.</p>
      {:else}
        <div class="discount-grid">
          <label class="discount-option">
            <input type="radio" name="discount" value="" checked={selectedDiscount === null} onchange={() => { selectedDiscount = null; }} />
            <span>No discount</span>
          </label>
          {#each discounts as discount}
            <label class="discount-option">
              <input
                type="radio"
                name="discount"
                value={discount.id}
                checked={selectedDiscount === discount.id}
                onchange={() => { selectedDiscount = discount.id; }}
              />
              <div class="discount-info">
                <strong>{discount.description}</strong>
                <span class="discount-value">
                  {discount.discount_type === 'percentage' ? `${discount.value}%` : `$${discount.value}`}
                </span>
              </div>
            </label>
          {/each}
        </div>
      {/if}
    </div>
  {/if}

  <!-- Step 5: Review & Send -->
  {#if step === 5}
    <div class="step-content">
      <h3>Review and send invoice</h3>
      <p class="step-intro">Confirm the details before sending to {lead.business_name}.</p>

      <div class="review-section">
        <h4>Line Items</h4>
        <table class="line-items-table">
          <thead>
            <tr>
              <th>Description</th>
              <th style="text-align: right;">Qty</th>
              <th style="text-align: right;">Price</th>
              <th style="text-align: right;">Total</th>
            </tr>
          </thead>
          <tbody>
            {#each lineItems as item}
              <tr>
                <td>{item.description}</td>
                <td style="text-align: right;">{item.quantity}</td>
                <td style="text-align: right;">${parseFloat(item.unit_price).toFixed(2)}</td>
                <td style="text-align: right;">${(parseFloat(item.unit_price) * item.quantity).toFixed(2)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <div class="review-totals">
        <div class="total-row">
          <span>Subtotal</span>
          <strong>${subtotal.toFixed(2)}</strong>
        </div>
        {#if selectedDiscount && discounts.find(d => d.id === selectedDiscount)}
          <div class="total-row">
            <span>Discount</span>
            <strong>-${discountAmount.toFixed(2)}</strong>
          </div>
        {/if}
        <div class="total-row grand-total">
          <span>Total</span>
          <strong>${total.toFixed(2)}</strong>
        </div>
      </div>

      <div class="invoice-fields">
        <label for="due-date">Due date *
          <input id="due-date" type="date" bind:value={dueDate} required />
        </label>
        <label class="full" for="invoice-link">Secure payment link *
          <input id="invoice-link" type="url" pattern="https://.*" placeholder="https://payments.example.com/..." bind:value={invoiceLink} required />
        </label>
      </div>
    </div>
  {/if}

  <div class="actions">
    <button type="button" disabled={submitting || step === 1} onclick={() => { step--; errors = {}; }}>← Previous</button>

    {#if step < 5}
      <button type="button" disabled={submitting || !canAdvance()} class="primary" onclick={() => { step++; errors = {}; }}>Next →</button>
    {:else}
      <button type="button" disabled={submitting || !dueDate || !invoiceLink} class="primary send" onclick={createAndSendInvoice}>
        {submitting ? 'Sending…' : 'Send invoice & approve'}
      </button>
    {/if}
  </div>
</dialog>

<style>
  dialog {
    box-sizing: border-box;
    width: min(720px, calc(100% - 32px));
    max-height: calc(100dvh - 32px);
    border: 0;
    border-radius: 12px;
    padding: 24px;
    color: #26262c;
    box-shadow: 0 24px 70px #15243755;
  }
  dialog::backdrop {
    background: #182637aa;
  }
  .heading {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    align-items: start;
    margin-bottom: 20px;
  }
  .eyebrow {
    margin: 0 0 8px;
    color: #818390;
    font-size: 11px;
    letter-spacing: .05em;
  }
  h2 {
    margin: 0;
    font-size: 21px;
  }
  h3 {
    margin: 0 0 8px;
    font-size: 16px;
    font-weight: 600;
  }
  h4 {
    margin: 0 0 12px;
    font-size: 13px;
    font-weight: 600;
    color: #565966;
  }
  .close {
    border: 0;
    font-size: 25px;
    padding: 0 5px;
    background: transparent;
    color: #26262c;
    cursor: pointer;
  }
  .close:disabled {
    opacity: .55;
    cursor: wait;
  }
  .error-summary {
    background: #fff0ed;
    color: #922218;
    border-radius: 6px;
    padding: 12px;
    font-size: 12px;
    margin-bottom: 16px;
  }
  .error-summary ul {
    margin-bottom: 0;
    padding-left: 20px;
  }
  .steps-progress {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin-bottom: 28px;
  }
  .step-dot {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    border: 2px solid #dedfe5;
    background: white;
    color: #818390;
    flex-shrink: 0;
  }
  .step-dot.active {
    border-color: #004aad;
    color: #004aad;
    background: #f0f5ff;
  }
  .step-dot.completed {
    border-color: #10b981;
    background: #dcfce7;
    color: #065f46;
  }
  .step-line {
    height: 2px;
    flex: 1;
    background: #dedfe5;
    margin: 0 4px;
  }
  .step-line.active {
    background: #10b981;
  }
  .step-content {
    min-height: 200px;
  }
  .step-intro {
    color: #666b77;
    font-size: 13px;
    margin: 0 0 18px;
  }
  .loading, .empty {
    color: #818390;
    font-size: 13px;
    text-align: center;
    padding: 20px;
  }
  .booth-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
  }
  .booth-card, .addon-card {
    border: 1px solid #dedfe5;
    border-radius: 8px;
    padding: 14px;
    background: white;
  }
  .booth-header, .addon-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    gap: 8px;
    margin-bottom: 8px;
  }
  .booth-header strong, .addon-header strong {
    font-size: 13px;
    font-weight: 600;
  }
  .booth-price, .addon-price {
    color: #004aad;
    font-weight: 600;
    font-size: 12px;
  }
  .booth-desc, .addon-desc {
    margin: 0 0 10px;
    font-size: 11px;
    color: #818390;
  }
  .booth-selector, .addon-selector {
    display: flex;
    align-items: center;
    gap: 10px;
    justify-content: center;
  }
  .btn-counter {
    width: 28px;
    height: 28px;
    border-radius: 4px;
    border: 1px solid #cbd1da;
    background: white;
    color: #26262c;
    font-weight: 600;
    cursor: pointer;
    font-size: 14px;
  }
  .btn-counter:disabled {
    opacity: .45;
    cursor: default;
  }
  .booth-count, .addon-count {
    min-width: 30px;
    text-align: center;
    font-weight: 600;
  }
  .weekend-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 8px;
  }
  .weekend-option, .discount-option {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    border: 1px solid #dedfe5;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    font-size: 13px;
  }
  .weekend-option:hover, .discount-option:hover {
    background: #f8f9fb;
  }
  input[type="checkbox"], input[type="radio"] {
    width: 16px;
    height: 16px;
    cursor: pointer;
    accent-color: #004aad;
  }
  .discount-grid {
    display: grid;
    gap: 8px;
  }
  .discount-info {
    display: flex;
    justify-content: space-between;
    gap: 8px;
    flex: 1;
  }
  .discount-info strong {
    font-size: 12px;
  }
  .discount-value {
    color: #004aad;
    font-weight: 600;
    font-size: 12px;
  }
  .review-section {
    margin-bottom: 20px;
  }
  .line-items-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }
  .line-items-table th {
    text-align: left;
    padding: 8px;
    border-bottom: 1px solid #dedfe5;
    font-weight: 600;
    color: #565966;
  }
  .line-items-table td {
    padding: 8px;
    border-bottom: 1px solid #dedfe5;
  }
  .review-totals {
    background: #f8f9fb;
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 20px;
  }
  .total-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    padding: 6px 0;
  }
  .total-row.grand-total {
    border-top: 1px solid #dedfe5;
    padding-top: 10px;
    margin-top: 8px;
    font-weight: 600;
    color: #26262c;
  }
  .invoice-fields {
    display: grid;
    gap: 12px;
    margin-bottom: 20px;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
  }
  label.full {
    grid-column: 1 / -1;
  }
  input[type="date"], input[type="url"] {
    box-sizing: border-box;
    padding: 10px 12px;
    border: 1px solid #cbd1da;
    border-radius: 6px;
    font: inherit;
    font-size: 13px;
  }
  input[type="date"]:focus, input[type="url"]:focus {
    outline: 2px solid #004aad;
    outline-offset: 2px;
  }
  .actions {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    border-top: 1px solid #e4e6eb;
    padding-top: 18px;
  }
  button {
    flex: 1;
    border: 1px solid #d0d4db;
    border-radius: 6px;
    padding: 10px 16px;
    background: white;
    color: #26262c;
    font: inherit;
    font-size: 12px;
    cursor: pointer;
  }
  button.primary {
    border-color: #004aad;
    background: #004aad;
    color: white;
    font-weight: 600;
  }
  button:disabled {
    opacity: .55;
    cursor: wait;
  }
  @media (max-width: 560px) {
    dialog {
      padding: 18px;
    }
    .booth-grid {
      grid-template-columns: 1fr;
    }
    .steps-progress {
      gap: 0;
    }
    .step-line {
      margin: 0 2px;
    }
  }
</style>
