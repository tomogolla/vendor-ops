import { dev } from '$app/environment';
import { redirect, type Handle, type HandleFetch } from '@sveltejs/kit';
import { AUTH_COOKIE, djangoApi, type AuthUser } from '$lib/server/auth';

const isPublicRoute = (pathname: string) => pathname.startsWith('/login');

export const handleFetch: HandleFetch = async ({ event, request, fetch }) => {
  if (request.url.startsWith(`${djangoApi()}/api/`)) {
    const token = event.cookies.get(AUTH_COOKIE);
    if (token && !request.headers.has('authorization')) {
      request.headers.set('authorization', `Token ${token}`);
    }
  }
  return fetch(request);
};

export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get(AUTH_COOKIE);
  let user: AuthUser | null = null;

  if (token) {
    try {
      const response = await event.fetch(`${djangoApi()}/api/auth/me/`);
      if (response.ok) user = (await response.json() as { user: AuthUser }).user;
    } catch {
      // Treat an unavailable or expired authentication service as signed out.
    }
    if (!user) event.cookies.delete(AUTH_COOKIE, { path: '/', secure: !dev });
  }

  event.locals.user = user;
  if (!user && !isPublicRoute(event.url.pathname)) {
    const next = `${event.url.pathname}${event.url.search}`;
    redirect(303, `/login?next=${encodeURIComponent(next)}`);
  }
  if (user && isPublicRoute(event.url.pathname)) redirect(303, '/dashboard');

  return resolve(event);
};
