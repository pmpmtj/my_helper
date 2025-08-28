# mY_Helper - Django Project Template with YouTube Downloader

A production-ready Django project template that automates the complete setup of a PostgreSQL-backed web application with integrated YouTube downloading capabilities. This template provides a robust foundation for web applications requiring user authentication and media processing features.

## 🚀 Features

### Core Django Setup
- **Automated Django + PostgreSQL Configuration**: Complete project initialization with database setup
- **Custom User Authentication System**: Extended user model with email field and complete auth flow
- **Production-Ready Architecture**: Proper path handling, logging, and configuration management
- **Environment Variable Management**: Secure SECRET_KEY generation and database configuration
- **Template System**: Authentication-aware base templates with modern UI

### YouTube Downloader Integration
- **Interactive Dashboard**: Web-based interface for YouTube video downloads
- **Advanced Metadata Storage**: Thumbnails, video statistics, and playlist information
- **Quality Selection**: Multiple format and quality options
- **Smart File Organization**: Automated file management and storage
- **Error Handling & Retry Logic**: Robust download processing with failure recovery

### Development Features
- **Centralized Logging**: Configurable logging system across all modules
- **Cross-Platform Compatibility**: Windows, macOS, and Linux support
- **Configuration Management**: JSON-based configuration with user prompts
- **Utility Functions**: Comprehensive file and directory operations
- **Database Flexibility**: Support for both local PostgreSQL and cloud databases

## 📋 Prerequisites

Before running the setup scripts, ensure you have the following installed:

### Required Software
- **Python 3.8+**: Main programming language
- **PostgreSQL**: Database server (for local setup) or cloud database access
- **pip**: Python package installer
- **Virtual Environment**: Recommended for isolation

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space for dependencies and downloads
- **Network**: Internet connection for package installation and YouTube access

### PostgreSQL Setup (Local Database)
If using a local PostgreSQL database:
1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Ensure PostgreSQL service is running
3. Know your PostgreSQL superuser credentials (usually 'postgres' user)
4. Verify `psql` command is available in your system PATH

### Cloud Database Alternative
For cloud databases (AWS RDS, Google Cloud SQL, etc.):
- Have your database connection credentials ready
- Ensure the database is accessible from your development environment
- Database should be PostgreSQL compatible

## 🛠️ Installation & Setup

### Step 1: Environment Preparation

1. **Clone or download this repository**:
   ```bash
   git clone <repository-url>
   cd mY_helper
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install base dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Configure Your Project

Edit `config_db.json` to customize your project settings:

```json
{
  "STARTPROJECT_NAME": "my_helper",           // Django project name
  "STARTAPP_NAME": "app_my_helper",           // Main Django app name
  "USE_LOCAL_DATABASE": true,                 // true = local PostgreSQL, false = cloud DB
  "DB_NAME": "db_my_helper",                  // Database name
  "DB_USER": "user_my_helper",                // Database user
  "DB_PASSWORD": "Change_ME",                 // Database password (CHANGE THIS!)
  "DB_HOST": "localhost",                     // Database host
  "DB_PORT": "5432",                         // Database port
  "POSTGRES_SUPERUSER": "postgres",          // PostgreSQL admin user (local only)
  "TEMPLATE_TITLE": "Django Lean Starter (PostgreSQL)",
  "TEMPLATE_HEADING": "WELCOME TO mY_Helper"
}
```

**Important**: Change the `DB_PASSWORD` to a secure password before running the setup!

### Step 3: Run the Django + PostgreSQL Setup

Execute the first setup script to create your Django project with authentication:

```bash
python setup_django_postgres_signup_login.py
```

This script will:
- ✅ Check all prerequisites (Python, Django, PostgreSQL)
- ✅ Prompt for configuration confirmation
- ✅ Create Django project and main app
- ✅ Set up custom User model with email field
- ✅ Create accounts app with signup/login functionality
- ✅ Generate secure SECRET_KEY and .env file
- ✅ Configure PostgreSQL database (local) or prepare for cloud DB
- ✅ Create authentication templates with modern UI
- ✅ Set up admin interface for user management
- ✅ Configure URL routing for authentication flows

**Expected Output**: A fully functional Django project with user authentication.

### Step 4: Database Migration

After the Django setup completes, run the Django migration commands:

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Create superuser account (optional but recommended)
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 5: Test Basic Authentication

Verify the basic setup works:

```bash
# Start the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` and test:
- ✅ Home page loads correctly
- ✅ Navigation shows login/signup links
- ✅ Signup process works (`/accounts/signup/`)
- ✅ Login process works (`/accounts/login/`)
- ✅ Admin interface accessible (`/admin/`)

### Step 6: Run the YouTube Downloader Setup

Once the basic Django setup is working, add the YouTube downloader functionality:

```bash
python setup_ytdl_app.py
```

This script will:
- ✅ Verify existing Django project
- ✅ Create YouTube downloader app (`app_ytdl_simple`)
- ✅ Set up video download models and database tables
- ✅ Create interactive dashboard interface
- ✅ Configure file storage and organization
- ✅ Add metadata extraction capabilities
- ✅ Set up error handling and retry logic
- ✅ Create admin interfaces for download management
- ✅ Add URL routing for downloader features

### Step 7: Final Migration and Testing

Run migrations for the new YouTube downloader app:

```bash
# Create migration files for the new app
python manage.py makemigrations

# Apply the new migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

## 🎯 Usage

### Authentication System

#### User Registration & Login
- **Signup**: Navigate to `/accounts/signup/` to create new accounts
- **Login**: Use `/accounts/login/` for user authentication
- **Logout**: Available in navigation when authenticated
- **Admin Panel**: Access `/admin/` with superuser credentials

#### User Management
- Custom User model extends Django's AbstractUser
- Email field is required and unique
- Admin interface for user management
- Password reset functionality (console backend for development)

### YouTube Downloader

#### Dashboard Access
- Navigate to `/ytdl/` for the main dashboard
- Interactive interface for video downloads
- Real-time progress updates
- Download history and management

#### Video Download Features
- **URL Input**: Paste YouTube video or playlist URLs
- **Quality Selection**: Choose from available formats
- **Metadata Extraction**: Automatic thumbnail and info retrieval
- **File Organization**: Smart storage and naming conventions
- **Batch Downloads**: Support for playlists and multiple videos

#### Advanced Features
- **Progress Tracking**: Real-time download progress
- **Error Recovery**: Automatic retry mechanisms
- **Storage Management**: Configurable download directories
- **Admin Interface**: Backend management of downloads

## 📁 Project Structure

```
mY_helper/
├── config_db.json                          # Main configuration file
├── requirements.txt                        # Python dependencies
├── setup_django_postgres_signup_login.py   # Django + auth setup script
├── setup_ytdl_app.py                      # YouTube downloader setup script
├── logging_utils/                         # Centralized logging system
│   ├── __init__.py
│   ├── config.json                        # Logging configuration
│   └── logger_config.py                   # Logger setup utility
├── utils/                                 # File and system utilities
│   ├── __init__.py
│   └── file_utils.py                     # Path resolution and file operations
└── [Generated Django Files After Setup]
    ├── manage.py                          # Django management script
    ├── .env                              # Environment variables (SECRET_KEY, DB config)
    ├── my_helper/                        # Django project directory
    │   ├── settings.py                   # Django configuration
    │   ├── urls.py                       # URL routing
    │   └── wsgi.py                       # WSGI configuration
    ├── app_my_helper/                    # Main Django app
    │   ├── templates/                    # HTML templates
    │   ├── views.py                      # View functions
    │   └── urls.py                       # App URL patterns
    ├── accounts/                         # User authentication app
    │   ├── models.py                     # Custom User model
    │   ├── views.py                      # Auth views
    │   ├── forms.py                      # Signup forms
    │   ├── admin.py                      # Admin configuration
    │   └── templates/registration/       # Auth templates
    └── app_ytdl_simple/                  # YouTube downloader app
        ├── models.py                     # Download models
        ├── views.py                      # Dashboard views
        ├── tasks.py                      # Download processing
        ├── templates/                    # Downloader templates
        └── static/                       # CSS/JS assets
```

## ⚙️ Configuration

### Environment Variables (.env)

After setup, your `.env` file will contain:
```env
# Django Secret Key - Keep this secret and unique per deployment!
SECRET_KEY=<automatically-generated-secure-key>

# Database Configuration
DB_NAME=db_my_helper
DB_USER=user_my_helper
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Logging Configuration

Customize logging in `logging_utils/config.json`:
```json
{
  "loggers": {
    "your_module_name": {
      "level": "DEBUG",
      "handlers": ["console"],
      "propagate": false
    }
  }
}
```

### Database Settings

#### Local PostgreSQL
- Automatically creates database and user
- Requires PostgreSQL superuser credentials
- Configures proper permissions and encoding

#### Cloud Database
- Set `USE_LOCAL_DATABASE: false` in config_db.json
- Update .env file with cloud database credentials
- Ensure database exists and is accessible

## 🔧 Customization

### Adding New Apps

1. **Create the app**:
   ```bash
   python manage.py startapp your_app_name
   ```

2. **Add to settings.py**:
   ```python
   INSTALLED_APPS = [
       # ... existing apps
       'your_app_name',
   ]
   ```

3. **Create URL patterns**:
   ```python
   # your_app_name/urls.py
   from django.urls import path
   from . import views

   urlpatterns = [
       path('', views.index, name='your_app_index'),
   ]
   ```

4. **Include in main URLs**:
   ```python
   # my_helper/urls.py
   urlpatterns = [
       # ... existing patterns
       path('your-app/', include('your_app_name.urls')),
   ]
   ```

### Extending the User Model

The custom User model in `accounts/models.py` can be extended:
```python
class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    
    # Add your custom fields here
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'auth_user'
```

### Customizing Templates

Templates use a responsive design framework. Customize in:
- `app_my_helper/templates/app_my_helper/base.html` - Main layout
- `accounts/templates/registration/` - Authentication pages
- `app_ytdl_simple/templates/` - YouTube downloader interface

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Errors
```
FATAL: password authentication failed for user "user_my_helper"
```
**Solution**: Verify PostgreSQL is running and credentials are correct

#### Django Import Errors
```
ModuleNotFoundError: No module named 'django'
```
**Solution**: Ensure virtual environment is activated and dependencies installed

#### psql Command Not Found
```
'psql' is not recognized as an internal or external command
```
**Solution**: Add PostgreSQL bin directory to system PATH

#### Permission Denied Errors
```
Permission denied: '/path/to/downloads'
```
**Solution**: Check directory permissions and disk space

### Debugging Steps

1. **Check Prerequisites**:
   ```bash
   python --version
   django-admin --version
   psql --version
   ```

2. **Verify Database Connection**:
   ```bash
   psql -U user_my_helper -d db_my_helper -h localhost
   ```

3. **Check Django Configuration**:
   ```bash
   python manage.py check
   python manage.py showmigrations
   ```

4. **Review Logs**:
   - Console output during setup
   - Django debug information
   - PostgreSQL logs

### Getting Help

If you encounter issues:
1. Check the console output for specific error messages
2. Verify all prerequisites are installed correctly
3. Ensure configuration values in `config_db.json` are correct
4. Check that PostgreSQL service is running (for local databases)
5. Verify virtual environment is activated

## 🔒 Security Considerations

### Production Deployment

Before deploying to production:

1. **Update Settings**:
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   ```

2. **Secure Environment Variables**:
   - Never commit `.env` file to version control
   - Use proper secret management in production
   - Rotate SECRET_KEY for each deployment

3. **Database Security**:
   - Use strong passwords for database users
   - Enable SSL/TLS for database connections
   - Restrict database access by IP

4. **File Uploads**:
   - Configure proper file storage (AWS S3, etc.)
   - Validate file types and sizes
   - Scan uploads for malware

### Development Security

- Default console email backend (not for production)
- Debug mode enabled (disable in production)
- Local database with basic authentication
- Default admin interface (secure in production)

## 📚 Dependencies

### Core Framework
- **Django 5.2.5**: Web framework
- **psycopg 3.2.9**: PostgreSQL adapter
- **python-dotenv 1.1.1**: Environment variable management

### YouTube Downloader
- **yt-dlp**: YouTube video downloading
- **youtube-transcript-api**: Subtitle extraction
- **colorama**: Terminal color output

### Development
- **asgiref**: ASGI utilities
- **sqlparse**: SQL parsing
- **typing_extensions**: Type hints
- **tzdata**: Timezone data

## 🤝 Contributing

When contributing to this project:

1. Follow the existing code style and architecture
2. Add proper logging for new features
3. Update configuration files as needed
4. Test both local and cloud database configurations
5. Document any new features or changes

## 📄 License

This project is designed as a template for Django applications. Customize and use according to your needs.

---

**Created with ❤️ for rapid Django development**

*Happy coding! 🚀*
