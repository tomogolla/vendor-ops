<script lang="ts">
  interface Props {
    title: string;
    value: string | number;
    subtitle?: string;
    highlight?: boolean;
    isError?: boolean;
  }

  let { title, value, subtitle, highlight = false, isError = false }: Props = $props();
</script>

<div class="metric-card" class:highlight class:error={isError}>
  <h3>{title}</h3>
  <p class="metric-value" class:error-text={isError}>{value}</p>
  {#if subtitle}
    <p class="subtitle">{subtitle}</p>
  {/if}
</div>

<style>
  .metric-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
  }

  .metric-card.highlight {
    background: #f0f9ff;
    border-color: #0284c7;
  }

  .metric-card.error {
    background: #fef2f2;
    border-color: #fecaca;
  }

  h3 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: #666;
    font-weight: 500;
  }

  .metric-value {
    margin: 0;
    font-size: 32px;
    font-weight: 700;
    color: #1f2937;
  }

  .metric-value.error-text {
    color: #dc2626;
  }

  .subtitle {
    margin: 8px 0 0 0;
    font-size: 12px;
    color: #999;
  }
</style>
