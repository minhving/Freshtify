import React from "react";
import teamLogo from "../assets/teamlogo.png";
import { Link } from "react-router";

const navigation = [
  { name: "Home", href: "/" },
  { name: "Upload", href: "/upload" },
  { name: "Dashboard", href: "/dashboard" },
  { name: "Alert", href: "/alert" },
];

export default function Header() {
  return (
    <header className="w-full bg-primary shadow px-6 py-3 flex items-center justify-between gap-4 ">
      {/* Logo */}
      <div className="flex justify-center items-center p-2 bg-secondary rounded-lg text-primary font-semibold text-3xl gap-2 ">
        <img src={teamLogo} width={40} alt="logo block" />
        <span className="hidden md:block">Freshtify</span>
      </div>

      {/* Navigation */}
      <nav className="flex justify-between gap-2 sm:gap-8">
        {navigation.map((item) => (
          <Link key={item.href} to={item.href} className="text-xl font-regular">
            {item.name}
          </Link>
        ))}
      </nav>
    </header>
  );
}
