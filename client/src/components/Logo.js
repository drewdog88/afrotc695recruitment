import React from 'react';

const Logo = ({ className = "h-8 w-auto", showText = true, size = "medium" }) => {
  const sizeClasses = {
    small: "h-6 w-auto",
    medium: "h-8 w-auto", 
    large: "h-12 w-auto",
    xlarge: "h-16 w-auto"
  };

  const textSizes = {
    small: "text-sm",
    medium: "text-base",
    large: "text-lg",
    xlarge: "text-xl"
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <img
        src="https://www.up.edu/afrotc/images/det-695-full-color-patch.png"
        alt="AFROTC Detachment 695 Logo"
        className={`${sizeClasses[size]} object-contain`}
        onError={(e) => {
          // Fallback to a shield icon if image fails to load
          e.target.style.display = 'none';
          e.target.nextSibling.style.display = 'block';
        }}
      />
      <svg
        className={`${sizeClasses[size]} hidden text-primary-600`}
        fill="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
      </svg>
      {showText && (
        <div className={`font-bold ${textSizes[size]} text-gray-900`}>
          <div>AFROTC</div>
          <div className="text-primary-600">Detachment 695</div>
        </div>
      )}
    </div>
  );
};

export default Logo; 