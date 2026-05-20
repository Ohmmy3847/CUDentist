import type { User } from './types'

/**
 * Returns the default landing page for a user based on their permissions.
 * Use this instead of hardcoding '/dashboard' or '/login' in access checks.
 */
export function getHomeRoute(user: Pick<User, 'roles' | 'is_superuser'>): string {
  const roles = user.roles ?? []
  if (roles.includes('view_cases') || roles.includes('view_all_cases')) return '/dashboard'
  if (user.is_superuser || roles.includes('manage_users')) return '/settings/users'
  if (roles.includes('manage_docs')) return '/data/documents'
  return '/settings/account'
}
