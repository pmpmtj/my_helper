#!/usr/bin/env python3
"""
Django + PostgreSQL Setup Automation Script

This script automates the Django project setup process as described in readme.md
from steps 3-12, using configuration values from config_db.json.

Author: Automated Setup Script
Usage: python setup_django_postgres.py
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Initialize paths - handling both frozen (PyInstaller) and regular Python execution
SCRIPT_DIR = Path(__file__).resolve().parent

# Add project modules to path
sys.path.insert(0, str(SCRIPT_DIR))

from logging_utils import setup_logger
from utils import (
    resolve_path, check_command_available, check_django_project_exists,
    run_command, write_file_content, read_file_content, ensure_directory_exists
)

# Set up logging
logger = setup_logger('setup_django_postgres')


class DjangoPostgresSetup:
    """Main class for Django + PostgreSQL setup automation."""
    
    def __init__(self, config_file: str = 'config_db.json'):
        """
        Initialize the setup class.
        
        Args:
            config_file: Path to the configuration JSON file
        """
        self.config_file = resolve_path(config_file)
        self.config = {}
        self.project_dir = Path.cwd()
        
        logger.debug(f"Initializing Django setup with config: {self.config_file}")
        logger.debug(f"Working directory: {self.project_dir}")
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        logger.debug(f"Loading configuration from {self.config_file}")
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.debug("Configuration loaded successfully")
            return config
            
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to JSON file.
        
        Args:
            config: Configuration dictionary to save
            
        Raises:
            OSError: If config file cannot be written
        """
        logger.debug(f"Saving configuration to {self.config_file}")
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.debug("Configuration saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            # Don't raise here - this is not critical to the setup process
    
    def prompt_for_config_value(self, key: str, current_value: Any, description: str) -> Any:
        """
        Prompt user for a configuration value.
        
        Args:
            key: Configuration key
            current_value: Current/default value
            description: Description of what this value is for
            
        Returns:
            User input or default value (preserving original type)
        """
        if isinstance(current_value, list):
            current_display = ", ".join(current_value)
        else:
            current_display = str(current_value)
        
        prompt = f"{description}\nCurrent value: {current_display}\nNew value (press Enter for default): "
        user_input = input(prompt).strip()
        
        if not user_input:
            logger.debug(f"Using default value for {key}: {current_value}")
            return current_value
        else:
            # Handle boolean values
            if isinstance(current_value, bool):
                if user_input.lower() in ('true', 't', '1', 'yes', 'y'):
                    converted_value = True
                elif user_input.lower() in ('false', 'f', '0', 'no', 'n'):
                    converted_value = False
                else:
                    logger.warning(f"Invalid boolean value '{user_input}', using default: {current_value}")
                    return current_value
                logger.debug(f"User provided new boolean value for {key}: {converted_value}")
                return converted_value
            else:
                logger.debug(f"User provided new value for {key}: {user_input}")
                return user_input
    
    def gather_configuration(self) -> Dict[str, Any]:
        """
        Gather configuration values from user input.
        
        Returns:
            Updated configuration dictionary
        """
        logger.info("=== Django + PostgreSQL Setup Configuration ===")
        logger.info("Please review and update the configuration values:")
        logger.info("")
        
        config = self.load_config()
        
        # Define prompts for each configuration value
        prompts = {
            'STARTPROJECT_NAME': 'Django project name (used with startproject)',
            'STARTAPP_NAME': 'Django app name (used with startapp)',
            'USE_LOCAL_DATABASE': 'Use local PostgreSQL database (true) or cloud database (false)',
            'DB_NAME': 'PostgreSQL database name',
            'DB_USER': 'PostgreSQL database user',
            'DB_PASSWORD': 'PostgreSQL database password',
            'DB_HOST': 'PostgreSQL host',
            'DB_PORT': 'PostgreSQL port',
            'POSTGRES_SUPERUSER': 'PostgreSQL superuser (for creating DB/role - only needed for local DB)',
            'TEMPLATE_TITLE': 'HTML template title',
            'TEMPLATE_HEADING': 'HTML template main heading'
        }
        
        # Prompt for each configuration value
        for key, description in prompts.items():
            if key in config:
                config[key] = self.prompt_for_config_value(key, config[key], description)
        
        logger.debug("Configuration gathering completed")
        
        # Save updated configuration back to file
        self.save_config(config)
        
        return config
    
    def check_prerequisites(self) -> bool:
        """
        Check if all required tools are available.
        
        Returns:
            True if all prerequisites are met, False otherwise
        """
        logger.info("=== Checking Prerequisites ===")
        
        required_commands = ['python', 'django-admin', 'psql']
        all_good = True
        
        for command in required_commands:
            if check_command_available(command):
                logger.info(f"✓ {command} is available")
            else:
                logger.error(f"✗ {command} is not available in PATH")
                all_good = False
        
        # Check if we're in a virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.info("✓ Virtual environment is activated")
        else:
            logger.warning("⚠ No virtual environment detected")
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                logger.info("Setup cancelled by user")
                return False
        
        return all_good
    
    def check_existing_project(self) -> bool:
        """
        Check if Django project already exists.
        
        Returns:
            True if no existing project found, False if project exists
        """
        logger.info("=== Checking for Existing Django Project ===")
        
        if check_django_project_exists(self.project_dir):
            logger.error("Django project files already exist in current directory!")
            logger.error("This script should be run in an empty directory.")
            logger.error("Found potential Django files:")
            
            # List found Django files
            django_files = ['manage.py', 'settings.py', 'urls.py', 'wsgi.py', 'asgi.py']
            for file in django_files:
                if (self.project_dir / file).exists():
                    logger.error(f"  - {file}")
                
                # Check subdirectories
                for item in self.project_dir.iterdir():
                    if item.is_dir() and (item / file).exists():
                        logger.error(f"  - {item.name}/{file}")
            
            return False
        
        logger.info("✓ No existing Django project found")
        return True
    
    def create_django_project(self, project_name: str) -> bool:
        """
        Create Django project using django-admin startproject.
        
        Args:
            project_name: Name of the Django project
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"=== Creating Django Project: {project_name} ===")
        
        try:
            # Step 3: Initialize Django project in current folder
            logger.debug("Running django-admin startproject command")
            result = run_command(f"django-admin startproject {project_name} .", cwd=self.project_dir)
            
            logger.info(f"✓ Django project '{project_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Django project: {e}")
            return False
    
    def create_django_app(self, app_name: str) -> bool:
        """
        Create Django app using manage.py startapp.
        
        Args:
            app_name: Name of the Django app
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"=== Creating Django App: {app_name} ===")
        
        try:
            # Step 4: Create Django app
            logger.debug("Running manage.py startapp command")
            result = run_command(f"python manage.py startapp {app_name}", cwd=self.project_dir)
            
            logger.info(f"✓ Django app '{app_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Django app: {e}")
            return False
    
    def create_accounts_app(self) -> bool:
        """
        Create accounts app for user management.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Accounts App ===")
        
        try:
            # Create accounts app
            logger.debug("Running manage.py startapp accounts command")
            result = run_command("python manage.py startapp accounts", cwd=self.project_dir)
            
            logger.info("✓ Accounts app created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create accounts app: {e}")
            return False
    
    def create_custom_user_model(self) -> bool:
        """
        Create custom User model in accounts app.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Custom User Model ===")
        
        try:
            # Create custom User model in accounts/models.py
            user_model_content = '''from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model that extends AbstractUser.
    
    This model is designed to be easily extensible for future requirements.
    Currently adds email as a required and unique field.
    """
    email = models.EmailField(unique=True, blank=False)
    
    class Meta:
        db_table = 'auth_user'  # Keep standard table name for compatibility
        
    def __str__(self):
        return self.username
'''
            
            models_file = self.project_dir / 'accounts' / 'models.py'
            logger.debug(f"Writing custom User model to: {models_file}")
            write_file_content(models_file, user_model_content)
            
            logger.info("✓ Custom User model created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create custom User model: {e}")
            return False
    
    def create_accounts_forms(self) -> bool:
        """
        Create accounts/forms.py with SignUpForm.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Accounts Forms ===")
        
        try:
            # Create SignUpForm in accounts/forms.py
            forms_content = '''from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")  # password fields come from UserCreationForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
'''
            
            forms_file = self.project_dir / 'accounts' / 'forms.py'
            logger.debug(f"Writing accounts forms to: {forms_file}")
            write_file_content(forms_file, forms_content)
            
            logger.info("✓ Accounts forms created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create accounts forms: {e}")
            return False
    
    def create_accounts_views(self) -> bool:
        """
        Create accounts/views.py with SignUpView.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Accounts Views ===")
        
        try:
            # Create SignUpView in accounts/views.py
            views_content = '''from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")  # after sign-up, go to login
'''
            
            views_file = self.project_dir / 'accounts' / 'views.py'
            logger.debug(f"Writing accounts views to: {views_file}")
            write_file_content(views_file, views_content)
            
            logger.info("✓ Accounts views created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create accounts views: {e}")
            return False
    
    def create_accounts_urls(self) -> bool:
        """
        Create accounts/urls.py with signup route.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Accounts URLs ===")
        
        try:
            # Create accounts URLs configuration
            urls_content = '''from django.urls import path
from .views import SignUpView

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
]
'''
            
            urls_file = self.project_dir / 'accounts' / 'urls.py'
            logger.debug(f"Writing accounts URLs to: {urls_file}")
            write_file_content(urls_file, urls_content)
            
            logger.info("✓ Accounts URLs created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create accounts URLs: {e}")
            return False
    
    def create_accounts_admin(self) -> bool:
        """
        Create accounts/admin.py for User model admin.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Accounts Admin ===")
        
        try:
            # Create accounts admin configuration
            admin_content = '''from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "is_staff", "is_active",)
    search_fields = ("username", "email")
'''
            
            admin_file = self.project_dir / 'accounts' / 'admin.py'
            logger.debug(f"Writing accounts admin to: {admin_file}")
            write_file_content(admin_file, admin_content)
            
            logger.info("✓ Accounts admin created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create accounts admin: {e}")
            return False
    
    def create_registration_templates(self, app_name: str) -> bool:
        """
        Create registration templates (login.html, signup.html, logged_out.html).
        
        Args:
            app_name: Name of the Django app for template inheritance
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Registration Templates ===")
        
        try:
            # Create registration template directory
            registration_dir = self.project_dir / 'accounts' / 'templates' / 'registration'
            logger.debug(f"Creating registration template directory: {registration_dir}")
            ensure_directory_exists(registration_dir)
            
            # Login template
            login_template = '''{% extends "''' + app_name + '''/base.html" %}
{% block content %}
  <h2>Login</h2>
  <form method="post" action="{% url 'login' %}">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Login</button>
  </form>
  <p class="muted">No account? <a href="{% url 'signup' %}">Create one</a>.</p>
{% endblock %}
'''
            
            # Signup template
            signup_template = '''{% extends "''' + app_name + '''/base.html" %}
{% block content %}
  <h2>Create your account</h2>
  <form method="post" action="{% url 'signup' %}">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Sign up</button>
  </form>
  <p class="muted">Already have an account? <a href="{% url 'login' %}">Log in</a>.</p>
{% endblock %}
'''
            
            # Logged out template
            logged_out_template = '''{% extends "''' + app_name + '''/base.html" %}
{% block content %}
  <h2>Logged out</h2>
  <p>You have been logged out. <a href="{% url 'login' %}">Log in again</a>.</p>
{% endblock %}
'''
            
            # Write template files
            templates = [
                ('login.html', login_template),
                ('signup.html', signup_template),
                ('logged_out.html', logged_out_template)
            ]
            
            for template_name, template_content in templates:
                template_file = registration_dir / template_name
                logger.debug(f"Writing registration template: {template_file}")
                write_file_content(template_file, template_content)
            
            logger.info("✓ Registration templates created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create registration templates: {e}")
            return False
    
    def create_template_structure(self, app_name: str, title: str, heading: str) -> bool:
        """
        Create template directory structure and base template.
        
        Args:
            app_name: Name of the Django app
            title: HTML title for the template
            heading: Main heading for the template
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Template Structure ===")
        
        try:
            # Step 5: Create template directory structure
            template_dir = self.project_dir / app_name / 'templates' / app_name
            logger.debug(f"Creating template directory: {template_dir}")
            ensure_directory_exists(template_dir)
            
            # Create base.html template with authentication navigation
            template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{{ title|default:"''' + title + '''" }}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 2rem auto; max-width: 700px; line-height: 1.5; }
    header, main { margin-bottom: 1.5rem; }
    nav a { margin-right: 1rem; }
    form { display: grid; gap: .75rem; max-width: 420px; }
    input, button { padding: .6rem .7rem; font-size: 1rem; }
    .card { border: 1px solid #e5e7eb; border-radius: .75rem; padding: 1rem 1.25rem; }
    .muted { color: #6b7280; }
  </style>
</head>
<body>
  <header>
    <h1>''' + heading + '''</h1>
    <nav>
      <a href="{% url 'home' %}">Home</a>
      {% if request.user.is_authenticated %}
        <span class="muted">Hello, {{ request.user.username }}!</span>
        <form method="post" action="{% url 'logout' %}" style="display: inline;">
          {% csrf_token %}
          <button type="submit" style="background: none; border: none; color: #0066cc; text-decoration: underline; cursor: pointer; font-size: inherit; padding: 0;">Logout</button>
        </form>
      {% else %}
        <a href="{% url 'login' %}">Login</a>
        <a href="{% url 'signup' %}">Sign up</a>
      {% endif %}
    </nav>
  </header>

  <main>
    {% block content %}
      <div class="card">
        <p>Welcome. Use the navigation to login or sign up.</p>
      </div>
    {% endblock %}
  </main>
</body>
</html>'''
            
            template_file = template_dir / 'base.html'
            logger.debug(f"Writing template file: {template_file}")
            write_file_content(template_file, template_content)
            
            logger.info("✓ Template structure created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template structure: {e}")
            return False
    
    def generate_secret_key(self) -> str:
        """
        Generate a cryptographically secure Django SECRET_KEY.
        
        Returns:
            50-character random string suitable for Django SECRET_KEY
        """
        import secrets
        import string
        
        logger.debug("Generating cryptographically secure SECRET_KEY")
        
        # Use Django-recommended character set for SECRET_KEY
        chars = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
        secret_key = ''.join(secrets.choice(chars) for _ in range(50))
        
        logger.debug("SECRET_KEY generated successfully (50 characters)")
        return secret_key
    
    def create_env_file(self, config: Dict[str, Any]) -> bool:
        """
        Create .env file with database configuration and secure SECRET_KEY.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating .env File ===")
        
        try:
            # Generate a unique SECRET_KEY for this deployment
            secret_key = self.generate_secret_key()
            logger.info("✓ Generated unique SECRET_KEY for this deployment")
            
            # Step 7: Create .env file with SECRET_KEY and database config
            env_content = f'''# Django Secret Key - Keep this secret and unique per deployment!
SECRET_KEY={secret_key}

# Database Configuration
DB_NAME={config['DB_NAME'].lower()}
DB_USER={config['DB_USER'].lower()}
DB_PASSWORD={config['DB_PASSWORD']}
DB_HOST={config['DB_HOST']}
DB_PORT={config['DB_PORT']}'''
            
            env_file = self.project_dir / '.env'
            logger.debug(f"Writing .env file: {env_file}")
            write_file_content(env_file, env_content)
            
            logger.info("✓ .env file created successfully with secure SECRET_KEY")
            logger.warning("🔐 IMPORTANT: Keep the .env file secure and never commit it to version control!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            return False
    
    def run_psql_command_with_retry(self, command: str, description: str, max_attempts: int = 3) -> bool:
        """
        Run a psql command with retry logic for password authentication failures.
        
        Args:
            command: The psql command to execute
            description: Human-readable description of what the command does
            max_attempts: Maximum number of attempts (default: 3)
            
        Returns:
            True if successful, False if all attempts fail
        """
        for attempt in range(1, max_attempts + 1):
            try:
                if attempt > 1:
                    logger.info(f"Attempt {attempt}/{max_attempts} for {description}")
                else:
                    logger.info(f"{description}")
                
                result = run_command(command, capture_output=False)
                logger.info(f"✓ {description} completed successfully")
                return True
                
            except Exception as e:
                if attempt < max_attempts:
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed: {e}")
                    logger.info("Please check your password and try again...")
                else:
                    logger.error(f"All {max_attempts} attempts failed for {description}: {e}")
                    logger.error("Unable to authenticate with PostgreSQL superuser. Please check:")
                    logger.error("  • PostgreSQL superuser password")
                    logger.error("  • PostgreSQL server is running")
                    logger.error("  • Database connection settings (host, port)")
                    return False
        
        return False

    def create_database_and_role(self, config: Dict[str, Any]) -> bool:
        """
        Create PostgreSQL database and role (for local databases) or skip for cloud databases.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        use_local_db = config.get('USE_LOCAL_DATABASE', True)
        
        if not use_local_db:
            logger.info("=== Skipping Local Database Creation ===")
            logger.info("Using cloud database configuration")
            logger.info("✓ Cloud database mode - ensure your database is created and accessible")
            logger.info("✓ Update the .env file with your cloud database credentials after setup completes")
            return True
        
        logger.info("=== Creating Local PostgreSQL Database and Role ===")
        logger.info("You will be prompted for the PostgreSQL superuser password up to 3 times for each operation.")
        logger.info("If authentication fails 3 times for any operation, the setup will exit.")
        
        try:
            superuser = config['POSTGRES_SUPERUSER']
            db_user = config['DB_USER']
            db_password = config['DB_PASSWORD']
            db_name = config['DB_NAME']
            db_host = config['DB_HOST']
            db_port = config['DB_PORT']
            
            # Step 8a: Create role with retry logic (PostgreSQL automatically lowercases unquoted identifiers)
            db_user_lower = db_user.lower()
            db_name_lower = db_name.lower()
            create_role_cmd = f'psql -U {superuser} -h {db_host} -p {db_port} -c "CREATE ROLE {db_user_lower} WITH LOGIN PASSWORD \'{db_password}\';"'
            if not self.run_psql_command_with_retry(create_role_cmd, f"Creating role '{db_user_lower}'"):
                return False
            
            # Step 8b: Create database with retry logic
            create_db_cmd = f'psql -U {superuser} -h {db_host} -p {db_port} -c "CREATE DATABASE {db_name_lower} OWNER {db_user_lower} ENCODING \'UTF8\';"'
            if not self.run_psql_command_with_retry(create_db_cmd, f"Creating database '{db_name_lower}'"):
                return False
            
            # Step 8c: Grant privileges with retry logic
            grant_cmd = f'psql -U {superuser} -h {db_host} -p {db_port} -c "GRANT ALL PRIVILEGES ON DATABASE {db_name_lower} TO {db_user_lower};"'
            if not self.run_psql_command_with_retry(grant_cmd, f"Granting privileges on database '{db_name_lower}' to '{db_user_lower}'"):
                return False
            
            logger.info("✓ All local PostgreSQL database operations completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database and role: {e}")
            return False
    
    def update_settings_py(self, project_name: str, app_name: str) -> bool:
        """
        Update Django settings.py file with PostgreSQL configuration.
        
        Args:
            project_name: Name of the Django project
            app_name: Name of the Django app
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Updating Django Settings ===")
        
        try:
            settings_file = self.project_dir / project_name / 'settings.py'
            logger.debug(f"Reading settings file: {settings_file}")
            settings_content = read_file_content(settings_file)
            
            # Step 9a: Add imports
            logger.debug("Adding import statements")
            if 'from dotenv import load_dotenv' not in settings_content:
                settings_content = re.sub(
                    r'from pathlib import Path',
                    'from pathlib import Path\nimport os\nfrom dotenv import load_dotenv',
                    settings_content
                )
            
            # Step 9b: Add load_dotenv call
            logger.debug("Adding load_dotenv call")
            if 'load_dotenv(' not in settings_content:
                settings_content = re.sub(
                    r'(BASE_DIR\s*=.*)',
                    r"\1\nload_dotenv(BASE_DIR / '.env')",
                    settings_content
                )
            
            # Step 9c: Replace DATABASES configuration
            logger.debug("Updating DATABASES configuration")
            pg_database_config = '''DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'my_local_pg_project_db'),
        'USER': os.environ.get('DB_USER', 'my_local_pg_project_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}'''
            
            # Replace the entire DATABASES block
            settings_content = re.sub(
                r'DATABASES\s*=\s*\{[^}]*\}[^}]*\}',
                pg_database_config,
                settings_content,
                flags=re.MULTILINE | re.DOTALL
            )
            
            # Step 9d: Add apps to INSTALLED_APPS
            logger.debug(f"Adding '{app_name}' and 'accounts' to INSTALLED_APPS")
            if f"'{app_name}'" not in settings_content:
                settings_content = re.sub(
                    r"('django\.contrib\.staticfiles',)",
                    rf"\1\n    '{app_name}',\n    'accounts',",
                    settings_content
                )
            elif "'accounts'" not in settings_content:
                settings_content = re.sub(
                    r"('django\.contrib\.staticfiles',)",
                    rf"\1\n    'accounts',",
                    settings_content
                )
            
            # Step 9e: Add AUTH_USER_MODEL setting
            logger.debug("Adding AUTH_USER_MODEL setting")
            if 'AUTH_USER_MODEL' not in settings_content:
                # Add AUTH_USER_MODEL and auth settings at the end of the file
                auth_settings = """
# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Auth redirects
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Dev-only email output (password reset emails print to console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
"""
                settings_content += auth_settings
            
            # Step 9f: Save updated settings
            logger.debug("Saving updated settings.py")
            write_file_content(settings_file, settings_content)
            
            logger.info("✓ Django settings updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Django settings: {e}")
            return False
    
    def create_app_urls(self, app_name: str) -> bool:
        """
        Create URL configuration for the Django app.
        
        Args:
            app_name: Name of the Django app
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating App URL Configuration ===")
        
        try:
            # Step 10: Create app urls.py
            urls_content = '''from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
]'''
            
            urls_file = self.project_dir / app_name / 'urls.py'
            logger.debug(f"Writing URLs file: {urls_file}")
            write_file_content(urls_file, urls_content)
            
            logger.info("✓ App URL configuration created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create app URL configuration: {e}")
            return False
    
    def create_app_views(self, app_name: str) -> bool:
        """
        Create views for the Django app.
        
        Args:
            app_name: Name of the Django app
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating App Views ===")
        
        try:
            # Step 11: Create views.py
            views_content = f'''from django.shortcuts import render

def home(request):
    return render(request, "{app_name}/base.html")'''
            
            views_file = self.project_dir / app_name / 'views.py'
            logger.debug(f"Writing views file: {views_file}")
            write_file_content(views_file, views_content)
            
            logger.info("✓ App views created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create app views: {e}")
            return False
    
    def update_project_urls(self, project_name: str, app_name: str) -> bool:
        """
        Update project URL configuration to include app URLs.
        
        Args:
            project_name: Name of the Django project
            app_name: Name of the Django app
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Updating Project URL Configuration ===")
        
        try:
            # Step 12: Update project urls.py with auth routes
            project_urls_content = f'''from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("{app_name}.urls")),            # home
    path("accounts/", include("accounts.urls")),       # signup
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout/password reset
]'''
            
            project_urls_file = self.project_dir / project_name / 'urls.py'
            logger.debug(f"Writing project URLs file: {project_urls_file}")
            write_file_content(project_urls_file, project_urls_content)
            
            logger.info("✓ Project URL configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project URL configuration: {e}")
            return False
    
    def run_setup(self) -> bool:
        """
        Run the complete Django + PostgreSQL setup process.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("🚀 Starting Django + PostgreSQL Setup Automation")
        logger.info("=" * 60)
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                logger.error("Prerequisites check failed")
                return False
            
            # Check for existing project
            if not self.check_existing_project():
                logger.error("Existing project detected")
                return False
            
            # Gather configuration
            self.config = self.gather_configuration()
            
            # Execute setup steps
            steps = [
                ("Create Django Project", lambda: self.create_django_project(self.config['STARTPROJECT_NAME'])),
                ("Create Django App", lambda: self.create_django_app(self.config['STARTAPP_NAME'])),
                ("Create Accounts App", lambda: self.create_accounts_app()),
                ("Create Custom User Model", lambda: self.create_custom_user_model()),
                ("Create Accounts Forms", lambda: self.create_accounts_forms()),
                ("Create Accounts Views", lambda: self.create_accounts_views()),
                ("Create Accounts URLs", lambda: self.create_accounts_urls()),
                ("Create Accounts Admin", lambda: self.create_accounts_admin()),
                ("Create Template Structure", lambda: self.create_template_structure(
                    self.config['STARTAPP_NAME'], 
                    self.config['TEMPLATE_TITLE'], 
                    self.config['TEMPLATE_HEADING']
                )),
                ("Create Registration Templates", lambda: self.create_registration_templates(self.config['STARTAPP_NAME'])),
                ("Create .env File", lambda: self.create_env_file(self.config)),
                ("Configure Database (Local Creation or Cloud Setup)", lambda: self.create_database_and_role(self.config)),
                ("Update Django Settings", lambda: self.update_settings_py(
                    self.config['STARTPROJECT_NAME'], 
                    self.config['STARTAPP_NAME']
                )),
                ("Create App URLs", lambda: self.create_app_urls(self.config['STARTAPP_NAME'])),
                ("Create App Views", lambda: self.create_app_views(self.config['STARTAPP_NAME'])),
                ("Update Project URLs", lambda: self.update_project_urls(
                    self.config['STARTPROJECT_NAME'], 
                    self.config['STARTAPP_NAME']
                ))
            ]
            
            # Execute each step
            for step_name, step_func in steps:
                logger.info(f"\n--- {step_name} ---")
                if not step_func():
                    logger.error(f"Failed at step: {step_name}")
                    return False
            
            # Success message
            use_local_db = self.config.get('USE_LOCAL_DATABASE', True)
            db_type = "local PostgreSQL" if use_local_db else "cloud"
            
            logger.info("\n" + "=" * 60)
            logger.info("🎉 Django + PostgreSQL Setup Completed Successfully!")
            logger.info("=" * 60)
            logger.info("\nSetup includes:")
            logger.info(f"• Django project configured for {db_type} database")
            logger.info("• Custom User model (accounts.User) with email field")
            logger.info("• Complete signup/login authentication system")
            logger.info("• Authentication templates (login, signup, logout)")
            logger.info("• Authentication-aware navigation in base template")
            logger.info("• Admin interface for user management")
            logger.info("• PostgreSQL configuration in settings.py")
            logger.info("• Environment variables template in .env file")
            logger.info("• 🔐 Cryptographically secure SECRET_KEY generation (unique per deployment)")
            
            if not use_local_db:
                logger.info("\n🔧 Cloud Database Setup:")
                logger.info("• Update .env file with your cloud database credentials")
                logger.info("• Ensure your cloud database is created and accessible")
            
            logger.info("\nNext steps:")
            if not use_local_db:
                logger.info("1. Update .env file with your cloud database credentials")
                logger.info("2. Run: python manage.py makemigrations")
                logger.info("3. Run: python manage.py migrate")
                logger.info("4. (Optional) Run: python manage.py createsuperuser")
                logger.info("5. Run: python manage.py runserver")
                logger.info("6. Visit: http://127.0.0.1:8000/")
            else:
                logger.info("1. Run: python manage.py makemigrations")
                logger.info("2. Run: python manage.py migrate")
                logger.info("3. (Optional) Run: python manage.py createsuperuser")
                logger.info("4. Run: python manage.py runserver")
                logger.info("5. Visit: http://127.0.0.1:8000/")
            
            logger.info("\nAuthentication testing:")
            logger.info("• Visit /accounts/signup/ to create a new user account")
            logger.info("• Visit /accounts/login/ to log in")
            logger.info("• Use navigation to switch between authenticated/unauthenticated states")
            logger.info("• Visit /admin/ with superuser credentials to manage users")
            
            logger.info("\nYou should see: Authentication-aware navigation and working signup/login flow")
            logger.info("\nNote: Complete auth system is ready - customize templates and add features as needed!")
            
            return True
            
        except KeyboardInterrupt:
            logger.info("\nSetup cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during setup: {e}")
            return False


def main():
    """Main entry point for the script."""
    try:
        setup = DjangoPostgresSetup()
        success = setup.run_setup()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
