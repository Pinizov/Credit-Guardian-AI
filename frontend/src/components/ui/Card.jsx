import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Card component with optional header and footer
 */
export function Card({ className, children, ...props }) {
  return (
    <div
      className={cn(
        'bg-white rounded-xl shadow-md',
        'border border-gray-100',
        'transition-shadow duration-200',
        'hover:shadow-lg',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * Card Header
 */
export function CardHeader({ className, children, ...props }) {
  return (
    <div
      className={cn(
        'px-6 py-4 border-b border-gray-100',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * Card Title
 */
export function CardTitle({ className, children, as: Component = 'h3', ...props }) {
  return (
    <Component
      className={cn(
        'text-xl font-bold text-gray-900',
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

/**
 * Card Description
 */
export function CardDescription({ className, children, ...props }) {
  return (
    <p
      className={cn(
        'text-sm text-gray-500 mt-1',
        className
      )}
      {...props}
    >
      {children}
    </p>
  );
}

/**
 * Card Content
 */
export function CardContent({ className, children, ...props }) {
  return (
    <div
      className={cn('px-6 py-4', className)}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * Card Footer
 */
export function CardFooter({ className, children, ...props }) {
  return (
    <div
      className={cn(
        'px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-xl',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * Stat Card - for dashboard statistics
 */
export function StatCard({ icon, label, value, trend, trendUp, className }) {
  return (
    <Card className={cn('p-6', className)}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500">{label}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && (
            <p className={cn(
              'text-sm mt-2 flex items-center gap-1',
              trendUp ? 'text-green-600' : 'text-red-600'
            )}>
              {trendUp ? '↑' : '↓'} {trend}
            </p>
          )}
        </div>
        {icon && (
          <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center text-primary-600 text-xl">
            {icon}
          </div>
        )}
      </div>
    </Card>
  );
}

export default Card;

