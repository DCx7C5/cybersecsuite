/**
 * Components Index
 * Central export point for all React components
 */

export { AuthProtectedRoutes, useAuth, useHasRole, canAccessRoute, withAuthProtection } from './AuthProtectedRoutes';
export type { ProtectedRouteProps } from './AuthProtectedRoutes';

export {
  RouterProvider,
  Link,
  Route,
  Navigate,
  Outlet,
  Lazy,
  useRouter,
  useParams,
  useNavigate,
  useLocation,
} from './Router';
export type { RouteConfig, RouterContextType, RouterProviderProps, LinkProps, RouteProps, NavigateProps } from './Router';
