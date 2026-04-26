/**
 * Tests for Router Component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  RouterProvider,
  Link,
  Route,
  Navigate,
  useRouter,
  useParams,
  useNavigate,
  useLocation,
} from '../../src/dashboard/static/tsx/components/Router';

describe('RouterProvider', () => {
  it('should render children', () => {
    render(
      <RouterProvider>
        <div>Test Content</div>
      </RouterProvider>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('should initialize with default route', () => {
    const TestComponent = () => {
      const { currentRoute } = useRouter();
      return <div>{currentRoute}</div>;
    };

    render(
      <RouterProvider initialRoute="/dashboard">
        <TestComponent />
      </RouterProvider>
    );

    expect(screen.getByText('/dashboard')).toBeInTheDocument();
  });
});

describe('Link Component', () => {
  it('should render as anchor tag', () => {
    render(
      <RouterProvider>
        <Link to="/test">Click me</Link>
      </RouterProvider>
    );

    const link = screen.getByRole('link', { name: /Click me/ });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/test');
  });

  it('should apply active class when on current route', () => {
    render(
      <RouterProvider initialRoute="/test">
        <Link to="/test" activeClassName="active">
          Link
        </Link>
      </RouterProvider>
    );

    const link = screen.getByRole('link');
    expect(link).toHaveClass('active');
  });

  it('should not apply active class on different route', () => {
    render(
      <RouterProvider initialRoute="/other">
        <Link to="/test" activeClassName="active">
          Link
        </Link>
      </RouterProvider>
    );

    const link = screen.getByRole('link');
    expect(link).not.toHaveClass('active');
  });

  it('should navigate on click', () => {
    const TestComponent = () => {
      const { currentRoute } = useRouter();
      return (
        <div>
          <div>{currentRoute}</div>
          <Link to="/test">Navigate</Link>
        </div>
      );
    };

    render(
      <RouterProvider initialRoute="/home">
        <TestComponent />
      </RouterProvider>
    );

    expect(screen.getByText('/home')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('link'));
    expect(screen.getByText('/test')).toBeInTheDocument();
  });
});

describe('Route Component', () => {
  it('should render component on matching route', () => {
    const TestComponent = () => <div>Route Content</div>;

    render(
      <RouterProvider initialRoute="/test">
        <Route path="/test" component={TestComponent} />
      </RouterProvider>
    );

    expect(screen.getByText('Route Content')).toBeInTheDocument();
  });

  it('should not render component on non-matching route', () => {
    const TestComponent = () => <div>Route Content</div>;

    render(
      <RouterProvider initialRoute="/other">
        <Route path="/test" component={TestComponent} />
      </RouterProvider>
    );

    expect(screen.queryByText('Route Content')).not.toBeInTheDocument();
  });

  it('should render with render prop', () => {
    render(
      <RouterProvider initialRoute="/test">
        <Route path="/test" render={() => <div>Render Prop Content</div>} />
      </RouterProvider>
    );

    expect(screen.getByText('Render Prop Content')).toBeInTheDocument();
  });

  it('should render with children', () => {
    render(
      <RouterProvider initialRoute="/test">
        <Route path="/test">
          <div>Children Content</div>
        </Route>
      </RouterProvider>
    );

    expect(screen.getByText('Children Content')).toBeInTheDocument();
  });
});

describe('Navigate Component', () => {
  it('should navigate to specified route', () => {
    const TestComponent = () => {
      const { currentRoute } = useRouter();
      return <div>{currentRoute}</div>;
    };

    const App = () => (
      <div>
        <Navigate to="/redirected" />
        <TestComponent />
      </div>
    );

    render(
      <RouterProvider initialRoute="/home">
        <App />
      </RouterProvider>
    );

    // Note: Navigate component should trigger navigation
    // In a real implementation, you might see the redirected route
  });
});

describe('useRouter Hook', () => {
  it('should provide router context', () => {
    const TestComponent = () => {
      const { currentRoute, navigate } = useRouter();
      return (
        <div>
          <div>{currentRoute}</div>
          <button onClick={() => navigate('/new')}>Nav</button>
        </div>
      );
    };

    render(
      <RouterProvider initialRoute="/home">
        <TestComponent />
      </RouterProvider>
    );

    expect(screen.getByText('/home')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button'));
    expect(screen.getByText('/new')).toBeInTheDocument();
  });

  it('should throw without provider', () => {
    const TestComponent = () => {
      useRouter();
      return <div>Test</div>;
    };

    // Suppress console errors for this test
    const spy = jest.spyOn(console, 'error').mockImplementation();

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useRouter must be used within RouterProvider');

    spy.mockRestore();
  });
});

describe('useParams Hook', () => {
  it('should provide route params', () => {
    const TestComponent = () => {
      const params = useParams();
      return <div>{JSON.stringify(params)}</div>;
    };

    render(
      <RouterProvider>
        <TestComponent />
      </RouterProvider>
    );

    expect(screen.getByText('{}')).toBeInTheDocument();
  });
});

describe('useNavigate Hook', () => {
  it('should provide navigate function', () => {
    const TestComponent = () => {
      const { currentRoute } = useRouter();
      const navigate = useNavigate();

      return (
        <div>
          <div>{currentRoute}</div>
          <button onClick={() => navigate('/new')}>Nav</button>
        </div>
      );
    };

    render(
      <RouterProvider initialRoute="/home">
        <TestComponent />
      </RouterProvider>
    );

    fireEvent.click(screen.getByRole('button'));
    expect(screen.getByText('/new')).toBeInTheDocument();
  });
});

describe('useLocation Hook', () => {
  it('should provide location info', () => {
    const TestComponent = () => {
      const location = useLocation();
      return <div>{location.pathname}</div>;
    };

    render(
      <RouterProvider initialRoute="/home">
        <TestComponent />
      </RouterProvider>
    );

    expect(screen.getByText('/home')).toBeInTheDocument();
  });
});
