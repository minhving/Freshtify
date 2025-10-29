# Freshtify Frontend

A modern web application for AI-powered stock estimation and freshness analysis of produce items. Built with React Router v7, TypeScript, and TailwindCSS.

## 🚀 Features

- **Image Upload & Analysis**: Upload images for AI-powered stock estimation
- **Real-time Dashboard**: Visualize stock levels and freshness data
- **Alert System**: Monitor and manage stock alerts
- **Model Selection**: Choose between different AI models for analysis
- **Responsive Design**: Modern UI with TailwindCSS and shadcn/ui components
- **Server-side Rendering**: Fast initial page loads with React Router SSR
- **Hot Module Replacement**: Lightning-fast development experience

## 🛠 Tech Stack

- **Framework**: React Router v7
- **Language**: TypeScript
- **Styling**: TailwindCSS v4
- **UI Components**: Radix UI & shadcn/ui
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Build Tool**: Vite

## 📁 Folder Structure

```
front_end/
├── app/                          # Application source code
│   ├── routes/                   # Route components
│   │   ├── _layout.tsx          # Layout wrapper for nested routes
│   │   ├── index.tsx            # Home page
│   │   ├── upload.tsx           # Image upload page
│   │   ├── dashboard.tsx        # Dashboard with analytics
│   │   └── alert.tsx            # Alerts management page
│   │
│   ├── components/              # Reusable React components
│   │   ├── Header.tsx           # Navigation header
│   │   ├── Footer.tsx           # Footer component
│   │   ├── ModelSelector.tsx   # AI model selection component
│   │   ├── SectionToggle.tsx   # Section toggle component
│   │   ├── StatusPill.tsx       # Status indicator component
│   │   ├── TimeToggle.tsx       # Time filter toggle
│   │   └── ui/                  # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── dialog.tsx
│   │       ├── dropdown-menu.tsx
│   │       ├── input.tsx
│   │       ├── label.tsx
│   │       ├── navigation-menu.tsx
│   │       ├── select.tsx
│   │       └── table.tsx
│   │
│   ├── lib/                     # Utility libraries
│   │   ├── api.ts              # API client functions
│   │   └── utils.ts            # Helper utilities
│   │
│   ├── assets/                  # Static assets
│   │   ├── avatars/            # Team member avatars
│   │   ├── sampleImages/       # Sample images for demo
│   │   └── teamlogo.png        # Team logo
│   │
│   ├── welcome/                 # Welcome page assets
│   │   ├── welcome.tsx
│   │   ├── logo-dark.svg
│   │   └── logo-light.svg
│   │
│   ├── root.tsx                 # Root application component
│   ├── routes.ts                # Route configuration
│   └── app.css                  # Global styles
│
├── public/                      # Public static files
│   └── favicon.ico
│
├── build/                       # Production build output
│   ├── client/                 # Client-side assets
│   └── server/                 # Server-side code
│
├── components.json              # shadcn/ui configuration
├── Dockerfile                   # Docker configuration
├── env.example                  # Environment variables template
├── package.json                 # Dependencies and scripts
├── react-router.config.ts       # React Router configuration
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
└── README.md                    # This file
```

## 📦 Installation

### Prerequisites

- Node.js 18+
- npm or pnpm or yarn

### Install Dependencies

```bash
npm install
```

## 🔧 Configuration

1. Copy the environment variables template:

```bash
cp env.example .env
```

2. Update the `.env` file with your configuration:

```env
VITE_API_URL=http://localhost:8000
# Add other environment variables as needed
```

## 💻 Development

Start the development server with Hot Module Replacement:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server (on port 12355)
- `npm run typecheck` - Run TypeScript type checking

## 🏗 Building for Production

Create an optimized production build:

```bash
npm run build
```

This generates:

- `build/client/` - Static assets (HTML, CSS, JS)
- `build/server/` - Server-side code

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t freshtify-frontend .
```

### Run Container

```bash
docker run -p 3000:3000 freshtify-frontend
```

### Docker Compose

If you have a `docker-compose.yml` in the root directory:

```bash
docker-compose up frontend
```

## 🚀 Deployment Options

The application can be deployed to any platform that supports Node.js or Docker:

- **Cloud Platforms**: AWS ECS, Google Cloud Run, Azure Container Apps
- **PaaS**: Heroku, Railway, Fly.io, Render
- **Edge**: Cloudflare Pages, Vercel, Netlify
- **VPS**: Digital Ocean, Linode, Vultr

### Production Server

To run the production build locally:

```bash
npm run start
```

The server will start on port 12355 (configurable via PORT environment variable).

## 🎨 Styling

This project uses:

- **TailwindCSS v4** for utility-first styling
- **shadcn/ui** for pre-built accessible components
- **Radix UI** for unstyled, accessible component primitives
- **class-variance-authority** for component variants
- **clsx** & **tailwind-merge** for conditional class composition

### Adding New UI Components

Use the shadcn/ui CLI to add new components:

```bash
npx shadcn@latest add [component-name]
```

## 📱 Pages & Routes

- `/` - Home page with overview
- `/upload` - Upload images for analysis
- `/dashboard` - View analytics and stock data
- `/alert` - Manage alerts and notifications

## 🔌 API Integration

The frontend communicates with the backend API defined in `app/lib/api.ts`. Update the base URL in your environment variables:

```typescript
// app/lib/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

## 👥 Team

This project is built by the Freshtify team. Team member information and avatars are located in `app/assets/avatars/`.

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

---

Built with ❤️ using React Router v7 and modern web technologies.
