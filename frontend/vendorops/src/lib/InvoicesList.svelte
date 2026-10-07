<script lang="ts">
  import type { VendorLead } from '$lib/vendor-leads';

  interface LineItem {
    id: number;
    item_type: string;
    description: string;
    quantity: number;
    unit_price: string;
    subtotal: string;
  }

  interface Invoice {
    id: number;
    number: string;
    status: 'draft' | 'sent' | 'paid' | 'cancelled';
    subtotal: string;
    discount_amount: string;
    total_amount: string;
    due_date: string;
    sent_at: string | null;
    cancelled_at: string | null;
    line_items?: LineItem[];
  }

  let { lead }: { lead: VendorLead } = $props();
  let invoices = $state<Invoice[]>([]);
  let loading = $state(false);
  let selectedInvoice = $state<Invoice | null>(null);
  let expandedInvoice = $state<number | null>(null);

  $effect(() => {
    loadInvoices();
  });

  async function loadInvoices() {
    loading = true;
    try {
      const response = await fetch(`/api/vendor-leads/${lead.id}/`);
      if (response.ok) {
        const data = await response.json();
        if (data.approval_invoice) {
          invoices = [data.approval_invoice];
        }
      }
    } catch (e) {
      console.error('Failed to load invoices:', e);
    } finally {
      loading = false;
    }
  }

  function getStatusColor(status: string) {
    const colors: Record<string, string> = {
      draft: '#fef3c7',
      sent: '#dbeafe',
      paid: '#dcfce7',
      cancelled: '#fee2e2',
    };
    return colors[status] || '#f3f4f6';
  }

  function getStatusTextColor(status: string) {
    const colors: Record<string, string> = {
      draft: '#78350f',
      sent: '#0c4a6e',
      paid: '#065f46',
      cancelled: '#7f1d1d',
    };
    return colors[status] || '#374151';
  }

  async function sendInvoice(invoice: Invoice) {
    try {
      const response = await fetch(`/api/vendor-leads/${lead.id}/invoices/${invoice.id}/send/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (response.ok) {
        const updated = await response.json();
        invoices = invoices.map(inv => inv.id === invoice.id ? updated : inv);
      }
    } catch (e) {
      console.error('Failed to send invoice:', e);
    }
  }

  async function cancelInvoice(invoice: Invoice) {
    if (!confirm('Are you sure you want to cancel this invoice?')) return;
    try {
      const response = await fetch(`/api/vendor-leads/${lead.id}/invoices/${invoice.id}/cancel/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (response.ok) {
        const updated = await response.json();
        invoices = invoices.map(inv => inv.id === invoice.id ? updated : inv);
      }
    } catch (e) {
      console.error('Failed to cancel invoice:', e);
    }
  }

  async function sendReminder(invoice: Invoice, reminderType: 'first' | 'second') {
    try {
      const response = await fetch(`/api/vendor-leads/${lead.id}/invoices/${invoice.id}/remind/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reminder_type: reminderType }),
      });
      if (response.ok) {
        const updated = await response.json();
        invoices = invoices.map(inv => inv.id === invoice.id ? updated : inv);
      }
    } catch (e) {
      console.error('Failed to send reminder:', e);
    }
  }
</script>

<div class="invoices-container">
  {#if loading}
    <p class="empty">Loading invoices...</p>
  {:else if invoices.length === 0}
    <p class="empty">No invoices yet. Use the "Accept application" button to create one.</p>
  {:else}
    <div class="invoices-list">
      {#each invoices as invoice (invoice.id)}
        <div class="invoice-card">
          <div class="invoice-header">
            <div>
              <strong>Invoice #{invoice.number}</strong>
              <span
                class="status-badge"
                style:background-color={getStatusColor(invoice.status)}
                style:color={getStatusTextColor(invoice.status)}
              >
                {invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}
              </span>
            </div>
            <div class="invoice-amount">
              <strong>${parseFloat(invoice.total_amount).toFixed(2)}</strong>
              <span class="due-date">Due: {new Date(invoice.due_date).toLocaleDateString()}</span>
            </div>
          </div>

          <div class="invoice-details">
            <button
              class="expand-button"
              onclick={() => {
                expandedInvoice = expandedInvoice === invoice.id ? null : invoice.id;
              }}
            >
              {expandedInvoice === invoice.id ? '▼' : '▶'} View line items
            </button>

            {#if expandedInvoice === invoice.id && invoice.line_items}
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
                  {#each invoice.line_items as item}
                    <tr>
                      <td>{item.description}</td>
                      <td style="text-align: right;">{item.quantity}</td>
                      <td style="text-align: right;">${parseFloat(item.unit_price).toFixed(2)}</td>
                      <td style="text-align: right;">${parseFloat(item.subtotal).toFixed(2)}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>

              <div class="totals">
                <div class="total-row">
                  <span>Subtotal</span>
                  <strong>${parseFloat(invoice.subtotal).toFixed(2)}</strong>
                </div>
                {#if parseFloat(invoice.discount_amount) > 0}
                  <div class="total-row">
                    <span>Discount</span>
                    <strong>-${parseFloat(invoice.discount_amount).toFixed(2)}</strong>
                  </div>
                {/if}
                <div class="total-row grand-total">
                  <span>Total</span>
                  <strong>${parseFloat(invoice.total_amount).toFixed(2)}</strong>
                </div>
              </div>
            {/if}
          </div>

          <div class="invoice-actions">
            {#if invoice.status === 'draft'}
              <button class="action-btn send" onclick={() => sendInvoice(invoice)}>
                Send
              </button>
              <button class="action-btn cancel" onclick={() => cancelInvoice(invoice)}>
                Cancel
              </button>
            {:else if invoice.status === 'sent'}
              <button class="action-btn remind" onclick={() => sendReminder(invoice, 'first')}>
                Send reminder
              </button>
              <button class="action-btn cancel" onclick={() => cancelInvoice(invoice)}>
                Cancel
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .invoices-container {
    width: 100%;
  }
  .empty {
    color: #818390;
    text-align: center;
    padding: 40px 20px;
    font-size: 13px;
  }
  .invoices-list {
    display: grid;
    gap: 16px;
  }
  .invoice-card {
    border: 1px solid #dedfe5;
    border-radius: 8px;
    overflow: hidden;
  }
  .invoice-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    padding: 14px;
    background: #f8f9fb;
    border-bottom: 1px solid #dedfe5;
  }
  .invoice-header > div:first-child {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .invoice-header strong {
    font-size: 13px;
  }
  .status-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: capitalize;
  }
  .invoice-amount {
    text-align: right;
  }
  .invoice-amount strong {
    display: block;
    font-size: 14px;
  }
  .due-date {
    display: block;
    font-size: 11px;
    color: #818390;
  }
  .invoice-details {
    padding: 14px;
    border-bottom: 1px solid #dedfe5;
  }
  .expand-button {
    background: white;
    border: 0;
    color: #004aad;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .expand-button:hover {
    text-decoration: underline;
  }
  .line-items-table {
    width: 100%;
    margin-top: 12px;
    margin-bottom: 12px;
    border-collapse: collapse;
    font-size: 12px;
  }
  .line-items-table th {
    text-align: left;
    padding: 8px 0;
    border-bottom: 1px solid #dedfe5;
    font-weight: 600;
    color: #565966;
  }
  .line-items-table td {
    padding: 6px 0;
    border-bottom: 1px solid #f0f1f5;
  }
  .totals {
    background: #f8f9fb;
    border-radius: 6px;
    padding: 10px;
    margin-top: 10px;
  }
  .total-row {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    padding: 4px 0;
  }
  .total-row.grand-total {
    border-top: 1px solid #dedfe5;
    padding-top: 6px;
    margin-top: 6px;
    font-weight: 600;
    color: #26262c;
  }
  .invoice-actions {
    display: flex;
    gap: 8px;
    padding: 12px 14px;
    background: #f8f9fb;
  }
  .action-btn {
    flex: 1;
    padding: 8px 12px;
    border-radius: 4px;
    border: 1px solid #cbd1da;
    background: white;
    color: #26262c;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
  }
  .action-btn:hover {
    background: #fafbfc;
  }
  .action-btn.send {
    border-color: #004aad;
    color: #004aad;
  }
  .action-btn.send:hover {
    background: #f0f5ff;
  }
  .action-btn.remind {
    border-color: #f59e0b;
    color: #f59e0b;
  }
  .action-btn.remind:hover {
    background: #fef8e7;
  }
  .action-btn.cancel {
    border-color: #ef4444;
    color: #ef4444;
  }
  .action-btn.cancel:hover {
    background: #fef2f2;
  }
</style>
