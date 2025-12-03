# Next.js Frontend for Hyper-Personalized Customer Support Chatbot

A modern, responsive Next.js TypeScript frontend for the Starbucks customer support chatbot, featuring real-time chat, nearby store finder, and location-based personalization.

## Features

- **Modern Next.js 14**: Server-side rendering and optimized performance
- **TypeScript**: Full type safety for better development experience
- **Tailwind CSS**: Utility-first styling with responsive design
- **Real-time Chat**: Live conversation with AI assistant
- **Location Services**: Automatic location detection and nearby store finder
- **Store Information**: Display nearby stores with distance, hours, and promotions
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile

## Project Structure

```
src/
├── components/           # React components
│   ├── ChatInterface.tsx # Main chat layout
│   ├── MessageList.tsx   # Message display
│   ├── MessageInput.tsx  # Input field
│   └── StoreCard.tsx    # Store information card
├── pages/               # Next.js pages
│   ├── _app.tsx        # App wrapper
│   ├── _document.tsx   # Document wrapper
│   └── index.tsx       # Home page
├── types/              # TypeScript interfaces
│   └── index.ts       # Type definitions
├── utils/             # Utility functions
│   └── api.ts        # API client and helpers
└── styles/           # CSS files
    └── globals.css   # Tailwind CSS imports
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn package manager

### Installation

1. **Install Dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Create Environment File**:
   ```bash
   cp .env.example .env.local
   ```

3. **Update Configuration** (if backend is on different port):
   ```bash
   # Edit .env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Development

Start the development server:

```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

### Building for Production

Build the optimized production bundle:

```bash
npm run build
npm start
```

### Type Checking

Run TypeScript type checking:

```bash
npm run type-check
```

## Component Architecture

### ChatInterface (Main Component)
- **Props**: messages, nearbyStores, onSendMessage, isLoading, error
- **Layout**: 70% chat area + 30% stores sidebar
- **Features**: Message display, input handling, store listing

### MessageList
- **Props**: messages, isLoading
- **Features**: Auto-scroll, timestamp display, loading indicator

### MessageInput
- **Props**: onSendMessage, isLoading, placeholder
- **Features**: Enter to send, button disable on loading, message clearing

### StoreCard
- **Props**: store, onStoreClick
- **Features**: Store info display, distance, status, promotions, contact info

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000`

### Key Endpoints

- **POST /api/v1/chat**: Send chat message
- **GET /api/v1/customers/{id}**: Get customer profile
- **GET /api/v1/stores/nearby**: Get nearby stores
- **GET /api/v1/documents/search**: Search knowledge base
- **GET /api/v1/health**: Health check

### Request Example

```typescript
const response = await apiClient.sendChatMessage({
  customer_id: 'demo-user-001',
  message: 'What's your best coffee for winter?',
  location: {
    latitude: 28.7041,
    longitude: 77.1025
  }
});
```

## Styling with Tailwind CSS

All styling is done using Tailwind CSS utility classes. No additional CSS files are needed.

### Color Scheme

- **Primary**: Teal (#0d9488) - Used for active elements, buttons, highlights
- **Gray**: Standard gray palette - Used for backgrounds and text
- **Status**: Green (open), Red (closed) - For store status indicators

### Custom Utilities

See `src/styles/globals.css` for:
- Message styling (user vs bot)
- Store card styling
- Button and input styles
- Promotion badges

## Error Handling

The application includes comprehensive error handling:

- Network errors are caught and displayed to the user
- Loading states prevent multiple simultaneous requests
- Toast notifications inform users of errors
- Graceful fallbacks for missing data

## Performance Optimizations

- **Image Optimization**: Next.js Image component for responsive images
- **Code Splitting**: Automatic code splitting by Next.js
- **CSS Optimization**: Tailwind CSS purges unused styles
- **Lazy Loading**: Components are lazy-loaded where appropriate

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### API Connection Issues

If you get "Failed to connect to API" error:

1. Ensure backend is running: `python run.py` from the backend directory
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is enabled in the FastAPI backend

### Location Permission

The app requests location permission. If denied:

- The app will use default Delhi location
- You can manually update location in settings (future feature)

### Module Not Found Errors

If you get TypeScript module errors:

1. Ensure all dependencies are installed: `npm install`
2. Delete `.next` folder and rebuild: `rm -rf .next && npm run build`

## Development Tips

### Add a New Component

1. Create file in `src/components/ComponentName.tsx`
2. Define TypeScript interface for props in `src/types/index.ts`
3. Import and use in pages

### Add a New API Endpoint

1. Add method to `APIClient` class in `src/utils/api.ts`
2. Define request/response types in `src/types/index.ts`
3. Use in components

### Styling a Component

Use Tailwind classes directly in JSX:

```tsx
<div className="flex items-center gap-2 p-4 bg-primary-50 rounded-lg">
  <span className="text-primary-600 font-semibold">Hello</span>
</div>
```

## Contributing

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Check the main project README
- Review the API documentation at `http://localhost:8000/docs`
- Check browser console for error messages