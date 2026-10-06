<script lang="ts">
  import StatusBadge from '../../components/StatusBadge.svelte';
  import MetricCard from '../../components/MetricCard.svelte';

  let metrics = {
    new_leads_this_week: 5,
    applications_awaiting_review: 3,
    vendors_awaiting_contact: 8,
    qualified_vendors: 12,
    total_amount_pending: 2500,
    invoices_sent_unpaid: 4,
    overdue_invoices: 1,
    confirmed_bookings: 6,
    preparing_for_market: 3,
  };

  let awaitingPayment = [
    {
      id: 1,
      lead_business_name: 'The Good Brand',
      lead_email: 'hello@goodbrand.com',
      lead_phone: '555-1234',
      payment_status: 'invoice_sent',
    },
    {
      id: 2,
      lead_business_name: 'Vintage Collective',
      lead_email: 'info@vintage.com',
      lead_phone: '555-5678',
      payment_status: 'overdue',
    },
  ];

  let qualifiedNoInvoice = [
    {
      id: 3,
      lead_business_name: 'Modern Jewelry',
      lead_email: 'contact@jewelry.com',
      lead_phone: '555-9999',
      qualification_status: 'qualified',
    },
  ];
</script>

<div class="dashboard">
  <h1>Dashboard</h1>

  <div class="metrics-grid">
    <MetricCard title="New Leads This Week" value={metrics.new_leads_this_week} />
    <MetricCard title="Applications Awaiting Review" value={metrics.applications_awaiting_review} />
    <MetricCard title="Vendors Awaiting Contact" value={metrics.vendors_awaiting_contact} />
    <MetricCard title="Qualified Vendors" value={metrics.qualified_vendors} />
    <MetricCard title="Pending Payment" value={`$${metrics.total_amount_pending}`} subtitle="{metrics.invoices_sent_unpaid} invoices" highlight={true} />
    <MetricCard title="Overdue Invoices" value={metrics.overdue_invoices} isError={metrics.overdue_invoices > 0} />
    <MetricCard title="Confirmed Bookings" value={metrics.confirmed_bookings} />
    <MetricCard title="Preparing for Market" value={metrics.preparing_for_market} />
  </div>

  <div class="quick-actions">
    <h2>Quick Actions</h2>
    <div class="actions-grid">
      <a href="/vendors/new" class="action-btn">+ Create Vendor Lead</a>
      <a href="/vendors/import" class="action-btn">📥 Import CSV</a>
      <a href="/invoices" class="action-btn">📄 Manage Invoices</a>
      <a href="/markets" class="action-btn">📍 Markets</a>
    </div>
  </div>

  {#if awaitingPayment.length > 0}
    <div class="section">
      <h2>Vendors Awaiting Payment</h2>
      <div class="vendor-list">
        {#each awaitingPayment as vendor}
          <div class="vendor-item">
            <div class="vendor-info">
              <h4>{vendor.lead_business_name}</h4>
              <p class="vendor-meta">{vendor.lead_email} • {vendor.lead_phone}</p>
            </div>
            <div class="vendor-status">
              <StatusBadge status={vendor.payment_status} size="sm" />
            </div>
            <a href="/vendors/{vendor.id}" class="action-link">View</a>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  {#if qualifiedNoInvoice.length > 0}
    <div class="section">
      <h2>Qualified Vendors - Ready to Invoice</h2>
      <div class="vendor-list">
        {#each qualifiedNoInvoice as vendor}
          <div class="vendor-item">
            <div class="vendor-info">
              <h4>{vendor.lead_business_name}</h4>
              <p class="vendor-meta">{vendor.lead_email} • {vendor.lead_phone}</p>
            </div>
            <div class="vendor-status">
              <StatusBadge status={vendor.qualification_status} size="sm" />
            </div>
            <a href="/vendors/{vendor.id}/invoice/new" class="action-link">Create Invoice</a>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .dashboard {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }

  h1 {
    margin-bottom: 32px;
    font-size: 28px;
    font-weight: 600;
  }

  h2 {
    margin-bottom: 20px;
    font-size: 20px;
    font-weight: 600;
    margin-top: 32px;
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin-bottom: 40px;
  }

  .quick-actions {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 40px;
  }

  .actions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
  }

  .action-btn {
    display: block;
    padding: 12px 16px;
    background: #0284c7;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    text-align: center;
    font-weight: 500;
    transition: background 0.2s;
  }

  .action-btn:hover {
    background: #0369a1;
  }

  .section {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 24px;
  }

  .vendor-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .vendor-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px;
    background: #f8f9fb;
    border-radius: 6px;
    gap: 16px;
  }

  .vendor-info {
    flex: 1;
  }

  .vendor-info h4 {
    margin: 0 0 4px 0;
    font-size: 14px;
    font-weight: 600;
  }

  .vendor-meta {
    margin: 0;
    font-size: 12px;
    color: #999;
  }

  .vendor-status {
    width: 140px;
  }

  .action-link {
    color: #0284c7;
    text-decoration: none;
    font-size: 12px;
    font-weight: 600;
  }

  .action-link:hover {
    text-decoration: underline;
  }
</style>
