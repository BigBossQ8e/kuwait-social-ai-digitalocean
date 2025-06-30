# Kuwait Social AI - React Frontend

This is the modern React + TypeScript frontend for Kuwait Social AI platform, replacing the vanilla JavaScript implementation.

## 🚀 Technology Stack

- **React 18** - UI library with concurrent features
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool and development server
- **Material-UI (MUI) v5** - Component library with RTL support
- **Redux Toolkit + RTK Query** - State management and data fetching
- **React Router v6** - Client-side routing
- **Emotion** - CSS-in-JS styling
- **Vitest** - Unit testing framework
- **ESLint + Prettier** - Code linting and formatting

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Generic components (Layout, Modal, etc.)
│   ├── auth/           # Authentication components
│   ├── dashboard/      # Dashboard-specific components
│   ├── posts/          # Post management components
│   ├── analytics/      # Analytics and reporting components
│   └── features/       # Kuwait-specific features
├── hooks/              # Custom React hooks
├── services/           # API services and utilities
│   ├── api/           # RTK Query API definitions
│   ├── cache/         # Caching utilities
│   └── errorLogger/   # Error logging service
├── store/              # Redux store configuration
│   └── slices/        # Redux slices
├── types/              # TypeScript type definitions
├── utils/              # Utility functions and constants
└── test/               # Test setup and utilities
```

## 🛠️ Development Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run type checking
npm run type-check

# Run linting
npm run lint

# Run tests
npm run test
```

### Development Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Run ESLint with auto-fix
- `npm run format` - Format code with Prettier
- `npm run test` - Run unit tests
- `npm run test:coverage` - Run tests with coverage report
- `npm run type-check` - Run TypeScript type checking

## 🌍 Kuwait-Specific Features

### RTL Support
The application includes full Right-to-Left (RTL) support for Arabic language:
- Material-UI RTL theme configuration
- Emotion styling with RTL support
- Arabic typography (Noto Kufi Arabic font)
- Dynamic language switching

### Cultural Considerations
- Prayer times integration
- Kuwait business hours (Sunday-Thursday)
- Cultural content validation
- Local holidays and events
- Islamic calendar support

## 🔐 Authentication & Security

- JWT token-based authentication
- Automatic token refresh
- Protected routes with role-based access
- Secure API communication
- Session management

## 📱 Responsive Design

- Mobile-first approach
- Tablet and desktop optimized layouts
- Touch-friendly interactions
- Progressive web app capabilities

## 🚦 Migration Status

This React frontend is part of the complete platform modernization. Current status:

### ✅ Completed (Phase 1)
- [x] Project setup with React + TypeScript + Vite
- [x] Essential dependencies installation
- [x] Folder structure organization
- [x] Development environment configuration
- [x] Redux store with RTK Query setup
- [x] Authentication system with hooks
- [x] Protected routing
- [x] RTL support for Arabic
- [x] Basic Material-UI theme

### 🚧 In Progress (Phase 2-6)
- [ ] Dashboard components migration
- [ ] Post management interface
- [ ] Analytics and reporting
- [ ] Competitor tracking
- [ ] Kuwait-specific features (Prayer times, etc.)
- [ ] Testing implementation
- [ ] Performance optimization
- [ ] Production deployment

## 🔗 API Integration

The frontend connects to the Flask backend API at `/api/*`. See the backend documentation for API endpoints and authentication requirements.

---

**Note**: This is the new React frontend that will eventually replace the current vanilla JavaScript implementation. Both versions may run in parallel during the migration period.
