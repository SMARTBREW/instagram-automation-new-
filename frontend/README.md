# Instagram DM Automation - Frontend

Beautiful React frontend for Instagram DM Automation with animations.

## Features

- 🎨 Beautiful UI with custom color scheme (#f0e9d3, #f5cd4c, #000000)
- ✨ Smooth animations using Framer Motion
- 📱 Responsive design
- 🔐 JWT authentication
- 💬 Real-time message interface
- 🎯 Modern React with Vite

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Tech Stack

- React 18
- Vite
- React Router
- Framer Motion (animations)
- Tailwind CSS
- Axios
- React Hot Toast

## Pages

- `/login` - User login
- `/register` - User registration
- `/` - Dashboard (Instagram accounts)
- `/conversations/:accountId` - Conversations list
- `/messages/:conversationId` - Message interface

