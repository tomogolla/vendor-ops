<script>let { children } = $props();</script>
<div class="auth-shell">{@render children()}</div>
<style>
  .auth-shell { min-height: 100%; display: grid; place-items: center; padding: 32px 20px; background: linear-gradient(135deg, #fff8d7 0 42%, #f7f8fb 42%); }
</style>
