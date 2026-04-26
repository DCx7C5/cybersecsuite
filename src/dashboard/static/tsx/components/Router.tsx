/**
 * Router Component
 * React Router v7 configuration with lazy loading
 */

import React, { Suspense, lazy, ReactNode } from 'react';

export interface RouteConfig {
  path: string;
  name: string;
  component?: React.ComponentType<any>;
  lazy?: () => Promise<{ default: React.ComponentType<any> }>;
  children?: RouteConfig[];
  requiredRole?: string;
  icon?: string;
}

/**
 * Router Provider that manages navigation state
 */
export interface RouterContextType {
  currentRoute: string;
  navigate: (path: string) => void;
  routeParams: Record<string, string>;
}

const RouterContext = React.createContext<RouterContextType | undefined>(undefined);

/**
 * Hook for accessing router context
 */
export function useRouter() {
  const context = React.useContext(RouterContext);
  if (!context) {
    throw new Error('useRouter must be used within RouterProvider');
  }
  return context;
}

/**
 * Router Provider component
 */
export interface RouterProviderProps {
  initialRoute?: string;
  children: ReactNode;
}

export const RouterProvider: React.FC<RouterProviderProps> = ({ initialRoute = '/', children }) => {
  const [currentRoute, setCurrentRoute] = React.useState<string>(initialRoute);
  const [routeParams, setRouteParams] = React.useState<Record<string, string>>({});

  const navigate = React.useCallback((path: string) => {
    setCurrentRoute(path);
    window.history.pushState({ route: path }, '', path);
  }, []);

  React.useEffect(() => {
    const handlePopState = (event: PopStateEvent) => {
      if (event.state?.route) {
        setCurrentRoute(event.state.route);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const value: RouterContextType = {
    currentRoute,
    navigate,
    routeParams,
  };

  return <RouterContext.Provider value={value}>{children}</RouterContext.Provider>;
};

/**
 * Link component for navigation
 */
export interface LinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  to: string;
  children: ReactNode;
  activeClassName?: string;
  exact?: boolean;
}

export const Link: React.FC<LinkProps> = ({
  to,
  children,
  activeClassName = 'active',
  exact = false,
  className = '',
  ...props
}) => {
  const { currentRoute, navigate } = useRouter();
  const isActive = exact ? currentRoute === to : currentRoute.startsWith(to);

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    navigate(to);
  };

  const finalClassName = `${className} ${isActive ? activeClassName : ''}`.trim();

  return (
    <a href={to} onClick={handleClick} className={finalClassName} {...props}>
      {children}
    </a>
  );
};

/**
 * Lazy loading component wrapper
 */
export interface LazyProps {
  children: React.ComponentType<any>;
  fallback?: ReactNode;
}

export const Lazy: React.FC<LazyProps> = ({ children: Component, fallback = <div>Loading...</div> }) => (
  <Suspense fallback={fallback}>
    <Component />
  </Suspense>
);

/**
 * Route component for declarative routing
 */
export interface RouteProps {
  path: string;
  component?: React.ComponentType<any>;
  render?: (props: any) => ReactNode;
  children?: ReactNode | ((props: any) => ReactNode);
}

export const Route: React.FC<RouteProps> = ({ path, component: Component, render, children }) => {
  const { currentRoute } = useRouter();

  const match = currentRoute === path || currentRoute.startsWith(path + '/');
  if (!match) return null;

  if (Component) {
    return <Component />;
  }

  if (render) {
    return <>{render({})}</>;
  }

  if (typeof children === 'function') {
    return <>{children({})}</>;
  }

  return <>{children}</>;
};

/**
 * Navigate component - programmatic navigation
 */
export interface NavigateProps {
  to: string;
  replace?: boolean;
}

export const Navigate: React.FC<NavigateProps> = ({ to, replace = false }) => {
  const { navigate } = useRouter();

  React.useEffect(() => {
    if (replace) {
      window.history.replaceState({ route: to }, '', to);
    } else {
      navigate(to);
    }
  }, [to, navigate, replace]);

  return null;
};

/**
 * Outlet component for rendering child routes
 */
export const Outlet: React.FC = () => {
  const { currentRoute } = useRouter();
  return <div className="router-outlet" data-route={currentRoute} />;
};

/**
 * useParams hook for accessing route parameters
 */
export function useParams(): Record<string, string> {
  const { routeParams } = useRouter();
  return routeParams;
}

/**
 * useNavigate hook for programmatic navigation
 */
export function useNavigate() {
  const { navigate } = useRouter();
  return navigate;
}

/**
 * useLocation hook for accessing current location
 */
export function useLocation() {
  const { currentRoute } = useRouter();
  return {
    pathname: currentRoute,
    search: window.location.search,
    hash: window.location.hash,
  };
}
