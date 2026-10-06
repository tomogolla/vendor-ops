<script>
  import { goto } from '$app/navigation';
</script>

<div class="home">
  <h1>Vendor Operations Platform</h1>
  <p>Manage vendors, invoices, bookings, and market operations</p>

  <nav class="main-nav">
    <a href="/dashboard" class="nav-card">
      <h3>📊 Dashboard</h3>
      <p>View metrics, upcoming actions, and quick stats</p>
    </a>
    <a href="/vendors" class="nav-card">
      <h3>👥 Vendors</h3>
      <p>Manage vendor profiles and applications</p>
    </a>
    <a href="/invoices" class="nav-card">
      <h3>💰 Invoices</h3>
      <p>Create and manage invoices and payments</p>
    </a>
    <a href="/markets" class="nav-card">
      <h3>📍 Markets</h3>
      <p>Manage market products and bookings</p>
    </a>
  </nav>
</div>

<style>
  .home {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 24px;
  }

  h1 {
    font-size: 32px;
    margin-bottom: 8px;
  }

  > p {
    font-size: 16px;
    color: #666;
    margin-bottom: 40px;
  }

  .main-nav {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
  }

  .nav-card {
    display: block;
    padding: 24px;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.2s;
  }

  .nav-card:hover {
    border-color: #0284c7;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.1);
    transform: translateY(-2px);
  }

  .nav-card h3 {
    margin: 0 0 8px 0;
    font-size: 18px;
    color: #1f2937;
  }

  .nav-card p {
    margin: 0;
    font-size: 14px;
    color: #666;
  }
</style>
