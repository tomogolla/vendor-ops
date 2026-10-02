<script lang="ts">
  import { enhance } from "$app/forms";
  import type { ActionData } from "./$types";

  let { form }: { form: ActionData | null } = $props();
  let submitting = $state(false);
</script>

<svelte:head><title>Sign in | Vendor OS</title></svelte:head>

<section class="login-card">
  <div class="brand">THE GOOD FLEA <span>VENDOR OS</span></div>
  <div>
    <p class="eyebrow">TEAM ACCESS</p>
    <h1>Welcome back</h1>
    <p class="intro">
      Sign in to manage vendor applications, bookings, and communications.
    </p>
  </div>
  <form
    method="POST"
    use:enhance={() => {
      submitting = true;
      return async ({ update }) => {
        await update();
        submitting = false;
      };
    }}
  >
    <label
      >Username<input
        name="username"
        autocomplete="username"
        value={form?.username ?? ""}
        required
      /></label
    >
    <label
      >Password<input
        name="password"
        type="password"
        autocomplete="current-password"
        required
      /></label
    >
    {#if form?.error}<p class="error" role="alert">{form.error}</p>{/if}
    <button disabled={submitting}
      >{submitting ? "Signing in…" : "Sign in"}</button
    >
  </form>
</section>

<style>
  .login-card {
    box-sizing: border-box;
    width: min(420px, 100%);
    padding: 34px;
    border: 1px solid #dedfe5;
    border-radius: 10px;
    background: white;
    box-shadow: 0 18px 45px rgb(34 49 74 / 9%);
  }
  .brand {
    margin-bottom: 44px;
    color: #004aad;
    font-size: 18px;
    font-weight: 700;
  }
  .brand span {
    display: block;
    margin-top: 5px;
    color: #989aa3;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.12em;
  }
  .eyebrow {
    margin: 0 0 7px;
    color: #9a9ca5;
    font-size: 9px;
    letter-spacing: 0.12em;
  }
  h1 {
    margin: 0;
    font-size: 25px;
  }
  .intro {
    margin: 9px 0 25px;
    color: #747680;
    font-size: 12px;
    line-height: 1.6;
  }
  form,
  label {
    display: grid;
    gap: 8px;
  }
  form {
    gap: 18px;
  }
  label {
    color: #464851;
    font-size: 11px;
    font-weight: 600;
  }
  input {
    box-sizing: border-box;
    width: 100%;
    border: 1px solid #d9dbe1;
    border-radius: 6px;
    padding: 11px 12px;
    background: #fff;
    color: #25252b;
    font: inherit;
    font-size: 13px;
  }
  input:focus {
    border-color: #004aad;
    outline: 2px solid rgb(0 74 173 / 15%);
  }
  button {
    border: 1px solid #004aad;
    border-radius: 6px;
    padding: 12px;
    background: #004aad;
    color: white;
    font: inherit;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
  }
  button:disabled {
    opacity: 0.65;
    cursor: wait;
  }
  .error {
    margin: -5px 0 0;
    border-radius: 5px;
    padding: 10px;
    background: #fff0ed;
    color: #922218;
    font-size: 11px;
  }
</style>
