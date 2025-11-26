import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Spinner sizes
 */
const sizes = {
  xs: 'w-3 h-3',
  sm: 'w-4 h-4',
  md: 'w-8 h-8',
  lg: 'w-12 h-12',
  xl: 'w-16 h-16',
};

/**
 * Loading Spinner component
 * 
 * @param {Object} props
 * @param {'xs'|'sm'|'md'|'lg'|'xl'} props.size - Spinner size
 * @param {string} props.className - Additional classes
 */
export function Spinner({ size = 'md', className }) {
  return (
    <div
      className={cn(
        'animate-spin rounded-full',
        'border-2 border-primary-200 border-t-primary-600',
        sizes[size],
        className
      )}
      role="status"
      aria-label="Зареждане"
    >
      <span className="sr-only">Зареждане...</span>
    </div>
  );
}

/**
 * Full page loader
 */
export function PageLoader({ message = 'Зареждане...' }) {
  return (
    <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="text-center">
        <Spinner size="xl" />
        <p className="mt-4 text-gray-600 font-medium">{message}</p>
      </div>
    </div>
  );
}

/**
 * Section loader (for cards/sections)
 */
export function SectionLoader({ message }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Spinner size="lg" />
      {message && (
        <p className="mt-4 text-gray-500 text-sm">{message}</p>
      )}
    </div>
  );
}

/**
 * Inline loader (for buttons, etc.)
 */
export function InlineLoader({ className }) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Spinner size="sm" />
      <span className="text-sm text-gray-600">Зареждане...</span>
    </div>
  );
}

export default Spinner;

