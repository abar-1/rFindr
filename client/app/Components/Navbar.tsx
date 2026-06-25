"use client";

import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../contexts/AuthContext";

// Sliding-text nav link: the label rides up on hover to reveal a brighter copy.
const AnimatedNavLink = ({
  href,
  children,
  onClick,
}: {
  href: string;
  children: React.ReactNode;
  onClick?: React.MouseEventHandler<HTMLAnchorElement>;
}) => (
  <a
    href={href}
    onClick={onClick}
    className="group relative inline-block overflow-hidden h-5 flex items-center text-sm cursor-pointer"
  >
    <div className="flex flex-col transition-transform duration-400 ease-out transform group-hover:-translate-y-1/2">
      <span className="text-gray-600">{children}</span>
      <span className="text-indigo-600">{children}</span>
    </div>
  </a>
);

interface NavbarProps {
  onOpenHistory?: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onOpenHistory }) => {
  const { user, loading, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [headerShapeClass, setHeaderShapeClass] = useState("rounded-full");
  const shapeTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const toggleMenu = () => setIsOpen((o) => !o);
  const closeMenu = () => setIsOpen(false);

  // Square the pill off the moment the mobile menu opens; restore the rounded
  // shape only after the collapse animation has finished.
  useEffect(() => {
    if (shapeTimeoutRef.current) {
      clearTimeout(shapeTimeoutRef.current);
    }

    if (isOpen) {
      setHeaderShapeClass("rounded-xl");
    } else {
      shapeTimeoutRef.current = setTimeout(() => {
        setHeaderShapeClass("rounded-full");
      }, 300);
    }

    return () => {
      if (shapeTimeoutRef.current) {
        clearTimeout(shapeTimeoutRef.current);
      }
    };
  }, [isOpen]);

  const handleHistory: React.MouseEventHandler<HTMLAnchorElement> = (e) => {
    e.preventDefault();
    onOpenHistory?.();
    closeMenu();
  };

  const logoElement = (
    <div className="flex items-center gap-2">
      <div className="relative w-5 h-5 flex items-center justify-center">
        <span className="absolute w-1.5 h-1.5 rounded-full bg-indigo-500 top-0 left-1/2 transform -translate-x-1/2"></span>
        <span className="absolute w-1.5 h-1.5 rounded-full bg-indigo-500 left-0 top-1/2 transform -translate-y-1/2"></span>
        <span className="absolute w-1.5 h-1.5 rounded-full bg-indigo-500 right-0 top-1/2 transform -translate-y-1/2"></span>
        <span className="absolute w-1.5 h-1.5 rounded-full bg-indigo-500 bottom-0 left-1/2 transform -translate-x-1/2"></span>
      </div>
      <span className="text-sm font-bold text-indigo-700 select-none">ResearchMatch</span>
    </div>
  );

  // Prominent indigo pill button with a soft glow — used for the auth CTA.
  const PrimaryButton = ({
    children,
    onClick,
  }: {
    children: React.ReactNode;
    onClick?: () => void;
  }) => (
    <div className="relative group w-full sm:w-auto">
      <div className="absolute inset-0 -m-2 rounded-full hidden sm:block bg-indigo-400 opacity-30 filter blur-lg pointer-events-none transition-all duration-300 ease-out group-hover:opacity-50 group-hover:blur-xl group-hover:-m-3"></div>
      <button
        type="button"
        onClick={onClick}
        className="relative z-10 px-4 py-2 sm:px-3 text-xs sm:text-sm font-semibold text-white bg-indigo-600 rounded-full hover:bg-indigo-700 transition-all duration-200 w-full sm:w-auto shadow-sm"
      >
        {children}
      </button>
    </div>
  );

  const navLinksData = [
    { label: "Home", href: "#" },
    { label: "About", href: "#" },
  ];

  return (
    <header
      className={`fixed top-6 left-1/2 transform -translate-x-1/2 z-20
                  flex flex-col items-center
                  pl-6 pr-6 py-3 backdrop-blur-md
                  ${headerShapeClass}
                  border border-gray-200 bg-white/80 shadow-md
                  w-[calc(100%-2rem)] sm:w-auto
                  transition-[border-radius] duration-0 ease-in-out`}
    >
      <div className="flex items-center justify-between w-full gap-x-6 sm:gap-x-8">
        <div className="flex items-center">{logoElement}</div>

        <nav className="hidden sm:flex items-center space-x-4 sm:space-x-6 text-sm">
          {navLinksData.map((link) => (
            <AnimatedNavLink key={link.label} href={link.href}>
              {link.label}
            </AnimatedNavLink>
          ))}
          {!loading && user && (
            <AnimatedNavLink href="#" onClick={handleHistory}>
              History
            </AnimatedNavLink>
          )}
        </nav>

        <div className="hidden sm:flex items-center gap-2 sm:gap-3">
          {loading ? null : user ? (
            <>
              <span className="text-xs sm:text-sm text-gray-600">
                Hi, {user.name ?? user.email}
              </span>
              <PrimaryButton onClick={() => { logout(); closeMenu(); }}>
                Log out
              </PrimaryButton>
            </>
          ) : (
            <PrimaryButton onClick={closeMenu}>Get Started</PrimaryButton>
          )}
        </div>

        <button
          className="sm:hidden flex items-center justify-center w-8 h-8 text-gray-600 focus:outline-none"
          onClick={toggleMenu}
          aria-label={isOpen ? "Close Menu" : "Open Menu"}
        >
          {isOpen ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          ) : (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          )}
        </button>
      </div>

      <div
        className={`sm:hidden flex flex-col items-center w-full transition-all ease-in-out duration-300 overflow-hidden
                    ${isOpen ? "max-h-[1000px] opacity-100 pt-4" : "max-h-0 opacity-0 pt-0 pointer-events-none"}`}
      >
        <nav className="flex flex-col items-center space-y-4 text-base w-full">
          {navLinksData.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={closeMenu}
              className="text-gray-600 hover:text-indigo-600 transition-colors w-full text-center"
            >
              {link.label}
            </a>
          ))}
          {!loading && user && (
            <a
              href="#"
              onClick={handleHistory}
              className="text-gray-600 hover:text-indigo-600 transition-colors w-full text-center"
            >
              History
            </a>
          )}
        </nav>
        <div className="flex flex-col items-center space-y-4 mt-4 w-full">
          {loading ? null : user ? (
            <>
              <span className="text-sm text-gray-600 w-full text-center">
                Hi, {user.name ?? user.email}
              </span>
              <PrimaryButton onClick={() => { logout(); closeMenu(); }}>
                Log out
              </PrimaryButton>
            </>
          ) : (
            <PrimaryButton onClick={closeMenu}>Get Started</PrimaryButton>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;
