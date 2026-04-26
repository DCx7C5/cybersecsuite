/**
 * Tests for useMenuInput Hook
 */

import { renderHook, act } from '@testing-library/react';
import { useKeyboardMenuInput, useMouseMenuInput, useMenuInput } from '../../src/dashboard/static/tsx/hooks/useMenuInput';

describe('useKeyboardMenuInput Hook', () => {
  it('should initialize with index 0', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useKeyboardMenuInput(3, onSelect, onClose));

    expect(result.current.selectedIndex).toBe(0);
    expect(result.current.isActive).toBe(true);
  });

  it('should move down through items', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useKeyboardMenuInput(3, onSelect, onClose));

    act(() => {
      result.current.handleKeyDown(new KeyboardEvent('keydown', { key: 'ArrowDown' }));
    });

    expect(result.current.selectedIndex).toBe(1);
  });

  it('should wrap around when at end', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useKeyboardMenuInput(3, onSelect, onClose));

    act(() => {
      result.current.setSelectedIndex(2);
      result.current.handleKeyDown(new KeyboardEvent('keydown', { key: 'ArrowDown' }));
    });

    expect(result.current.selectedIndex).toBe(0);
  });

  it('should move up through items', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useKeyboardMenuInput(3, onSelect, onClose));

    act(() => {
      result.current.setSelectedIndex(1);
      result.current.handleKeyDown(new KeyboardEvent('keydown', { key: 'ArrowUp' }));
    });

    expect(result.current.selectedIndex).toBe(0);
  });

  it('should select on Enter', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useKeyboardMenuInput(3, onSelect, onClose));

    act(() => {
      result.current.setSelectedIndex(1);
      result.current.handleKeyDown(new KeyboardEvent('keydown', { key: 'Enter' }));
    });

    expect(onSelect).toHaveBeenCalledWith(1);
  });

  it('should close on Escape', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useKeyboardMenuInput(3, onSelect, onClose));

    act(() => {
      result.current.handleKeyDown(new KeyboardEvent('keydown', { key: 'Escape' }));
    });

    expect(onClose).toHaveBeenCalled();
    expect(result.current.isActive).toBe(false);
  });

  it('should jump to Home', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useKeyboardMenuInput(3, onSelect, onClose));

    act(() => {
      result.current.setSelectedIndex(2);
      result.current.handleKeyDown(new KeyboardEvent('keydown', { key: 'Home' }));
    });

    expect(result.current.selectedIndex).toBe(0);
  });

  it('should jump to End', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useKeyboardMenuInput(3, onSelect, onClose));

    act(() => {
      result.current.handleKeyDown(new KeyboardEvent('keydown', { key: 'End' }));
    });

    expect(result.current.selectedIndex).toBe(2);
  });
});

describe('useMouseMenuInput Hook', () => {
  it('should select item on click', () => {
    const onSelect = jest.fn();
    const onHover = jest.fn();
    const { result } = renderHook(() => useMouseMenuInput(onSelect, onHover));

    act(() => {
      result.current.handleMouseClick(1);
    });

    expect(onSelect).toHaveBeenCalledWith(1);
    expect(result.current.isMouseActive).toBe(false);
  });

  it('should hover on mouse enter', () => {
    const onSelect = jest.fn();
    const onHover = jest.fn();
    const { result } = renderHook(() => useMouseMenuInput(onSelect, onHover));

    act(() => {
      result.current.handleMouseEnter(1);
    });

    expect(onHover).toHaveBeenCalledWith(1);
    expect(result.current.isMouseActive).toBe(true);
  });

  it('should deactivate on mouse leave', () => {
    const onSelect = jest.fn();
    const onHover = jest.fn();
    const { result } = renderHook(() => useMouseMenuInput(onSelect, onHover));

    act(() => {
      result.current.handleMouseEnter(1);
      result.current.handleMouseLeave();
    });

    expect(result.current.isMouseActive).toBe(false);
  });
});

describe('useMenuInput Combined Hook', () => {
  it('should combine keyboard and mouse inputs', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useMenuInput(3, onSelect, onClose));

    expect(result.current.state.isKeyboardActive).toBe(true);
    expect(result.current.state.selectedIndex).toBe(0);
  });

  it('should track last input type', () => {
    const onSelect = jest.fn();
    const onClose = jest.fn();
    const { result } = renderHook(() => useMenuInput(3, onSelect, onClose));

    expect(result.current.state.lastInputType).toMatch(/keyboard|mouse/);
  });
});
