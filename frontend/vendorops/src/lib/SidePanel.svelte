<script lang="ts">
	import { page } from '$app/state';
	import { resolve } from '$app/paths';

	let expanded = $state(false);
	const items = [
		{ label: 'Dashboard', href: '/dashboard' },
		{ label: 'Vendors', href: '/vendors' },
		{ label: 'Applications', href: '/applications' },
		{ label: 'Markets', href: '/markets' },
		{ label: 'Communications', href: '/communications' },
		{ label: 'Payments', href: '/payments' },
		{ label: 'Market weekends', href: '/market-weekends' }
	] as const;
</script>

<aside class="side-panel">
	<div class="panel-heading">
		<a class="brand" href={resolve('/dashboard')} onclick={() => (expanded = false)}>
			<span>THE GOOD FLEA<small>VENDOR OS</small></span>
		</a>
		<button
			class="menu-toggle"
			aria-expanded={expanded}
			aria-controls="side-panel-navigation"
			onclick={() => (expanded = !expanded)}
		>
			{expanded ? 'Close menu' : 'Menu'}
		</button>
	</div>
	<nav id="side-panel-navigation" aria-label="Main navigation" class:expanded>
		<p class="section-label">Workspace</p>
		<ul>
			{#each items as item}
				{@const href = resolve(item.href)}
				{@const active = page.url.pathname === href || page.url.pathname.startsWith(`${href}/`)}
				<li>
					<a
						{href}
						class:active
						aria-current={active ? 'page' : undefined}
						onclick={() => (expanded = false)}
					>
						{item.label}
					</a>
				</li>
			{/each}
		</ul>
	</nav>
</aside>

<style>
	.side-panel {
		box-sizing: border-box;
		position: sticky;
		top: 0;
		width: 220px;
		flex-shrink: 0;
		height: 100dvh;
		overflow-y: auto;
		padding: 20px 16px;
		background: #fcf0ba;
		color: #004aad;
	}
	.brand {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 0;
		color: inherit;
		font-size: 16px;
		font-weight: 700;
		text-decoration: none;
	}
	.brand small { display: block; margin-top: 8px; font-size: 10px; font-weight: 400; color: #96979d; letter-spacing: .06em; }
	.section-label {
		margin: 40px 14px 12px;
		color: #004aad;
		font-size: 8px;
		font-weight: 500;
		letter-spacing: 0.12em;
		text-transform: uppercase;
	}
	ul { list-style: none; margin: 0; padding: 0; }
	li + li { margin-top: 6px; }
	li a {
		display: block;
		padding: 10px 12px;
		border-radius: 8px;
		color: #004aad;
		font-size: 14px;
		text-decoration: none;
	}
	li a:hover { background: #004aad; color: white; }
	li a.active { background: #08739d; color: #fff; font-weight: 600; }
	a:focus-visible, button:focus-visible { outline: 2px solid #004aad; outline-offset: 4px; }
	.menu-toggle { display: none; }
	@media (max-width: 760px) {
		.side-panel { position: static; width: 100%; height: auto; padding: 18px; }
		.panel-heading { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
		.menu-toggle {
			display: block;
			border: 1px solid #fcb533;
			border-radius: 6px;
			padding: 8px 12px;
			background: transparent;
			color: inherit;
			font: inherit;
			cursor: pointer;
		}
		nav { display: none; }
		nav.expanded { display: block; }
		.section-label { margin-top: 24px; }
	}
</style>
