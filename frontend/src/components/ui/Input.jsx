import React, { forwardRef } from 'react';
import { cn } from '../../lib/utils';

/**
 * Reusable Input component with label and error state
 */
export const Input = forwardRef(function Input(
  {
    label,
    error,
    helperText,
    leftIcon,
    rightIcon,
    className,
    containerClassName,
    required,
    ...props
  },
  ref
) {
  const inputId = props.id || props.name;
  
  return (
    <div className={cn('space-y-1', containerClassName)}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700"
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
            {leftIcon}
          </div>
        )}
        
        <input
          ref={ref}
          id={inputId}
          className={cn(
            // Base styles
            'w-full rounded-lg border bg-white px-4 py-2.5',
            'text-gray-900 placeholder-gray-400',
            'transition-colors duration-200',
            // Focus state
            'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            // Error state
            error
              ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
              : 'border-gray-300 hover:border-gray-400',
            // Icon padding
            leftIcon && 'pl-10',
            rightIcon && 'pr-10',
            // Disabled state
            props.disabled && 'bg-gray-50 text-gray-500 cursor-not-allowed',
            className
          )}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-400">
            {rightIcon}
          </div>
        )}
      </div>
      
      {(error || helperText) && (
        <p className={cn(
          'text-sm',
          error ? 'text-red-600' : 'text-gray-500'
        )}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

/**
 * Textarea variant
 */
export const Textarea = forwardRef(function Textarea(
  { label, error, helperText, className, containerClassName, required, ...props },
  ref
) {
  const textareaId = props.id || props.name;
  
  return (
    <div className={cn('space-y-1', containerClassName)}>
      {label && (
        <label
          htmlFor={textareaId}
          className="block text-sm font-medium text-gray-700"
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <textarea
        ref={ref}
        id={textareaId}
        className={cn(
          'w-full rounded-lg border bg-white px-4 py-2.5',
          'text-gray-900 placeholder-gray-400',
          'transition-colors duration-200 resize-y min-h-[100px]',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
          error
            ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
            : 'border-gray-300 hover:border-gray-400',
          props.disabled && 'bg-gray-50 text-gray-500 cursor-not-allowed',
          className
        )}
        {...props}
      />
      
      {(error || helperText) && (
        <p className={cn('text-sm', error ? 'text-red-600' : 'text-gray-500')}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

export default Input;

