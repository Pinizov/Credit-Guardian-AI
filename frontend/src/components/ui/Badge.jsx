import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Badge variants
 */
const variants = {
  default: 'bg-gray-100 text-gray-800',
  primary: 'bg-primary-100 text-primary-800',
  secondary: 'bg-purple-100 text-purple-800',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  danger: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
};

const sizes = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

/**
 * Badge component for labels and status indicators
 * 
 * @param {Object} props
 * @param {'default'|'primary'|'secondary'|'success'|'warning'|'danger'|'info'} props.variant
 * @param {'sm'|'md'|'lg'} props.size
 * @param {boolean} props.dot - Show status dot
 */
export function Badge({
  variant = 'default',
  size = 'md',
  dot = false,
  children,
  className,
  ...props
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-medium rounded-full',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full',
            variant === 'success' && 'bg-green-500',
            variant === 'warning' && 'bg-yellow-500',
            variant === 'danger' && 'bg-red-500',
            variant === 'info' && 'bg-blue-500',
            variant === 'primary' && 'bg-primary-500',
            (variant === 'default' || variant === 'secondary') && 'bg-gray-500'
          )}
        />
      )}
      {children}
    </span>
  );
}

/**
 * Risk Badge - specialized for risk levels
 */
export function RiskBadge({ level, className }) {
  const levels = {
    low: { variant: 'success', label: 'Нисък' },
    medium: { variant: 'warning', label: 'Среден' },
    high: { variant: 'danger', label: 'Висок' },
    critical: { variant: 'danger', label: 'Критичен' },
  };
  
  const config = levels[level?.toLowerCase()] || levels.medium;
  
  return (
    <Badge variant={config.variant} dot className={className}>
      {config.label}
    </Badge>
  );
}

/**
 * Status Badge - for status indicators
 */
export function StatusBadge({ status, className }) {
  const statuses = {
    active: { variant: 'success', label: 'Активен' },
    inactive: { variant: 'default', label: 'Неактивен' },
    pending: { variant: 'warning', label: 'Изчакващ' },
    completed: { variant: 'success', label: 'Завършен' },
    failed: { variant: 'danger', label: 'Неуспешен' },
    processing: { variant: 'info', label: 'Обработва се' },
  };
  
  const config = statuses[status?.toLowerCase()] || { variant: 'default', label: status };
  
  return (
    <Badge variant={config.variant} dot className={className}>
      {config.label}
    </Badge>
  );
}

export default Badge;

