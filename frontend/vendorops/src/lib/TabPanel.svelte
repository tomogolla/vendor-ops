<script lang="ts">
  interface Tab {
    id: string;
    label: string;
  }

  let { tabs, activeTab = tabs[0]?.id }: { tabs: Tab[]; activeTab?: string } = $props();
  let active = $state(activeTab || tabs[0]?.id);

  function setActive(tabId: string) {
    active = tabId;
  }
</script>

<div class="tab-panel">
  <div class="tab-buttons" role="tablist">
    {#each tabs as tab}
      <button
        role="tab"
        aria-selected={active === tab.id}
        aria-controls={`tab-content-${tab.id}`}
        class:active={active === tab.id}
        onclick={() => setActive(tab.id)}
      >
        {tab.label}
      </button>
    {/each}
  </div>

  <div class="tab-content">
    <slot {active} />
  </div>
</div>

<style>
  .tab-panel {
    display: flex;
    flex-direction: column;
  }
  .tab-buttons {
    display: flex;
    gap: 0;
    border-bottom: 1px solid #dedfe5;
    margin-bottom: 0;
  }
  button {
    padding: 14px 16px;
    border: 0;
    border-bottom: 3px solid transparent;
    background: white;
    color: #565966;
    font: inherit;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
  }
  button:hover {
    background: #f8f9fb;
  }
  button.active {
    color: #004aad;
    border-bottom-color: #004aad;
  }
  button:focus-visible {
    outline: 2px solid #004aad;
    outline-offset: -2px;
  }
  .tab-content {
    padding-top: 20px;
  }
</style>
