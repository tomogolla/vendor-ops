<script lang="ts">
  let { name, options, initial = '', invalid = false, labelId }: {
    name: string;
    options: readonly string[];
    initial?: string;
    invalid?: boolean;
    labelId: string;
  } = $props();

  const delimiter = ' | ';
  let selected = $derived(initial ? initial.split(delimiter).filter(Boolean) : []);
  const previous = $derived(selected.filter((item) => !options.includes(item)));
  const chosen = $derived(options.filter((item) => selected.includes(item)));

  function toggle(option: string, checked: boolean) {
    selected = options.filter((item) => item !== option ? selected.includes(item) : checked);
  }
</script>

<input type="hidden" {name} value={selected.join(delimiter)} />
<details class="dropdown" class:invalid aria-labelledby={labelId}>
  <summary>{chosen.length ? `${chosen.length} weekend${chosen.length === 1 ? '' : 's'} selected` : previous.length ? 'Previously entered dates' : 'Select weekends'}</summary>
  <div class="options">
    {#if previous.length}
      <p class="previous">Previously entered: {previous.join(', ')}. Select a weekend to replace this entry.</p>
    {/if}
    {#each options as option}
      <label>
        <input type="checkbox" checked={selected.includes(option)} onchange={(event) => toggle(option, event.currentTarget.checked)} />
        <span>{option}</span>
      </label>
    {/each}
  </div>
</details>
{#if chosen.length}
  <p class="selected-list">{chosen.join(', ')}</p>
{/if}

<style>
  .dropdown { border: 1px solid #99b7f5; border-radius: 7px; background: white; color: #20352f; font-size: 13px; }
  .dropdown.invalid { border-color: #b42318; }
  summary { cursor: pointer; padding: 11px 12px; }
  summary:focus-visible, input:focus-visible { outline: 2px solid #004aad; outline-offset: 2px; }
  .options { max-height: 280px; overflow-y: auto; padding: 6px; border-top: 1px solid #dbe5f7; }
  label { display: flex; align-items: center; gap: 10px; margin: 0; padding: 7px 6px; font-weight: 400; cursor: pointer; }
  label:hover { background: #eef4ff; }
  input[type='checkbox'] { width: 18px; height: 18px; margin: 0; accent-color: #004aad; flex-shrink: 0; }
  .previous { padding: 0 6px; color: #5d6476; font-size: 12px; line-height: 1.5; }
  .selected-list { margin: 6px 0 0; color: #4c6080; font-size: 12px; line-height: 1.5; }
</style>
