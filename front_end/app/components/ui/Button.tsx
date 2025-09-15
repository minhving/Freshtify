import React from "react";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  variant?: "primary" | "secondary";
  size?: "small" | "medium" | "large";
}

function Button({
  children,
  onClick,
  className = "",
  disabled = false,
  variant = "primary",
  size = "medium",
}: ButtonProps) {
  const sizeClasses = {
    small: "px-3 py-1.5 text-sm",
    medium: "px-4 py-2 text-base",
    large: "px-6 py-3 text-lg",
  };

  const variantClasses = {
    primary: "bg-primary hover:bg-secondary text-secondary hover:text-primary",
    secondary:
      "bg-secondary hover:bg-primary text-primary hover:text-secondary",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${sizeClasses[size]} ${variantClasses[variant]} rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${className}`}
    >
      {children}
    </button>
  );
}

export default Button;
