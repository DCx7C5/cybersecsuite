/**
 * Menu Input Tracking Hooks
 * Keyboard and mouse input handlers for menu interactions
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface MenuInputState {
  isKeyboardActive: boolean;
  isMouseActive: boolean;
  lastInputType: 'keyboard' | 'mouse' | null;
  selectedIndex: number;
}

/**
 * Hook for tracking keyboard input in menus
 * Handles arrow keys, Enter, Escape navigation
 */
export function useKeyboardMenuInput(
  itemCount: number,
  onSelect: (index: number) => void,
  onClose: () => void
) {
  const [selectedIndex, setSelectedIndex] = useState<number>(0);
  const [isActive, setIsActive] = useState<boolean>(true);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!isActive) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => (prev + 1) % itemCount);
          break;
        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => (prev - 1 + itemCount) % itemCount);
          break;
        case 'Enter':
          e.preventDefault();
          onSelect(selectedIndex);
          break;
        case 'Escape':
          e.preventDefault();
          onClose();
          setIsActive(false);
          break;
        case 'Home':
          e.preventDefault();
          setSelectedIndex(0);
          break;
        case 'End':
          e.preventDefault();
          setSelectedIndex(itemCount - 1);
          break;
      }
    },
    [itemCount, onSelect, onClose, selectedIndex, isActive]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return {
    selectedIndex,
    setSelectedIndex,
    isActive,
    setIsActive,
    handleKeyDown,
  };
}

/**
 * Hook for tracking mouse input in menus
 * Handles hover and click interactions
 */
export function useMouseMenuInput(
  onSelect: (index: number) => void,
  onHover: (index: number) => void
) {
  const [isMouseActive, setIsMouseActive] = useState<boolean>(false);

  const handleMouseEnter = useCallback(
    (index: number) => {
      setIsMouseActive(true);
      onHover(index);
    },
    [onHover]
  );

  const handleMouseLeave = useCallback(() => {
    setIsMouseActive(false);
  }, []);

  const handleMouseClick = useCallback(
    (index: number) => {
      setIsMouseActive(false);
      onSelect(index);
    },
    [onSelect]
  );

  return {
    isMouseActive,
    setIsMouseActive,
    handleMouseEnter,
    handleMouseLeave,
    handleMouseClick,
  };
}

/**
 * Combined hook for full menu input tracking
 */
export function useMenuInput(
  itemCount: number,
  onSelect: (index: number) => void,
  onClose: () => void
) {
  const keyboard = useKeyboardMenuInput(itemCount, onSelect, onClose);
  const mouse = useMouseMenuInput(onSelect, (index) => {
    keyboard.setSelectedIndex(index);
  });

  const state: MenuInputState = {
    isKeyboardActive: keyboard.isActive,
    isMouseActive: mouse.isMouseActive,
    lastInputType: keyboard.isActive ? 'keyboard' : 'mouse',
    selectedIndex: keyboard.selectedIndex,
  };

  return {
    ...keyboard,
    ...mouse,
    state,
  };
}
