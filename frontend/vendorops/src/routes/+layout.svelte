<script lang="ts">
  import favicon from "$lib/assets/favicon.svg";

  let { children } = $props();
  import Header from "$lib/header.svelte";
  import SidePanel from "$lib/SidePanel.svelte";
  import { page } from "$app/state";
  const isAuthPage = $derived(page.route.id?.startsWith("/(auth)") ?? false);
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<div class="app-layout">
  {#if !isAuthPage}<SidePanel />{/if}
  <div class="page-layout">
    {#if !isAuthPage}<Header />{/if}
    <main>{@render children()}</main>
  </div>
</div>

<style>
  :global(body) {
    margin: 0;
	font-family: "Poppins", sans-serif;
  	font-optical-sizing: auto;
    color: #26262c;
    background: #f8f9fb;
  }
  .app-layout {
    display: flex;
    min-height: 100dvh;
  }
  .page-layout {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-width: 0;
  }
  main {
    flex: 1;
    padding: 24px;
  }
  @media (max-width: 760px) {
    .app-layout {
      flex-direction: column;
    }
    main {
      padding: 20px;
    }
  }
</style>
