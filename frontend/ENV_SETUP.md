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

When using Docker, pass the environment variable:

```bash
docker build --build-arg VITE_API_URL=https://api.example.com -t frontend .
```

Or use docker-compose:

```yaml
services:
  frontend:
    build:
      context: .
      args:
        VITE_API_URL: https://api.example.com
```

## Available Variables

- `VITE_API_URL`: Backend API base URL (required for production)
