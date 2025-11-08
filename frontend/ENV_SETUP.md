# Frontend Environment Configuration

## Environment Variables

The frontend uses environment variables to configure the backend API URL.

### Development

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000
```

In development, the app uses Vite's proxy, so you can leave it empty or set to `http://localhost:8000`.

### Production

For production deployment, create `.env.production` or set the environment variable:

```env
VITE_API_URL=https://your-backend-domain.com
```

### Building for Production

```bash
# Build with production env
npm run build

# The VITE_API_URL will be baked into the build
```

### Docker Deployment

> Note: Docker-related instructions have been intentionally removed from this guide. For local development and production builds, set `VITE_API_URL` in your environment or in `.env`/`.env.production` as appropriate. If you need container-based deployment, add project-specific instructions in a separate deployment guide.

## Available Variables

- `VITE_API_URL`: Backend API base URL (required for production)
