# AlphaForge Trading Dashboard

A modern React.js trading dashboard for cryptocurrency and financial market analysis.

## Features

- **Real-time Market Data**: Live price tickers and charts
- **Trading Signals**: Signal generation and analysis tools  
- **Portfolio Management**: Journal and trading analytics
- **Backtesting**: Strategy testing interface
- **Modern UI**: Responsive design with Tailwind CSS

## Tech Stack

- **Frontend**: React.js, JavaScript
- **Styling**: Tailwind CSS
- **Build Tool**: Create React App
- **Deployment**: Vercel/Netlify ready

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sadaru2002/AlphaForge.git
cd AlphaForge
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm run eject` - Ejects from Create React App (irreversible)

## Deployment

The project is configured for easy deployment:

- **Vercel**: Auto-deploys from this repository
- **Netlify**: Drag and drop the `build` folder
- **GitHub Pages**: Use `npm run build` and deploy the build folder

## Project Structure

```
src/
├── components/       # Reusable UI components
├── pages/           # Main application pages
├── hooks/           # Custom React hooks
├── services/        # API and external services
├── utils/           # Utility functions
├── config/          # Configuration files
└── App.jsx          # Main application component
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request

## License

This project is licensed under the MIT License.