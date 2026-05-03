/**
 * Tests for AuthProtectedRoutes Component
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import {
  AuthProtectedRoutes,
  useAuth,
  useHasRole,
  canAccessRoute,
  withAuthProtection,
} from '../../src/dashboard/static/tsx/components/AuthProtectedRoutes';

const TestComponent = () => <div>Protected Content</div>;

describe('AuthProtectedRoutes Component', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should render children when authenticated', () => {
    localStorage.setItem('auth_token', 'test_token');

    render(
      <AuthProtectedRoutes isAuthenticated={true}>
        <TestComponent />
      </AuthProtectedRoutes>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should show auth required when not authenticated', () => {
    render(
      <AuthProtectedRoutes isAuthenticated={false}>
        <TestComponent />
      </AuthProtectedRoutes>
    );

    expect(screen.getByText('Authentication required')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should use fallback when not authenticated', () => {
    render(
      <AuthProtectedRoutes isAuthenticated={false} fallback={<div>Custom Fallback</div>}>
        <TestComponent />
      </AuthProtectedRoutes>
    );

    expect(screen.getByText('Custom Fallback')).toBeInTheDocument();
  });

  it('should check role when provided', () => {
    render(
      <AuthProtectedRoutes
        isAuthenticated={true}
        requiredRole="admin"
        userRole="admin"
      >
        <TestComponent />
      </AuthProtectedRoutes>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should deny access when role does not match', () => {
    render(
      <AuthProtectedRoutes
        isAuthenticated={true}
        requiredRole="admin"
        userRole="user"
      >
        <TestComponent />
      </AuthProtectedRoutes>
    );

    expect(screen.getByText('Access denied')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });
});

describe('useAuth Hook', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should return not authenticated when no token', () => {
    const TestHookComponent = () => {
      const { isAuthenticated } = useAuth();
      return <div>{isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</div>;
    };

    render(<TestHookComponent />);
    expect(screen.getByText('Not Authenticated')).toBeInTheDocument();
  });

  it('should return authenticated when token exists', () => {
    localStorage.setItem('auth_token', 'test_token');

    const TestHookComponent = () => {
      const { isAuthenticated } = useAuth();
      return <div>{isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</div>;
    };

    render(<TestHookComponent />);
    expect(screen.getByText('Authenticated')).toBeInTheDocument();
  });

  it('should return user role', () => {
    localStorage.setItem('user_role', 'admin');

    const TestHookComponent = () => {
      const { userRole } = useAuth();
      return <div>Role: {userRole}</div>;
    };

    render(<TestHookComponent />);
    expect(screen.getByText('Role: admin')).toBeInTheDocument();
  });

  it('should return user ID', () => {
    localStorage.setItem('user_id', '12345');

    const TestHookComponent = () => {
      const { userId } = useAuth();
      return <div>ID: {userId}</div>;
    };

    render(<TestHookComponent />);
    expect(screen.getByText('ID: 12345')).toBeInTheDocument();
  });

  it('should logout', () => {
    localStorage.setItem('auth_token', 'test_token');
    localStorage.setItem('user_role', 'admin');
    localStorage.setItem('user_id', '12345');

    const TestHookComponent = () => {
      const { logout } = useAuth();
      logout();
      return <div>Logged out</div>;
    };

    render(<TestHookComponent />);

    expect(localStorage.getItem('auth_token')).toBeNull();
    expect(localStorage.getItem('user_role')).toBeNull();
    expect(localStorage.getItem('user_id')).toBeNull();
  });
});

describe('useHasRole Hook', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should return true for matching role', () => {
    localStorage.setItem('user_role', 'admin');

    const TestHookComponent = () => {
      const hasAdminRole = useHasRole('admin');
      return <div>{hasAdminRole ? 'Has Admin' : 'No Admin'}</div>;
    };

    render(<TestHookComponent />);
    expect(screen.getByText('Has Admin')).toBeInTheDocument();
  });

  it('should return false for non-matching role', () => {
    localStorage.setItem('user_role', 'user');

    const TestHookComponent = () => {
      const hasAdminRole = useHasRole('admin');
      return <div>{hasAdminRole ? 'Has Admin' : 'No Admin'}</div>;
    };

    render(<TestHookComponent />);
    expect(screen.getByText('No Admin')).toBeInTheDocument();
  });
});

describe('canAccessRoute Function', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should allow access when authenticated', () => {
    localStorage.setItem('auth_token', 'test_token');

    const result = canAccessRoute();
    expect(result).toBe(true);
  });

  it('should deny access when not authenticated', () => {
    const result = canAccessRoute();
    expect(result).toBe(false);
  });

  it('should check role requirement', () => {
    localStorage.setItem('auth_token', 'test_token');
    localStorage.setItem('user_role', 'admin');

    const result = canAccessRoute('admin');
    expect(result).toBe(true);
  });

  it('should deny access with wrong role', () => {
    localStorage.setItem('auth_token', 'test_token');
    localStorage.setItem('user_role', 'user');

    const result = canAccessRoute('admin');
    expect(result).toBe(false);
  });
});

describe('withAuthProtection HOC', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should wrap component with auth check', () => {
    localStorage.setItem('auth_token', 'test_token');

    const ProtectedComponent = withAuthProtection(TestComponent);
    render(<ProtectedComponent />);

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should show auth required when not authenticated', () => {
    const ProtectedComponent = withAuthProtection(TestComponent);
    render(<ProtectedComponent />);

    expect(screen.getByText('Authentication required')).toBeInTheDocument();
  });

  it('should check role requirement', () => {
    localStorage.setItem('auth_token', 'test_token');
    localStorage.setItem('user_role', 'user');

    const ProtectedComponent = withAuthProtection(TestComponent, { requiredRole: 'admin' });
    render(<ProtectedComponent />);

    expect(screen.getByText('Insufficient permissions')).toBeInTheDocument();
  });
});
