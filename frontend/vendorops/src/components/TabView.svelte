<script lang="ts">
  interface Tab {
    id: string;
    label: string;
  }

  interface Props {
    tabs: Tab[];
    activeTab: string;
    onTabChange: (tabId: string) => void;
  }

  let { tabs, activeTab, onTabChange }: Props = $props();
</script>

<div class="tab-view">
  <div class="tab-buttons">
    {#each tabs as tab}
      <button
        class="tab-button"
        class:active={activeTab === tab.id}
        onclick={() => onTabChange(tab.id)}
      >
        {tab.label}
      </button>
    {/each}
  </div>
  <div class="tab-content">
    <slot />
  </div>
</div>

<style>
  .tab-view {
    display: flex;
    flex-direction: column;
  }

  .tab-buttons {
    display: flex;
    gap: 0;
    border-bottom: 2px solid #e5e7eb;
  }

  .tab-button {
    flex: 0 1 auto;
    padding: 12px 20px;
    background: none;
    border: none;
    color: #666;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
  }

  .tab-button:hover {
    color: #333;
  }

  .tab-button.active {
    color: #0284c7;
    border-bottom-color: #0284c7;
  }

  .tab-content {
    padding-top: 20px;
  }
</style>
