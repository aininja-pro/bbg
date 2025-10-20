# BBG Rebate Processing Frontend

React-based web application for uploading and processing rebate Excel files.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your API URL
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── ui/         # shadcn/ui components
│   │   ├── upload/     # File upload components
│   │   ├── preview/    # Data preview components
│   │   ├── rules/      # Rules management
│   │   └── lookups/    # Lookup table management
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Utility functions
│   ├── services/       # API service layer
│   ├── App.jsx         # Main application component
│   └── main.jsx        # Entry point
├── package.json
└── README.md
```

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory, ready for deployment to Vercel.

## Features

- Drag-and-drop file upload
- Real-time processing progress
- Data preview with validation warnings
- Rules engine management
- Lookup table management
- CSV/ZIP export functionality
