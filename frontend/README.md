# ChatBI Autocomplete Frontend

A React + TypeScript frontend for the ChatBI Autocomplete Service.

## Features

- **Real-time Autocomplete**: Display suggestions as user types with 300ms debounce
- **Keyboard Navigation**: Support arrow keys, Enter, and Escape
- **Visual Feedback**: Show loading states, errors, and suggestion scores
- **Responsive Design**: Works on desktop and mobile devices
- **Backend Integration**: Connects to FastAPI backend for autocomplete and feedback

## Development

### Prerequisites

- Node.js 18+ and npm
- Backend service running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Usage

1. Start the backend service (see main README.md)
2. Start the frontend development server
3. Open http://localhost:3000 in your browser
4. Type in the search box to see autocomplete suggestions

## Architecture

```
frontend/
├── src/
│   ├── components/
│   │   └── Autocomplete.tsx    # Autocomplete component
│   ├── App.tsx                 # Main app component
│   ├── App.css                 # Styles
│   ├── main.tsx                # Entry point
│   └── vite-env.d.ts           # Vite types
├── index.html                  # HTML template
├── package.json                # Dependencies
├── tsconfig.json               # TypeScript config
├── tsconfig.node.json          # TypeScript config for Vite
└── vite.config.ts              # Vite configuration
```

## API Integration

The frontend communicates with the backend API:

- `POST /api/v1/autocomplete` - Get suggestions
- `POST /api/v1/feedback` - Submit user feedback
- `GET /api/v1/health` - Check backend health

API calls are proxied through Vite dev server to avoid CORS issues.

## Customization

You can customize the Autocomplete component by passing props:

```tsx
<Autocomplete
  apiUrl="/api/v1/autocomplete"
  userId="your-user-id"
  limit={10}
/>
```
