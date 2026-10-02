import { dev } from '$app/environment';
import { redirect, type RequestHandler } from '@sveltejs/kit';
import { AUTH_COOKIE, djangoApi } from '$lib/server/auth';

export const POST: RequestHandler = async ({ cookies, fetch }) => {
  try { await fetch(`${djangoApi()}/api/auth/logout/`, { method: 'POST' }); }
  finally { cookies.delete(AUTH_COOKIE, { path: '/', secure: !dev }); }
  redirect(303, '/login');
};
