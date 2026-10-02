<script lang="ts">
  import { page } from '$app/state';
  const title = $derived(page.params.vendorId
    ? 'Vendor lead/applicant profile'
    : (page.url.pathname.split('/').filter(Boolean)[0] || 'Dashboard').replaceAll('-', ' '));
</script>

<header class="layout-header">
  <span>{title}</span>
  {#if page.data.user}
    <div class="account"><span>{page.data.user.display_name}</span><form method="POST" action="/logout"><button type="submit">Sign out</button></form></div>
  {/if}
</header>

<style>
  .layout-header { box-sizing: border-box; min-height: 56px; display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 12px 24px; background: white; border-bottom: 1px solid #dedfe5; color: #25252b; font-size: 15px; font-weight: 600; }
  .layout-header > span::first-letter { text-transform: uppercase; }
  .account { display: flex; align-items: center; gap: 12px; color: #666973; font-size: 11px; font-weight: 500; }
  form { margin: 0; }
  button { border: 1px solid #d9dbe1; border-radius: 5px; padding: 7px 10px; background: white; color: #34353c; font: inherit; cursor: pointer; }
  button:hover { border-color: #004aad; color: #004aad; }
</style>
