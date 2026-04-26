/**
 * AuthProtectedRoutes Component
 * Wraps routes with authentication checks and redirects
 */

import React, { ReactNode } from 'react';

export interface ProtectedRouteProps {
  children: ReactNode;
  isAuthenticated: boolean;
  fallback?: ReactNode;
  requiredRole?: string;
  userRole?: string;
}

/**
 * Higher-order component for route protection
 */
export const withAuthProtection = (
  Component: React.ComponentType<any>,
  options: { requiredRole?: string } = {}
) => {
  return (props: any) => {
    const isAuthenticated = !!localStorage.getItem('auth_token');
    const userRole = localStorage.getItem('user_role');

    if (!isAuthenticated) {
      return <div className="auth-required">Authentication required. Please log in.</div>;
    }

    if (options.requiredRole && userRole !== options.requiredRole) {
      return <div className="auth-forbidden">Insufficient permissions for this route.</div>;
    }

    return <Component {...props} />;
  };
};

/**
 * AuthProtectedRoutes component
 * Checks authentication status and conditional rendering
 */
export const AuthProtectedRoutes: React.FC<ProtectedRouteProps> = ({
  children,
  isAuthenticated,
  fallback,
  requiredRole,
  userRole,
}) => {
  if (!isAuthenticated) {
    return fallback || <div className="auth-required">Authentication required</div>;
  }

  if (requiredRole && userRole !== requiredRole) {
    return fallback || <div className="auth-forbidden">Access denied</div>;
  }

  return <>{children}</>;
};

/**
 * Hook for checking authentication status
 */
export function useAuth() {
  const isAuthenticated = !!localStorage.getItem('auth_token');
  const userRole = localStorage.getItem('user_role') || '';
  const userId = localStorage.getItem('user_id') || '';

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_id');
  };

  return {
    isAuthenticated,
    userRole,
    userId,
    logout,
  };
}

/**
 * Hook for checking specific role permissions
 */
export function useHasRole(requiredRole: string): boolean {
  const { userRole } = useAuth();
  return userRole === requiredRole;
}

/**
 * Route guard function
 */
export function canAccessRoute(requiredRole?: string): boolean {
  const auth = useAuth();
  if (!auth.isAuthenticated) {
    return false;
  }

  if (requiredRole && auth.userRole !== requiredRole) {
    return false;
  }

  return true;
}
