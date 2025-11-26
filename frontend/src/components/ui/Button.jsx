import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Button variants configuration
 */
const variants = {
  primary: 'bg-primary-500 hover:bg-primary-600 text-white shadow-md hover:shadow-lg',
  secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-800',
  outline: 'border-2 border-primary-500 text-primary-500 hover:bg-primary-50',
  ghost: 'hover:bg-gray-100 text-gray-700',
  danger: 'bg-red-500 hover:bg-red-600 text-white',
  success: 'bg-green-500 hover:bg-green-600 text-white',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
  xl: 'px-8 py-4 text-xl',
};

/**
 * Reusable Button component
 * 
 * @param {Object} props
 * @param {'primary'|'secondary'|'outline'|'ghost'|'danger'|'success'} props.variant
 * @param {'sm'|'md'|'lg'|'xl'} props.size
 * @param {boolean} props.loading
 * @param {boolean} props.disabled
 * @param {boolean} props.fullWidth
 * @param {React.ReactNode} props.leftIcon
 * @param {React.ReactNode} props.rightIcon
 * @param {string} props.className
 * @param {React.ReactNode} props.children
 */
export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  className,
  children,
  ...props
}) {
  const isDisabled = disabled || loading;
  
  return (
    <button
      className={cn(
        // Base styles
        'inline-flex items-center justify-center gap-2 font-semibold rounded-lg',
        'transition-all duration-200 ease-in-out',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
        'transform active:scale-[0.98]',
        // Variant
        variants[variant],
        // Size
        sizes[size],
        // States
        isDisabled && 'opacity-50 cursor-not-allowed pointer-events-none',
        fullWidth && 'w-full',
        className
      )}
      disabled={isDisabled}
      {...props}
    >
      {loading ? (
        <>
          <Spinner size="sm" />
          <span>Зареждане...</span>
        </>
      ) : (
        <>
          {leftIcon && <span className="flex-shrink-0">{leftIcon}</span>}
          {children}
          {rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
        </>
      )}
    </button>
  );
}

/**
 * Small spinner for loading state
 */
function Spinner({ size = 'sm' }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };
  
  return (
    <svg
      className={cn('animate-spin', sizeClasses[size])}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

export default Button;

