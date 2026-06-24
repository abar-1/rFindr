import React from "react";

const Navbar: React.FC = () => {
  return (
    // Updated container:
    // - backdrop-blur-md: Stronger blur effect
    // - bg-white/80: Slightly less transparent background
    // - shadow-md: Replaces the border with a cleaner shadow
    <nav className="backdrop-blur-md bg-white/80 shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto flex justify-between items-center px-6 py-4">
        
        {/* Logo/Brand:
          - text-2xl: Slightly larger text
          - font-bold: Bolder text
          - text-indigo-700: Uses the primary brand color
        */}
        <h1 className="text-2xl font-bold text-indigo-700 select-none cursor-pointer">
          ResearchMatch
        </h1>
        
        {/* Navigation Links:
          - space-x-8: Increased spacing for better clarity
          - text-gray-700: Darker link color for better contrast
        */}
        <div className="flex space-x-8 text-gray-700">
          <a 
            href="#" 
            className="font-medium hover:text-indigo-600 border-b-2 border-transparent hover:border-indigo-600 py-1 transition duration-300"
          >
            Home
          </a>
          <a 
            href="#" 
            className="font-medium hover:text-indigo-600 border-b-2 border-transparent hover:border-indigo-600 py-1 transition duration-300"
          >
            About
          </a>
          {/* Example of adding a prominent CTA button */}
          <a 
            href="#" 
            className="font-semibold text-white bg-indigo-600 px-4 py-1.5 rounded-lg hover:bg-indigo-700 transition duration-300 shadow-md"
          >
            Get Started
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;