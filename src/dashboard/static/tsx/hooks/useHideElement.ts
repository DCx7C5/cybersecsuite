/**
 * useHideElement Hook
 * DOM visibility management hook for React components
 * Handles element visibility with optional animations and callbacks
 */

import { useEffect, useRef, useCallback } from 'react';

interface HideElementOptions {
  animationDuration?: number;
  onHide?: () => void;
  onShow?: () => void;
  className?: string;
}

/**
 * Hook for managing element visibility in the DOM
 * @param initiallyHidden - Initial visibility state
 * @param options - Configuration options
 * @returns Object with visibility control methods
 */
export function useHideElement(
  initiallyHidden: boolean = false,
  options: HideElementOptions = {}
) {
  const elementRef = useRef<HTMLElement | null>(null);
  const isHiddenRef = useRef<boolean>(initiallyHidden);

  const {
    animationDuration = 300,
    onHide = () => {},
    onShow = () => {},
    className = 'hidden',
  } = options;

  const hide = useCallback(() => {
    if (!elementRef.current || isHiddenRef.current) return;

    if (animationDuration > 0) {
      elementRef.current.style.opacity = '0';
      elementRef.current.style.transition = `opacity ${animationDuration}ms ease-out`;
      setTimeout(() => {
        if (elementRef.current) {
          elementRef.current.style.display = 'none';
          elementRef.current.classList.add(className);
          isHiddenRef.current = true;
          onHide();
        }
      }, animationDuration);
    } else {
      elementRef.current.style.display = 'none';
      elementRef.current.classList.add(className);
      isHiddenRef.current = true;
      onHide();
    }
  }, [animationDuration, className, onHide]);

  const show = useCallback(() => {
    if (!elementRef.current || !isHiddenRef.current) return;

    elementRef.current.style.display = '';
    elementRef.current.classList.remove(className);

    if (animationDuration > 0) {
      requestAnimationFrame(() => {
        if (elementRef.current) {
          elementRef.current.style.opacity = '1';
          elementRef.current.style.transition = `opacity ${animationDuration}ms ease-in`;
          setTimeout(() => {
            if (elementRef.current) {
              elementRef.current.style.transition = '';
              isHiddenRef.current = false;
              onShow();
            }
          }, animationDuration);
        }
      });
    } else {
      isHiddenRef.current = false;
      onShow();
    }
  }, [animationDuration, className, onShow]);

  const toggle = useCallback(() => {
    if (isHiddenRef.current) {
      show();
    } else {
      hide();
    }
  }, [show, hide]);

  const isHidden = useCallback(() => isHiddenRef.current, []);

  useEffect(() => {
    return () => {
      if (elementRef.current) {
        elementRef.current.style.transition = '';
      }
    };
  }, []);

  return {
    elementRef,
    hide,
    show,
    toggle,
    isHidden,
  };
}
