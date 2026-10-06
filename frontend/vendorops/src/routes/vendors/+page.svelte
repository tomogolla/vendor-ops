<script lang="ts">
  import StatusBadge from '../../components/StatusBadge.svelte';

  let vendors = [
    {
      id: 1,
      lead_business_name: 'The Good Brand',
      lead_email: 'hello@goodbrand.com',
      lead_phone: '555-1234',
      qualification_status: 'qualified',
      payment_status: 'invoice_sent',
      booking_status: 'confirmed',
    },
    {
      id: 2,
      lead_business_name: 'Vintage Collective',
      lead_email: 'info@vintage.com',
      lead_phone: '555-5678',
      qualification_status: 'qualified',
      payment_status: 'overdue',
      booking_status: 'preparing',
    },
    {
      id: 3,
      lead_business_name: 'Modern Jewelry',
      lead_email: 'contact@jewelry.com',
      lead_phone: '555-9999',
      qualification_status: 'qualified',
      payment_status: 'not_invoiced',
      booking_status: 'not_booked',
    },
  ];

  let search = '';
  let statusFilter = '';

  let filteredVendors = $derived(
    vendors.filter((v) => {
      const matchesSearch =
        !search ||
        v.lead_business_name.toLowerCase().includes(search.toLowerCase()) ||
        v.lead_email.toLowerCase().includes(search.toLowerCase());
      const matchesStatus = !statusFilter || v.qualification_status === statusFilter;
      return matchesSearch && matchesStatus;
    })
  );
</script>

<div class="vendors-page">
  <h1>Vendor Management</h1>

  <div class="controls">
    <div class="search-box">
      <input
        type="text"
        placeholder="Search by name or email..."
        bind:value={search}
      />
    </div>
    <select bind:value={statusFilter}>
      <option value="">All Statuses</option>
      <option value="unreviewed">Unreviewed</option>
      <option value="contact_needed">Contact Needed</option>
      <option value="qualified">Qualified</option>
      <option value="not_qualified">Not Qualified</option>
    </select>
    <a href="/vendors/new" class="btn-primary">+ New Vendor</a>
  </div>

  <div class="vendors-table">
    <table>
      <thead>
        <tr>
          <th>Business Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Status</th>
          <th>Payment</th>
          <th>Booking</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {#each filteredVendors as vendor}
          <tr>
            <td><strong>{vendor.lead_business_name}</strong></td>
            <td>{vendor.lead_email}</td>
            <td>{vendor.lead_phone}</td>
            <td><StatusBadge status={vendor.qualification_status} size="sm" /></td>
            <td><StatusBadge status={vendor.payment_status} size="sm" /></td>
            <td><StatusBadge status={vendor.booking_status} size="sm" /></td>
            <td>
              <a href="/vendors/{vendor.id}" class="link">View</a>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
    {#if filteredVendors.length === 0}
      <p class="empty">No vendors found</p>
    {/if}
  </div>
</div>

<style>
  .vendors-page {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
  }

  h1 {
    margin-bottom: 24px;
    font-size: 28px;
    font-weight: 600;
  }

  .controls {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    align-items: center;
  }

  .search-box {
    flex: 1;
  }

  .search-box input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    font-size: 14px;
  }

  .controls select {
    padding: 10px 12px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    font-size: 14px;
  }

  .btn-primary {
    padding: 10px 16px;
    background: #0284c7;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    font-weight: 500;
    white-space: nowrap;
  }

  .btn-primary:hover {
    background: #0369a1;
  }

  .vendors-table {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    overflow: hidden;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  thead {
    background: #f8f9fb;
    border-bottom: 1px solid #e5e7eb;
  }

  th {
    padding: 12px;
    text-align: left;
    font-weight: 600;
    font-size: 13px;
    color: #666;
  }

  td {
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
    font-size: 14px;
  }

  tbody tr:hover {
    background: #f8f9fb;
  }

  .link {
    color: #0284c7;
    text-decoration: none;
    font-weight: 500;
  }

  .link:hover {
    text-decoration: underline;
  }

  .empty {
    padding: 40px 12px;
    text-align: center;
    color: #999;
  }
</style>
