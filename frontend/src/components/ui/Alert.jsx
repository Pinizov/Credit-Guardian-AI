import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Alert variants with icons
 */
const variants = {
  info: {
    container: 'bg-blue-50 border-blue-200 text-blue-800',
    icon: 'ℹ️',
  },
  success: {
    container: 'bg-green-50 border-green-200 text-green-800',
    icon: '✅',
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    icon: '⚠️',
  },
  danger: {
    container: 'bg-red-50 border-red-200 text-red-800',
    icon: '❌',
  },
};

/**
 * Alert component for notifications and messages
 * 
 * @param {Object} props
 * @param {'info'|'success'|'warning'|'danger'} props.variant
 * @param {string} props.title
 * @param {boolean} props.dismissible
 * @param {Function} props.onDismiss
 */
export function Alert({
  variant = 'info',
  title,
  children,
  dismissible = false,
  onDismiss,
  className,
  ...props
}) {
  const config = variants[variant];
  
  return (
    <div
      className={cn(
        'relative rounded-lg border p-4',
        'animate-fade-in',
        config.container,
        className
      )}
      role="alert"
      {...props}
    >
      <div className="flex gap-3">
        <span className="flex-shrink-0 text-lg">{config.icon}</span>
        <div className="flex-1">
          {title && (
            <h4 className="font-semibold mb-1">{title}</h4>
          )}
          <div className="text-sm">{children}</div>
        </div>
        {dismissible && onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 text-current opacity-60 hover:opacity-100 transition-opacity"
            aria-label="Затвори"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Alert with action buttons
 */
export function AlertWithActions({
  variant = 'info',
  title,
  children,
  actions,
  className,
  ...props
}) {
  const config = variants[variant];
  
  return (
    <div
      className={cn(
        'rounded-lg border p-4',
        config.container,
        className
      )}
      role="alert"
      {...props}
    >
      <div className="flex gap-3">
        <span className="flex-shrink-0 text-lg">{config.icon}</span>
        <div className="flex-1">
          {title && <h4 className="font-semibold mb-1">{title}</h4>}
          <div className="text-sm">{children}</div>
          {actions && (
            <div className="mt-3 flex gap-2">
              {actions}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Alert;

