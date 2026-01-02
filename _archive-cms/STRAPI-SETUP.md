# Strapi 5 CMS Setup for Gabe Clarke Portfolio

This project uses Strapi 5 following the [official Docker documentation](https://docs.strapi.io/cms/installation/docker).

## ✅ Setup Complete!

The Strapi 5 project has been created and configured. Here's what's been set up:

### What's Configured

1. **Strapi 5 Project** - Created in `./strapi` directory
2. **PostgreSQL Database** - Configured to use PostgreSQL instead of SQLite
3. **Docker Setup** - Dockerfile and docker-compose.yml ready
4. **Environment Variables** - Generated secrets in `strapi/.env.docker`
5. **Database Config** - Updated to use PostgreSQL by default

## Quick Start

### 1. Install Dependencies (if needed)

If the npm install didn't complete due to disk space:

```bash
cd strapi
npm install
```

### 2. Run with Docker

From the project root:

```bash
docker-compose up strapi strapiDB
```

Or run everything (Strapi + Flask):

```bash
docker-compose up
```

### 3. Access Strapi Admin

Once running, access the Strapi admin panel:
- URL: `http://localhost:1337/admin`
- Create your admin account on first visit

## Project Structure

```
strapi/
├── config/
│   ├── database.ts      # PostgreSQL configuration
│   ├── server.ts
│   └── ...
├── src/                 # Your content types and API
├── public/             # Public assets
├── .env.docker         # Docker environment variables
├── Dockerfile          # Development Dockerfile
└── package.json        # Dependencies (pg instead of better-sqlite3)
```

## Configuration Details

### Database

- **Type**: PostgreSQL 16
- **Host**: `strapiDB` (Docker service name)
- **Port**: 5432
- **Database**: `strapi`
- **Username**: `strapi`
- **Password**: `strapi`

### Environment Variables

The `strapi/.env.docker` file contains:
- Database connection settings
- Generated JWT secrets
- Generated APP_KEYS
- Node environment

**Note**: For local development outside Docker, you may want to create a separate `.env` file with `DATABASE_HOST=localhost`.

## Creating Content Types

After accessing the admin panel, create content types for:

1. **Page** - For managing page content
   - Fields: title (Text), slug (UID), content (Rich Text), meta_description (Text)

2. **Project** - For portfolio projects/works
   - Fields: title, description, image (Media), composer, year

3. **Product** - For shop items (if applicable)
   - Fields: name, description, price (Number), image (Media)

## Integration with Flask

The Flask app (`app.py`) is configured to optionally fetch content from Strapi:

```python
STRAPI_URL = "http://strapi:1337"  # In Docker network
# or "http://localhost:1337" for local development
```

To enable Strapi integration, set `STRAPI_ENABLED=true` in your Flask environment.

## Troubleshooting

### Strapi won't start
- Check that PostgreSQL container is running: `docker-compose ps strapiDB`
- View logs: `docker-compose logs strapi`
- Ensure `strapi/.env.docker` exists with all required variables

### Database connection errors
- Wait for PostgreSQL to be ready: `docker-compose up strapiDB -d` then wait a few seconds
- Check database credentials in `strapi/.env.docker`
- Verify `DATABASE_HOST=strapiDB` (not `localhost`) in Docker

### TypeScript errors
- The project uses TypeScript. The Dockerfile includes TypeScript compilation
- If building fails, check that all dependencies are installed

## References

- [Strapi Docker Documentation](https://docs.strapi.io/cms/installation/docker)
- [Strapi Quick Start Guide](https://docs.strapi.io/cms/getting-started/quick-start)
- [Strapi REST API](https://docs.strapi.io/dev-docs/api/rest)






