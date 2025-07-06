# Enhanced Dynamic Content System v6.1 - Frontend

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```

The application will be available at http://localhost:3000

## 📚 Technology Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Redux Toolkit** for state management
- **React Router** for navigation
- **Headless UI** for accessible components
- **Vite** for fast development and building

## 🎨 UI Features

### Pages
1. **Home Page** - Overview and introduction
2. **Categories Page** - Generate and manage content categories
3. **Content Generator** - Create content based on academic papers
4. **Library** - View and manage generated content

### Components
- **CategoryCard** - Display category information with scores
- **ContentViewer** - View and export generated content
- **Layout** - Main navigation and page structure

## 🔧 Development

### Project Structure
```
frontend/
├── src/
│   ├── components/     # Reusable components
│   ├── pages/         # Page components
│   ├── store/         # Redux store and slices
│   ├── utils/         # Utility functions
│   ├── App.tsx        # Main app component
│   ├── main.tsx       # Entry point
│   └── index.css      # Global styles with Tailwind
├── public/            # Static assets
├── package.json
├── tailwind.config.js # Tailwind configuration
├── vite.config.ts     # Vite configuration
└── tsconfig.json      # TypeScript configuration
```

### Tailwind CSS Classes

Custom utility classes defined in `index.css`:
- `.btn-primary` - Primary button style
- `.btn-secondary` - Secondary button style
- `.card` - Card container with shadow
- `.input` - Form input style

### State Management

Redux slices:
- `categoriesSlice` - Manage categories state
- `contentSlice` - Manage generated content

### API Integration

All API calls are proxied through Vite to the backend at http://localhost:8000

## 📱 Responsive Design

The application is fully responsive with:
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Touch-friendly interactions

## 🛠️ Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## 🧪 Development Tips

1. **Hot Module Replacement** - Changes are reflected instantly
2. **TypeScript Support** - Full type checking
3. **ESLint** - Code quality checks with `npm run lint`
4. **Fast Refresh** - Component state is preserved during edits

## 🎯 Key Features

- **Real-time Category Generation** - AI-powered category creation
- **Paper Discovery** - Automatic academic paper search
- **Multi-format Content** - Generate shorts, articles, and reports
- **Content Management** - View, filter, and export content
- **Quality Indicators** - Visual quality scores and metrics