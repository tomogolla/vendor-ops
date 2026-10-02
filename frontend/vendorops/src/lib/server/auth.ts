import { env } from '$env/dynamic/private';

export const AUTH_COOKIE = 'vendorops_session';
export const djangoApi = () => (env.DJANGO_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

export type AuthUser = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  display_name: string;
};
