import React, { Component } from 'react';
import { Button } from './ui';

/**
 * Error Boundary component for catching React errors
 * 
 * Usage:
 *   <ErrorBoundary>
 *     <YourComponent />
 *   </ErrorBoundary>
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null,
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    
    // Log error to console (in production, send to error tracking service)
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
    
    // Optional: Send to error tracking service
    // if (typeof window !== 'undefined' && window.Sentry) {
    //   window.Sentry.captureException(error);
    // }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full text-center">
            {/* Error Icon */}
            <div className="w-20 h-20 mx-auto mb-6 bg-red-100 rounded-full flex items-center justify-center">
              <span className="text-4xl">😵</span>
            </div>
            
            {/* Error Message */}
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Нещо се обърка
            </h1>
            <p className="text-gray-600 mb-6">
              Възникна неочаквана грешка. Моля, опитайте отново или презаредете страницата.
            </p>
            
            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button 
                variant="primary"
                onClick={this.handleReload}
              >
                🔄 Презареди страницата
              </Button>
              <Button 
                variant="outline"
                onClick={this.handleReset}
              >
                ↩️ Опитай отново
              </Button>
            </div>
            
            {/* Error Details (Development Only) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-8 text-left">
                <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
                  Детайли за грешката (развойна среда)
                </summary>
                <div className="mt-2 p-4 bg-gray-900 text-red-400 rounded-lg overflow-auto text-xs font-mono">
                  <p className="font-bold mb-2">{this.state.error.toString()}</p>
                  <pre className="whitespace-pre-wrap">
                    {this.state.errorInfo?.componentStack}
                  </pre>
                </div>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * HOC for wrapping components with ErrorBoundary
 */
export function withErrorBoundary(WrappedComponent, fallback = null) {
  return function WithErrorBoundary(props) {
    return (
      <ErrorBoundary fallback={fallback}>
        <WrappedComponent {...props} />
      </ErrorBoundary>
    );
  };
}

export default ErrorBoundary;

