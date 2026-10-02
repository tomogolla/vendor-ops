import { dev } from '$app/environment';
import { fail, redirect } from '@sveltejs/kit';
import { AUTH_COOKIE, djangoApi } from '$lib/server/auth';
import type { Actions } from './$types';

export const actions: Actions = {
  default: async ({ request, fetch, cookies, url }) => {
    const form = await request.formData();
    const username = String(form.get('username') ?? '').trim();
    const password = String(form.get('password') ?? '');
    if (!username || !password) return fail(400, { username, error: 'Enter your username and password.' });

    let response: Response;
    try {
      response = await fetch(`${djangoApi()}/api/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
    } catch {
      return fail(503, { username, error: 'The sign-in service is unavailable. Please try again.' });
    }
    if (!response.ok) return fail(400, { username, error: 'The username or password is incorrect.' });

    const { token } = await response.json() as { token: string };
    cookies.set(AUTH_COOKIE, token, {
      path: '/', httpOnly: true, sameSite: 'lax', secure: !dev, maxAge: 60 * 60 * 12
    });
    const requested = url.searchParams.get('next');
    const destination = requested?.startsWith('/') && !requested.startsWith('//') ? requested : '/dashboard';
    redirect(303, destination);
  }
};
