import React from 'react';

// Defines the properties for the spinner. 
// Size and color can be adjusted externally if needed.
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  // Defaults to 'md' size and the indigo color we established.
  size = 'md', 
  color = 'border-indigo-600' 
}) => {
  // Determine size and border thickness classes
  const sizeClasses = {
    sm: 'w-6 h-6 border-2',
    md: 'w-8 h-8 border-3', 
    lg: 'w-12 h-12 border-4',
  }[size];

  // The actual spinner element. 
  // It uses the animate-spin class and border styling to create the effect.
  return (
    <div className="flex justify-center items-center p-4">
      <div 
        className={`
          animate-spin 
          rounded-full 
          ${sizeClasses} 
          ${color} 
          border-t-transparent
        `}
        role="status"
        aria-live="polite"
        aria-label="Loading"
      >
        {/* sr-only makes the text accessible to screen readers, but invisible on screen */}
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  );
};

export default LoadingSpinner;
