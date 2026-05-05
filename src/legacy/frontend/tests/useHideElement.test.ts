/**
 * Tests for useHideElement Hook
 */

import { renderHook, act } from '@testing-library/react';
import { useHideElement } from '../../src/dashboard/static/tsx/hooks/useHideElement';

describe('useHideElement Hook', () => {
  let element: HTMLDivElement;

  beforeEach(() => {
    element = document.createElement('div');
    element.textContent = 'Test Element';
    document.body.appendChild(element);
  });

  afterEach(() => {
    document.body.removeChild(element);
  });

  it('should initialize with hidden state', () => {
    const { result } = renderHook(() => useHideElement(true));
    expect(result.current.isHidden()).toBe(true);
  });

  it('should initialize with visible state', () => {
    const { result } = renderHook(() => useHideElement(false));
    expect(result.current.isHidden()).toBe(false);
  });

  it('should hide element', async () => {
    const { result } = renderHook(() => useHideElement(false, { animationDuration: 0 }));

    act(() => {
      result.current.elementRef.current = element;
      result.current.hide();
    });

    expect(element.style.display).toBe('none');
    expect(result.current.isHidden()).toBe(true);
  });

  it('should show element', async () => {
    const { result } = renderHook(() => useHideElement(true, { animationDuration: 0 }));

    act(() => {
      result.current.elementRef.current = element;
      result.current.show();
    });

    expect(element.style.display).not.toBe('none');
  });

  it('should toggle visibility', () => {
    const { result } = renderHook(() => useHideElement(false, { animationDuration: 0 }));

    act(() => {
      result.current.elementRef.current = element;
      result.current.toggle();
    });

    expect(result.current.isHidden()).toBe(true);

    act(() => {
      result.current.toggle();
    });

    expect(result.current.isHidden()).toBe(false);
  });

  it('should apply custom class on hide', async () => {
    const { result } = renderHook(() =>
      useHideElement(false, { animationDuration: 0, className: 'custom-hidden' })
    );

    act(() => {
      result.current.elementRef.current = element;
      result.current.hide();
    });

    expect(element.classList.contains('custom-hidden')).toBe(true);
  });

  it('should call onHide callback', async () => {
    const onHide = jest.fn();
    const { result } = renderHook(() => useHideElement(false, { animationDuration: 0, onHide }));

    act(() => {
      result.current.elementRef.current = element;
      result.current.hide();
    });

    expect(onHide).toHaveBeenCalled();
  });

  it('should call onShow callback', async () => {
    const onShow = jest.fn();
    const { result } = renderHook(() => useHideElement(true, { animationDuration: 0, onShow }));

    act(() => {
      result.current.elementRef.current = element;
      result.current.show();
    });

    expect(onShow).toHaveBeenCalled();
  });
});
