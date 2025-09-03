import { Link } from "react-router";

function Footer() {
  const footerLinks = [
    { name: "Product", href: "/" },
    { name: "Solutions", href: "/" },
    { name: "Resources", href: "/" },
    { name: "Pricing", href: "/" },
  ];
  return (
    // <footer className="w-full bg-primary shadow px-20 py-3 flex flex-col items-center justify-center">
    //   <div className="w-full flex items-center justify-between gap-4 mb-2">
    //     {footerLinks.map((link) => (
    //       <Link key={link.href} to={link.href} className="text-xl font-regular">
    //         {link.name}
    //       </Link>
    //     ))}
    //   </div>
    //   <span className="text-center">Copyright 2025 Freshtify</span>
    // </footer>
    <footer className="w-full bg-primary shadow px-6 sm:px-12 lg:px-20 py-6 flex flex-col gap-3 items-center justify-center">
      <div className="flex w-full flex-wrap justify-center gap-20 sm:justify-between">
        {footerLinks.map((link) => (
          <Link
            key={link.href}
            to={link.href}
            className="sm:text-lg hover:text-accent transition-colors"
          >
            {link.name}
          </Link>
        ))}
      </div>
      <span className="text-center text-sm text-slate-400">
        &copy; 2025 La Trobe University. All rights reserved.
      </span>
    </footer>
  );
}

export default Footer;
