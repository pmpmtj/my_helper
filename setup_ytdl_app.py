#!/usr/bin/env python3
"""
YouTube Downloader App Setup Automation Script

This script automates the setup of app_ytdl_simple Django app with enhanced features:
- Interactive dashboard with live updates
- Complete metadata storage (thumbnails, stats, playlists)
- Advanced file organization
- Quality selection options
- Comprehensive error handling and retry functionality

Author: Automated Setup Script
Usage: python setup_ytdl_app.py
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

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
logger = setup_logger('setup_ytdl_app')


class YouTubeDownloaderSetup:
    """Main class for YouTube Downloader app setup automation."""
    
    def __init__(self, config_file: str = 'config_db.json'):
        """
        Initialize the setup class.
        
        Args:
            config_file: Path to the configuration JSON file
        """
        self.config_file = resolve_path(config_file)
        self.config = {}
        self.project_dir = Path.cwd()
        
        logger.debug(f"Initializing YouTube Downloader setup with config: {self.config_file}")
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
    
    def check_prerequisites(self) -> bool:
        """
        Check if all required tools and dependencies are available.
        
        Returns:
            True if all prerequisites are met, False otherwise
        """
        logger.info("=== Checking Prerequisites ===")
        
        all_good = True
        
        # Check if Django project exists
        if not check_django_project_exists(self.project_dir):
            logger.error("✗ No Django project found in current directory")
            logger.error("  Please run setup_django_postgres_signup_login.py first")
            all_good = False
        else:
            logger.info("✓ Django project detected")
        
        # Check for manage.py
        manage_py = self.project_dir / 'manage.py'
        if not manage_py.exists():
            logger.error("✗ manage.py not found")
            all_good = False
        else:
            logger.info("✓ manage.py found")
        
        # Check for accounts app (authentication system)
        accounts_dir = self.project_dir / 'accounts'
        if not accounts_dir.exists():
            logger.error("✗ accounts app not found")
            logger.error("  Authentication system is required for YouTube downloader")
            all_good = False
        else:
            logger.info("✓ accounts app found")
        
        # Check Python packages
        required_packages = [
            ('yt_dlp', 'yt-dlp'),
            ('youtube_transcript_api', 'youtube-transcript-api>=0.6.2')
        ]
        for module_name, package_name in required_packages:
            try:
                __import__(module_name)
                logger.info(f"✓ {package_name} is available")
            except ImportError:
                logger.error(f"✗ {package_name} is not installed")
                logger.error(f"  Run: pip install {package_name}")
                all_good = False
        
        # Check FFmpeg availability
        if check_command_available('ffmpeg'):
            logger.info("✓ FFmpeg is available")
        else:
            logger.error("✗ FFmpeg is not available in PATH")
            logger.error("  FFmpeg is required for audio/video processing")
            logger.error("  Windows: Install via scoop (scoop install ffmpeg) or download from https://ffmpeg.org/")
            logger.error("  Add ffmpeg.exe to your PATH environment variable")
            all_good = False
        
        return all_good
    
    def check_existing_app(self) -> bool:
        """
        Check if app_ytdl_simple already exists.
        
        Returns:
            True if no existing app found, False if app exists
        """
        logger.info("=== Checking for Existing YouTube Downloader App ===")
        
        app_dir = self.project_dir / 'app_ytdl_simple'
        if app_dir.exists():
            logger.error("app_ytdl_simple directory already exists!")
            logger.error("Please remove or rename the existing app directory first")
            return False
        
        logger.info("✓ No existing app_ytdl_simple found")
        return True
    
    def create_app_structure(self) -> bool:
        """
        Create the app_ytdl_simple Django app and directory structure.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating YouTube Downloader App Structure ===")
        
        try:
            # Create the Django app
            logger.debug("Running manage.py startapp app_ytdl_simple")
            result = run_command("python manage.py startapp app_ytdl_simple", cwd=self.project_dir)
            
            # Create additional directories
            app_dir = self.project_dir / 'app_ytdl_simple'
            template_dir = app_dir / 'templates' / 'app_ytdl_simple'
            static_dir = app_dir / 'static' / 'app_ytdl_simple'
            
            logger.debug(f"Creating template directory: {template_dir}")
            ensure_directory_exists(template_dir)
            
            logger.debug(f"Creating static directory: {static_dir}")
            ensure_directory_exists(static_dir / 'css')
            ensure_directory_exists(static_dir / 'js')
            
            # Create media directory structure
            media_dir = self.project_dir / 'media' / 'yt'
            logger.debug(f"Creating media directory: {media_dir}")
            ensure_directory_exists(media_dir)
            
            logger.info("✓ App structure created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create app structure: {e}")
            return False
    
    def create_enhanced_models(self) -> bool:
        """
        Create enhanced models with complete metadata support.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Enhanced Models ===")
        
        try:
            models_content = '''import uuid
import os
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.urls import reverse


class DownloadJob(models.Model):
    """Enhanced download job model with complete metadata support."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        DONE = 'DONE', 'Done'
        ERROR = 'ERROR', 'Error'
        RETRYING = 'RETRYING', 'Retrying'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    class Quality(models.TextChoices):
        BEST = 'best', 'Best Available'
        WORST = 'worst', 'Worst Available'
        HD1080 = '1080p', '1080p'
        HD720 = '720p', '720p'
        SD480 = '480p', '480p'
        SD360 = '360p', '360p'
        SD240 = '240p', '240p'
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Source information
    url = models.URLField(max_length=2048)
    original_url = models.URLField(max_length=2048, blank=True)  # For playlist items
    playlist_id = models.CharField(max_length=64, blank=True)
    playlist_title = models.CharField(max_length=512, blank=True)
    playlist_uploader = models.CharField(max_length=255, blank=True)
    playlist_index = models.PositiveIntegerField(null=True, blank=True)
    playlist_count = models.PositiveIntegerField(null=True, blank=True)
    
    # Request configuration
    requested_types = models.CharField(max_length=64)  # e.g. "MP3,MP4,TRANSCRIPT"
    requested_quality = models.CharField(max_length=20, choices=Quality.choices, default=Quality.BEST)
    custom_subfolder = models.CharField(max_length=255, blank=True)
    
    # Output configuration
    output_dir_rel = models.CharField(max_length=255, blank=True)
    
    # Status and progress
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    progress_pct = models.PositiveSmallIntegerField(default=0)
    message = models.TextField(blank=True)
    error_details = models.TextField(blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    # Video metadata
    video_id = models.CharField(max_length=32, blank=True)
    video_title = models.CharField(max_length=512, blank=True)
    video_description = models.TextField(blank=True)
    duration_secs = models.PositiveIntegerField(null=True, blank=True)
    upload_date = models.DateField(null=True, blank=True)
    
    # Channel/uploader information
    channel_id = models.CharField(max_length=64, blank=True)
    channel_name = models.CharField(max_length=255, blank=True)
    uploader = models.CharField(max_length=255, blank=True)
    uploader_id = models.CharField(max_length=64, blank=True)
    
    # Engagement metrics
    view_count = models.BigIntegerField(null=True, blank=True)
    like_count = models.BigIntegerField(null=True, blank=True)
    dislike_count = models.BigIntegerField(null=True, blank=True)
    comment_count = models.BigIntegerField(null=True, blank=True)
    
    # Technical metadata
    original_width = models.PositiveIntegerField(null=True, blank=True)
    original_height = models.PositiveIntegerField(null=True, blank=True)
    fps = models.FloatField(null=True, blank=True)
    video_codec = models.CharField(max_length=64, blank=True)
    audio_codec = models.CharField(max_length=64, blank=True)
    
    # Thumbnail
    thumbnail_url = models.URLField(max_length=2048, blank=True)
    thumbnail_path = models.CharField(max_length=512, blank=True)
    thumbnail_size = models.BigIntegerField(null=True, blank=True)
    
    # Output files
    path_mp3 = models.CharField(max_length=512, blank=True)
    size_mp3 = models.BigIntegerField(null=True, blank=True)
    checksum_mp3 = models.CharField(max_length=64, blank=True)
    
    path_mp4 = models.CharField(max_length=512, blank=True)
    size_mp4 = models.BigIntegerField(null=True, blank=True)
    checksum_mp4 = models.CharField(max_length=64, blank=True)
    
    path_txt = models.CharField(max_length=512, blank=True)  # timestamped
    size_txt = models.BigIntegerField(null=True, blank=True)
    
    path_txt_plain = models.CharField(max_length=512, blank=True)  # no timestamps
    size_txt_plain = models.BigIntegerField(null=True, blank=True)
    
    # Categorization and tags
    tags = models.TextField(blank=True)  # JSON array of tags
    categories = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['video_id']),
            models.Index(fields=['playlist_id']),
        ]
    
    def __str__(self):
        return f"{self.video_title or self.url} — {self.status}"
    
    def get_absolute_url(self):
        return reverse('app_ytdl_simple:job_detail', kwargs={'pk': self.pk})
    
    @property
    def duration_formatted(self):
        """Return duration in MM:SS or HH:MM:SS format."""
        if not self.duration_secs:
            return "Unknown"
        
        hours = self.duration_secs // 3600
        minutes = (self.duration_secs % 3600) // 60
        seconds = self.duration_secs % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def file_size_total(self):
        """Return total file size of all outputs."""
        total = 0
        for size in [self.size_mp3, self.size_mp4, self.size_txt, self.size_txt_plain, self.thumbnail_size]:
            if size:
                total += size
        return total
    
    @property
    def available_downloads(self):
        """Return list of available download types."""
        downloads = []
        if self.path_mp3:
            downloads.append(('mp3', 'MP3 Audio', self.size_mp3))
        if self.path_mp4:
            downloads.append(('mp4', 'MP4 Video', self.size_mp4))
        if self.path_txt:
            downloads.append(('txt', 'Transcript (Timestamped)', self.size_txt))
        if self.path_txt_plain:
            downloads.append(('txt_plain', 'Transcript (Plain)', self.size_txt_plain))
        if self.thumbnail_path:
            downloads.append(('thumbnail', 'Thumbnail', self.thumbnail_size))
        return downloads


class DownloadStats(models.Model):
    """User download statistics."""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Counts
    total_jobs = models.PositiveIntegerField(default=0)
    successful_jobs = models.PositiveIntegerField(default=0)
    failed_jobs = models.PositiveIntegerField(default=0)
    
    # Storage
    total_files_size = models.BigIntegerField(default=0)  # bytes
    
    # Activity
    last_download = models.DateTimeField(null=True, blank=True)
    first_download = models.DateTimeField(null=True, blank=True)
    
    # Updated automatically
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Download statistics"
    
    def __str__(self):
        return f"{self.user.username} - {self.total_jobs} jobs"
    
    @property
    def success_rate(self):
        """Return success rate as percentage."""
        if self.total_jobs == 0:
            return 0
        return (self.successful_jobs / self.total_jobs) * 100
    
    @property
    def storage_formatted(self):
        """Return formatted storage size."""
        size = self.total_files_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
'''
            
            models_file = self.project_dir / 'app_ytdl_simple' / 'models.py'
            logger.debug(f"Writing enhanced models to: {models_file}")
            write_file_content(models_file, models_content)
            
            logger.info("✓ Enhanced models created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create enhanced models: {e}")
            return False
    
    def create_enhanced_forms(self) -> bool:
        """
        Create enhanced forms with quality selection and advanced options.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Enhanced Forms ===")
        
        try:
            forms_content = '''from django import forms
from django.core.validators import URLValidator
from .models import DownloadJob
from .utils import safe_subpath


class DownloadBatchForm(forms.Form):
    """Enhanced batch download form with quality selection."""
    
    urls = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'Paste one URL per line. Playlists and channels supported.\\n\\nExamples:\\nhttps://www.youtube.com/watch?v=VIDEO_ID\\nhttps://www.youtube.com/playlist?list=PLAYLIST_ID',
            'class': 'form-control'
        }),
        help_text='One URL per line. Supports individual videos, playlists, and channels.'
    )
    
    # Output selection
    want_mp3 = forms.BooleanField(
        required=False, 
        initial=True, 
        label='Audio (MP3)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    want_mp4 = forms.BooleanField(
        required=False, 
        label='Video (MP4)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    want_transcript = forms.BooleanField(
        required=False, 
        label='Transcript (English)',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    want_thumbnail = forms.BooleanField(
        required=False, 
        label='Thumbnail',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Quality selection
    quality = forms.ChoiceField(
        choices=DownloadJob.Quality.choices,
        initial=DownloadJob.Quality.BEST,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Video quality preference (audio quality automatically optimized)'
    )
    
    # Organization
    subfolder = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Optional: organize files in subfolder',
            'class': 'form-control'
        }),
        help_text='Optional subfolder under your download directory'
    )
    
    # Advanced options
    organize_by_channel = forms.BooleanField(
        required=False,
        label='Organize by channel',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Create subfolders for each channel/uploader'
    )
    
    organize_by_date = forms.BooleanField(
        required=False,
        label='Organize by date',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Create date-based folder structure (YYYY/MM)'
    )
    
    def clean(self):
        """Validate form data."""
        data = super().clean()
        
        # At least one output type must be selected
        output_types = [
            data.get('want_mp3'),
            data.get('want_mp4'),
            data.get('want_transcript'),
            data.get('want_thumbnail')
        ]
        
        if not any(output_types):
            raise forms.ValidationError('Please select at least one output type.')
        
        # Clean and validate subfolder
        subfolder = data.get('subfolder', '').strip()
        if subfolder:
            cleaned = safe_subpath(subfolder)
            if not cleaned:
                raise forms.ValidationError('Invalid subfolder name. Use only letters, numbers, spaces, hyphens, and dots.')
            data['subfolder'] = cleaned
        
        # Basic URL validation
        urls_raw = data.get('urls', '').strip()
        if not urls_raw:
            raise forms.ValidationError('Please provide at least one URL.')
        
        urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]
        if not urls:
            raise forms.ValidationError('Please provide at least one valid URL.')
        
        # Validate each URL
        validator = URLValidator()
        invalid_urls = []
        
        for url in urls:
            try:
                validator(url)
                # Basic YouTube URL check
                if not any(domain in url.lower() for domain in ['youtube.com', 'youtu.be', 'm.youtube.com']):
                    invalid_urls.append(url)
            except forms.ValidationError:
                invalid_urls.append(url)
        
        if invalid_urls:
            raise forms.ValidationError(f'Invalid URLs detected: {", ".join(invalid_urls[:3])}{"..." if len(invalid_urls) > 3 else ""}')
        
        data['urls_list'] = urls
        return data


class JobRetryForm(forms.Form):
    """Form for retrying failed jobs."""
    
    job_ids = forms.CharField(widget=forms.HiddenInput())
    
    # Allow users to change settings for retry
    change_quality = forms.BooleanField(required=False, label='Change quality settings')
    new_quality = forms.ChoiceField(
        choices=DownloadJob.Quality.choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    change_outputs = forms.BooleanField(required=False, label='Change output types')
    want_mp3 = forms.BooleanField(required=False, label='Audio (MP3)')
    want_mp4 = forms.BooleanField(required=False, label='Video (MP4)')
    want_transcript = forms.BooleanField(required=False, label='Transcript')
    want_thumbnail = forms.BooleanField(required=False, label='Thumbnail')


class JobSearchForm(forms.Form):
    """Form for searching and filtering jobs."""
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by title, channel, or URL...',
            'class': 'form-control'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(DownloadJob.Status.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    output_type = forms.ChoiceField(
        choices=[
            ('', 'All Types'),
            ('mp3', 'Has MP3'),
            ('mp4', 'Has MP4'),
            ('transcript', 'Has Transcript'),
            ('thumbnail', 'Has Thumbnail')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
'''
            
            forms_file = self.project_dir / 'app_ytdl_simple' / 'forms.py'
            logger.debug(f"Writing enhanced forms to: {forms_file}")
            write_file_content(forms_file, forms_content)
            
            logger.info("✓ Enhanced forms created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create enhanced forms: {e}")
            return False
    
    def update_settings_py(self) -> bool:
        """
        Update Django settings.py to include the new app and media settings.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Updating Django Settings ===")
        
        try:
            # Find the project name from config
            config = self.load_config()
            project_name = config.get('STARTPROJECT_NAME', 'proj_nineteen_o_six')
            
            settings_file = self.project_dir / project_name / 'settings.py'
            logger.debug(f"Reading settings file: {settings_file}")
            settings_content = read_file_content(settings_file)
            
            # Add app to INSTALLED_APPS if not already present
            if "'app_ytdl_simple'" not in settings_content:
                logger.debug("Adding app_ytdl_simple to INSTALLED_APPS")
                settings_content = re.sub(
                    r"('accounts',)",
                    r"\1\n    'app_ytdl_simple',",
                    settings_content
                )
            
            # Add media settings if not present
            if 'MEDIA_URL' not in settings_content:
                logger.debug("Adding media configuration")
                media_settings = """
# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# YouTube Downloader settings
YT_DL_BASE_DIR = 'yt'
YT_DL_MAX_WORKERS = 2
YT_DL_MAX_RETRIES = 3
YT_DL_RETRY_DELAY = 60  # seconds
"""
                settings_content += media_settings
            elif 'YT_DL_BASE_DIR' not in settings_content:
                logger.debug("Adding YouTube downloader settings")
                ytdl_settings = """
# YouTube Downloader settings
YT_DL_BASE_DIR = 'yt'
YT_DL_MAX_WORKERS = 2
YT_DL_MAX_RETRIES = 3
YT_DL_RETRY_DELAY = 60  # seconds
"""
                settings_content += ytdl_settings
            
            # Save updated settings
            logger.debug("Saving updated settings.py")
            write_file_content(settings_file, settings_content)
            
            logger.info("✓ Django settings updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update Django settings: {e}")
            return False
    
    def update_project_urls(self) -> bool:
        """
        Update project URLs to include YouTube downloader routes and media serving.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Updating Project URLs ===")
        
        try:
            # Find the project name from config
            config = self.load_config()
            project_name = config.get('STARTPROJECT_NAME', 'proj_nineteen_o_six')
            
            project_urls_file = self.project_dir / project_name / 'urls.py'
            logger.debug(f"Reading project URLs file: {project_urls_file}")
            urls_content = read_file_content(project_urls_file)
            
            # Add imports if not present
            if 'from django.conf import settings' not in urls_content:
                urls_content = re.sub(
                    r'from django.urls import path, include',
                    'from django.urls import path, include\nfrom django.conf import settings\nfrom django.conf.urls.static import static',
                    urls_content
                )
            elif 'from django.conf.urls.static import static' not in urls_content:
                urls_content = re.sub(
                    r'from django.conf import settings',
                    'from django.conf import settings\nfrom django.conf.urls.static import static',
                    urls_content
                )
            
            # Add YouTube downloader URL if not present
            if 'app_ytdl_simple' not in urls_content:
                logger.debug("Adding YouTube downloader URL pattern")
                urls_content = re.sub(
                    r'(path\("accounts/", include\("django\.contrib\.auth\.urls"\)\),)',
                    r'\1\n    path("tools/ytdl/", include("app_ytdl_simple.urls", namespace="app_ytdl_simple")),',
                    urls_content
                )
            
            # Add media URL serving for development if not present
            if 'static(settings.MEDIA_URL' not in urls_content:
                logger.debug("Adding media URL serving for development")
                urls_content = re.sub(
                    r'(urlpatterns = \[.*?\])',
                    r'\1\n\nif settings.DEBUG:\n    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)',
                    urls_content,
                    flags=re.DOTALL
                )
            
            # Save updated URLs
            logger.debug("Saving updated project URLs")
            write_file_content(project_urls_file, urls_content)
            
            logger.info("✓ Project URLs updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update project URLs: {e}")
            return False
    
    def run_migrations(self) -> bool:
        """
        Run Django migrations for the new app.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Running Migrations ===")
        
        try:
            # Create migrations
            logger.debug("Creating migrations for app_ytdl_simple")
            result = run_command("python manage.py makemigrations app_ytdl_simple", cwd=self.project_dir)
            
            # Apply migrations
            logger.debug("Applying migrations")
            result = run_command("python manage.py migrate", cwd=self.project_dir)
            
            logger.info("✓ Migrations completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to run migrations: {e}")
            return False
    
    def create_enhanced_utils(self) -> bool:
        """
        Create enhanced utility functions.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Enhanced Utils ===")
        
        try:
            utils_content = '''import os
import re
import hashlib
from datetime import datetime
from pathlib import Path
from django.conf import settings
from django.utils import timezone


SAFE_SEGMENT_RE = re.compile(r'^[\\w\\-\\s\\.]{1,200}$')


def safe_subpath(raw: str) -> str:
    """Sanitize path segments for safe file system usage."""
    raw = (raw or '').strip().replace('..', '')
    if not raw:
        return ''
    parts = [p for p in raw.replace('\\\\', '/').split('/') if p]
    safe = [p for p in parts if SAFE_SEGMENT_RE.match(p)]
    return '/'.join(safe)


def media_base_for(user) -> str:
    """Get base media directory for user."""
    base = getattr(settings, 'YT_DL_BASE_DIR', 'yt')
    owner = str(user.id) if user and user.is_authenticated else 'anon'
    return os.path.join(base, owner)


def join_rel(*parts: str) -> str:
    """Join path parts with forward slashes."""
    return os.path.join(*parts).replace('\\\\', '/')


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if not size_bytes:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def calculate_file_checksum(file_path: Path) -> str:
    """Calculate SHA-256 checksum of a file."""
    try:
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception:
        return ""


def organize_output_path(job, base_dir: Path, filename: str) -> Path:
    """Organize output path based on job settings."""
    output_path = base_dir
    
    # Add date-based organization if requested
    if hasattr(job, 'organize_by_date') and job.organize_by_date:
        now = timezone.now()
        output_path = output_path / str(now.year) / f"{now.month:02d}"
    
    # Add channel-based organization if requested
    if hasattr(job, 'organize_by_channel') and job.organize_by_channel and job.channel_name:
        safe_channel = safe_subpath(job.channel_name)
        if safe_channel:
            output_path = output_path / safe_channel
    
    # Add custom subfolder if specified
    if job.custom_subfolder:
        output_path = output_path / job.custom_subfolder
    
    # Ensure directory exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    return output_path / filename


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """Sanitize filename for safe file system usage."""
    # Handle None or empty input
    if not filename or not isinstance(filename, str):
        return "Unknown"
    
    # Remove or replace problematic characters
    filename = re.sub(r'[<>:"/\\\\\\\\|?*]', '_', filename)
    filename = re.sub(r'[\\x00-\\x1f]', '', filename)  # Remove control characters
    filename = filename.strip('. ')  # Remove leading/trailing dots and spaces
    
    # If filename becomes empty after sanitization, provide fallback
    if not filename:
        return "Unknown"
    
    # Truncate if too long, preserving extension
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    patterns = [
        r'(?:youtube\\.com/watch\\?v=|youtu\\.be/|youtube\\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\\.com/watch\\?.*&v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ""


def is_playlist_url(url: str) -> bool:
    """Check if URL is a playlist URL."""
    playlist_patterns = [
        r'youtube\\.com/playlist\\?list=',
        r'youtube\\.com/watch\\?.*&list=',
        r'youtube\\.com/channel/',
        r'youtube\\.com/user/',
        r'youtube\\.com/c/',
    ]
    
    return any(re.search(pattern, url) for pattern in playlist_patterns)


def estimate_download_time(file_size: int, bitrate_kbps: int = 1000) -> int:
    """Estimate download time in seconds based on file size and connection speed."""
    if not file_size or not bitrate_kbps:
        return 0
    
    # Convert bitrate from kbps to bytes per second
    bytes_per_second = (bitrate_kbps * 1024) / 8
    
    # Add 20% buffer for overhead
    estimated_seconds = (file_size / bytes_per_second) * 1.2
    
    return int(estimated_seconds)


def get_thumbnail_filename(video_id: str, title: str) -> str:
    """Generate thumbnail filename."""
    safe_title = sanitize_filename(title[:50], 50)
    return f"{safe_title} [{video_id}].jpg"


def parse_duration(duration_str: str) -> int:
    """Parse duration string (PT4M13S) to seconds."""
    if not duration_str:
        return 0
    
    # Handle ISO 8601 duration format (PT4M13S)
    if duration_str.startswith('PT'):
        duration_str = duration_str[2:]  # Remove 'PT'
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours
        if 'H' in duration_str:
            hours_match = re.search(r'(\\\\d+)H', duration_str)
            if hours_match:
                hours = int(hours_match.group(1))
        
        # Extract minutes
        if 'M' in duration_str:
            minutes_match = re.search(r'(\\\\d+)M', duration_str)
            if minutes_match:
                minutes = int(minutes_match.group(1))
        
        # Extract seconds
        if 'S' in duration_str:
            seconds_match = re.search(r'(\\\\d+)S', duration_str)
            if seconds_match:
                seconds = int(seconds_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds
    
    # Handle simple formats like "4:13" or "1:04:13"
    parts = duration_str.split(':')
    if len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    
    return 0
'''
            
            utils_file = self.project_dir / 'app_ytdl_simple' / 'utils.py'
            logger.debug(f"Writing enhanced utils to: {utils_file}")
            write_file_content(utils_file, utils_content)
            
            logger.info("✓ Enhanced utils created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create enhanced utils: {e}")
            return False
    
    def create_enhanced_tasks(self) -> bool:
        """
        Create enhanced background task processing with retry logic and complete metadata.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Enhanced Background Tasks ===")
        
        try:
            tasks_content = '''import os
import json
import math
import time
import hashlib
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

import yt_dlp
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

from .models import DownloadJob, DownloadStats
from .utils import (
    media_base_for, join_rel, organize_output_path, sanitize_filename,
    calculate_file_checksum, get_thumbnail_filename, format_file_size
)

# Global thread pool executor
_executor = None
_stats_cache = {}


def _get_executor():
    """Get or create thread pool executor."""
    global _executor
    if _executor is None:
        max_workers = getattr(settings, 'YT_DL_MAX_WORKERS', 2)
        _executor = ThreadPoolExecutor(max_workers=max_workers)
    return _executor


def enqueue_job(job_id: str):
    """Enqueue a job for background processing."""
    _get_executor().submit(_process_job, job_id)


def _set(job: DownloadJob, **fields):
    """Atomically update job fields."""
    with transaction.atomic():
        j = DownloadJob.objects.select_for_update().get(pk=job.pk)
        for k, v in fields.items():
            setattr(j, k, v)
        j.save()


def _job_dir(job: DownloadJob) -> Path:
    """Get job output directory."""
    base = Path(settings.MEDIA_ROOT) / media_base_for(job.user) / str(job.id)
    base.mkdir(parents=True, exist_ok=True)
    return base


def _bytes(path: Path) -> Optional[int]:
    """Get file size in bytes."""
    try:
        return path.stat().st_size
    except Exception:
        return None


def _progress_update(job, pct, msg):
    """Update job progress."""
    pct = max(0, min(99, int(pct)))
    _set(job, progress_pct=pct, message=msg, updated_at=timezone.now())


def _download_thumbnail(job: DownloadJob, info: Dict[str, Any], out_dir: Path) -> Optional[str]:
    """Download video thumbnail."""
    try:
        thumbnail_url = info.get('thumbnail')
        if not thumbnail_url:
            return None
        
        thumbnail_filename = get_thumbnail_filename(job.video_id, job.video_title)
        thumbnail_path = out_dir / thumbnail_filename
        
        # Download thumbnail
        response = requests.get(thumbnail_url, timeout=30)
        response.raise_for_status()
        
        with open(thumbnail_path, 'wb') as f:
            f.write(response.content)
        
        rel_path = thumbnail_path.relative_to(settings.MEDIA_ROOT)
        size = _bytes(thumbnail_path)
        
        _set(job, 
             thumbnail_url=thumbnail_url,
             thumbnail_path=str(rel_path),
             thumbnail_size=size)
        
        return str(rel_path)
        
    except Exception as e:
        print(f"Failed to download thumbnail: {e}")
        return None


def _extract_metadata(job: DownloadJob, info: Dict[str, Any]):
    """Extract and store complete metadata."""
    try:
        # Basic video info
        video_id = info.get('id', '')
        title = info.get('title', '')[:510]
        description = info.get('description', '')[:5000]  # Limit description length
        duration = info.get('duration')
        
        # Upload date
        upload_date = None
        upload_date_str = info.get('upload_date')
        if upload_date_str:
            try:
                upload_date = datetime.strptime(upload_date_str, '%Y%m%d').date()
            except ValueError:
                pass
        
        # Channel info
        channel_id = info.get('channel_id', '')
        channel_name = info.get('channel', '') or info.get('uploader', '')
        uploader = info.get('uploader', '')
        uploader_id = info.get('uploader_id', '')
        
        # Engagement metrics
        view_count = info.get('view_count')
        like_count = info.get('like_count')
        dislike_count = info.get('dislike_count')
        comment_count = info.get('comment_count')
        
        # Technical metadata
        width = info.get('width')
        height = info.get('height')
        fps = info.get('fps')
        vcodec = info.get('vcodec', '')
        acodec = info.get('acodec', '')
        
        # Tags and categories
        tags = json.dumps(info.get('tags', []))
        categories = ', '.join(info.get('categories', []))
        
        # Playlist info (if applicable)
        playlist_id = info.get('playlist_id', '')
        playlist_title = info.get('playlist_title', '')
        playlist_uploader = info.get('playlist_uploader', '')
        playlist_index = info.get('playlist_index')
        playlist_count = info.get('playlist_count')
        
        # Update job with metadata
        _set(job,
             video_id=video_id,
             video_title=title,
             video_description=description,
             duration_secs=duration,
             upload_date=upload_date,
             channel_id=channel_id[:64],
             channel_name=channel_name[:255],
             uploader=uploader[:255],
             uploader_id=uploader_id[:64],
             view_count=view_count,
             like_count=like_count,
             dislike_count=dislike_count,
             comment_count=comment_count,
             original_width=width,
             original_height=height,
             fps=fps,
             video_codec=vcodec[:64],
             audio_codec=acodec[:64],
             tags=tags,
             categories=categories[:255],
             playlist_id=playlist_id[:64],
             playlist_title=playlist_title[:512],
             playlist_uploader=playlist_uploader[:255],
             playlist_index=playlist_index,
             playlist_count=playlist_count)
        
    except Exception as e:
        print(f"Failed to extract metadata: {e}")


def _process_job(job_id: str):
    """Process a download job with enhanced error handling and retry logic."""
    job = DownloadJob.objects.get(pk=job_id)
    max_retries = getattr(settings, 'YT_DL_MAX_RETRIES', 3)
    
    try:
        _set(job, status=DownloadJob.Status.RUNNING, message='Starting...', progress_pct=1)
        out_dir = _job_dir(job)
        _set(job, output_dir_rel=join_rel(out_dir.relative_to(settings.MEDIA_ROOT)))
        
        # 1) Pre-fetch metadata
        _progress_update(job, 5, 'Fetching video information...')
        info = None
        ydl_info_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(job.url, download=False)
        
        # Extract and store metadata
        _extract_metadata(job, info)
        
        # Download thumbnail if requested
        want_thumbnail = 'THUMBNAIL' in job.requested_types
        if want_thumbnail:
            _progress_update(job, 10, 'Downloading thumbnail...')
            _download_thumbnail(job, info, out_dir)
        
        # Decide which outputs to produce
        want_mp3 = 'MP3' in job.requested_types
        want_mp4 = 'MP4' in job.requested_types
        want_tx = 'TRANSCRIPT' in job.requested_types
        
        # Calculate progress weights
        steps = []
        if want_mp3:
            steps.append('mp3')
        if want_mp4:
            steps.append('mp4')
        if want_tx:
            steps.append('transcript')
        
        if not steps:
            _set(job, status=DownloadJob.Status.DONE, progress_pct=100, 
                 message='Completed (no media files requested)', finished_at=timezone.now())
            return
        
        step_weight = 80 / len(steps)  # Reserve 20% for metadata and cleanup
        cur_base = 20
        
        def hook(d):
            if d.get('status') == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                done = d.get('downloaded_bytes') or 0
                pct_local = int(done * 100 / total) if total else 50
                _progress_update(job, cur_base + math.floor(pct_local * step_weight / 100), 
                               f'Downloading {d.get("_percent_str", "").strip()}')
            elif d.get('status') == 'finished':
                _progress_update(job, cur_base + int(step_weight * 0.9), 'Post-processing...')
        
        # 2) Download MP3
        if want_mp3:
            _progress_update(job, cur_base + 1, 'Preparing audio download...')
            
            # Determine output filename with fallbacks
            title = job.video_title or info.get('title', '') or 'Unknown_Video'
            video_id = job.video_id or info.get('id', '') or 'unknown_id'
            safe_title = sanitize_filename(title, 80)
            output_template = str(out_dir / f"{safe_title} [{video_id}].%(ext)s")
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': 'bestaudio/best',
                'progress_hooks': [hook],
                'quiet': True,
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            # Apply quality settings
            if job.requested_quality != DownloadJob.Quality.BEST:
                if job.requested_quality == DownloadJob.Quality.WORST:
                    ydl_opts['format'] = 'worstaudio/worst'
                else:
                    # For specific quality, prefer that resolution for video
                    quality_num = job.requested_quality.replace('p', '')
                    ydl_opts['format'] = f'bestaudio[height<={quality_num}]/bestaudio/best'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([job.url])
                
                # Find the output file
                mp3_path = out_dir / f"{safe_title} [{job.video_id}].mp3"
                if mp3_path.exists():
                    rel_path = mp3_path.relative_to(settings.MEDIA_ROOT)
                    size = _bytes(mp3_path)
                    checksum = calculate_file_checksum(mp3_path)
                    _set(job, path_mp3=str(rel_path), size_mp3=size, checksum_mp3=checksum)
            
            cur_base += step_weight
        
        # 3) Download MP4
        if want_mp4:
            _progress_update(job, cur_base + 1, 'Preparing video download...')
            
            # Determine output filename with fallbacks
            title = job.video_title or info.get('title', '') or 'Unknown_Video'
            video_id = job.video_id or info.get('id', '') or 'unknown_id'
            safe_title = sanitize_filename(title, 80)
            output_template = str(out_dir / f"{safe_title} [{video_id}].%(ext)s")
            
            # Quality-based format selection
            format_selector = 'mp4/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
            if job.requested_quality != DownloadJob.Quality.BEST:
                if job.requested_quality == DownloadJob.Quality.WORST:
                    format_selector = 'worst[ext=mp4]/worst'
                else:
                    quality_num = job.requested_quality.replace('p', '')
                    format_selector = f'best[height<={quality_num}][ext=mp4]/best[height<={quality_num}]/best'
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': format_selector,
                'merge_output_format': 'mp4',
                'progress_hooks': [hook],
                'quiet': True,
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([job.url])
                
                # Find the output file
                mp4_path = out_dir / f"{safe_title} [{job.video_id}].mp4"
                if mp4_path.exists():
                    rel_path = mp4_path.relative_to(settings.MEDIA_ROOT)
                    size = _bytes(mp4_path)
                    checksum = calculate_file_checksum(mp4_path)
                    _set(job, path_mp4=str(rel_path), size_mp4=size, checksum_mp4=checksum)
            
            cur_base += step_weight
        
        # 4) Download Transcript with enhanced language support
        if want_tx:
            _progress_update(job, cur_base + 1, 'Fetching transcript...')
            try:
                # Use fallback video_id if job.video_id is not available
                transcript_video_id = job.video_id or info.get('id', '') or 'unknown_id'
                
                # Create API instance
                api = YouTubeTranscriptApi()
                
                # Improved transcript fetching with language fallback
                transcript = None
                transcript_language = 'en'
                
                try:
                    # Get available transcripts
                    _progress_update(job, cur_base + 2, 'Checking available transcripts...')
                    transcript_list = api.list(transcript_video_id)
                    
                    # Preferred language order: English variants first, then any available
                    preferred_languages = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']
                    
                    # Try to find manually created transcripts first, then generated ones
                    transcript_found = False
                    for lang in preferred_languages:
                        try:
                            # Try to fetch transcript in this language
                            transcript = api.fetch(transcript_video_id, [lang])
                            transcript_language = lang
                            transcript_found = True
                            _progress_update(job, cur_base + 5, f'Found transcript in {transcript_language}...')
                            break
                        except NoTranscriptFound:
                            continue
                        except Exception:
                            continue
                    
                    # If no English variants found, try any available language
                    if not transcript_found:
                        try:
                            transcript = api.fetch(transcript_video_id)  # Use default language
                            transcript_language = 'auto'
                            transcript_found = True
                            _progress_update(job, cur_base + 5, f'Found transcript in default language...')
                        except NoTranscriptFound:
                            pass
                        except Exception:
                            pass
                
                except NoTranscriptFound:
                    _set(job, message='No transcripts available for this video.')
                    transcript = None
                except Exception as e:
                    _set(job, message=f'Error accessing transcripts: {str(e)[:100]}...')
                    transcript = None
                
                if transcript:
                    # Determine output filename with fallbacks
                    title = job.video_title or info.get('title', '') or 'Unknown_Video'
                    safe_title = sanitize_filename(title, 80)
                    
                    # Add language indicator to filename if not English
                    lang_suffix = f".{transcript_language}" if transcript_language != 'en' else ""
                    
                    # Timestamped transcript
                    ts_path = out_dir / f"{safe_title} [{transcript_video_id}]{lang_suffix}.timestamped.txt"
                    with ts_path.open('w', encoding='utf-8') as f:
                        f.write(f"# Transcript for: {title}\\n")
                        f.write(f"# Video ID: {transcript_video_id}\\n")
                        f.write(f"# Language: {transcript_language}\\n")
                        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n\\n")
                        
                        for line in transcript:
                            start = getattr(line, 'start', 0.0)
                            text = getattr(line, 'text', '').strip()
                            if text:  # Skip empty lines
                                mm = int(start // 60)
                                ss = int(start % 60)
                                f.write(f"[{mm:02d}:{ss:02d}] {text}\\n")
                    
                    # Plain transcript
                    plain_path = out_dir / f"{safe_title} [{transcript_video_id}]{lang_suffix}.txt"
                    with plain_path.open('w', encoding='utf-8') as f:
                        f.write(f"Transcript for: {title}\\n")
                        f.write(f"Video ID: {transcript_video_id}\\n")
                        f.write(f"Language: {transcript_language}\\n")
                        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n")
                        f.write("-" * 50 + "\\n\\n")
                        
                        for line in transcript:
                            text = getattr(line, 'text', '').strip()
                            if text:  # Skip empty lines
                                f.write(text + " ")
                        f.write("\\n")
                    
                    _set(job,
                         path_txt=str(ts_path.relative_to(settings.MEDIA_ROOT)),
                         size_txt=_bytes(ts_path),
                         path_txt_plain=str(plain_path.relative_to(settings.MEDIA_ROOT)),
                         size_txt_plain=_bytes(plain_path))
                    
                    _progress_update(job, cur_base + int(step_weight * 0.9), f'Transcript saved ({transcript_language})')
                else:
                    _set(job, message='Unable to fetch transcript for this video.')
                
            except NoTranscriptFound:
                _set(job, message='No transcripts available for this video.')
            except AttributeError as e:
                _set(job, message=f'Transcript API error: {str(e)[:100]}...')
            except Exception as e:
                _set(job, message=f'Transcript error: {str(e)[:100]}...')
            
            cur_base += step_weight
        
        # Update user statistics
        _update_user_stats(job.user, success=True)
        
        _set(job, status=DownloadJob.Status.DONE, progress_pct=100, 
             message='Download completed successfully', finished_at=timezone.now())
        
    except Exception as e:
        error_msg = str(e)
        job.refresh_from_db()
        
        # Retry logic
        if job.retry_count < max_retries:
            retry_delay = getattr(settings, 'YT_DL_RETRY_DELAY', 60)
            _set(job, 
                 status=DownloadJob.Status.RETRYING,
                 progress_pct=0,
                 message=f'Retrying in {retry_delay}s... (attempt {job.retry_count + 1}/{max_retries})',
                 error_details=error_msg,
                 retry_count=job.retry_count + 1)
            
            # Schedule retry
            time.sleep(retry_delay)
            enqueue_job(job_id)
        else:
            # Max retries exceeded
            _update_user_stats(job.user, success=False)
            _set(job, 
                 status=DownloadJob.Status.ERROR,
                 progress_pct=100,
                 message=f'Failed after {max_retries} attempts: {error_msg[:200]}...',
                 error_details=error_msg,
                 finished_at=timezone.now())


def _update_user_stats(user, success: bool = True):
    """Update user download statistics."""
    try:
        stats, created = DownloadStats.objects.get_or_create(user=user)
        
        with transaction.atomic():
            stats = DownloadStats.objects.select_for_update().get(user=user)
            stats.total_jobs += 1
            
            if success:
                stats.successful_jobs += 1
            else:
                stats.failed_jobs += 1
            
            stats.last_download = timezone.now()
            if not stats.first_download:
                stats.first_download = timezone.now()
            
            # Recalculate total file size
            total_size = 0
            for job in DownloadJob.objects.filter(user=user, status=DownloadJob.Status.DONE):
                total_size += job.file_size_total or 0
            stats.total_files_size = total_size
            
            stats.save()
            
    except Exception as e:
        print(f"Failed to update user stats: {e}")


def retry_failed_jobs(user, job_ids: list):
    """Retry failed jobs for a user."""
    jobs = DownloadJob.objects.filter(
        user=user,
        id__in=job_ids,
        status__in=[DownloadJob.Status.ERROR, DownloadJob.Status.CANCELLED]
    )
    
    for job in jobs:
        # Reset job state
        _set(job,
             status=DownloadJob.Status.PENDING,
             progress_pct=0,
             message='Queued for retry',
             error_details='',
             retry_count=0,
             finished_at=None)
        
        # Enqueue for processing
        enqueue_job(str(job.id))
    
    return len(jobs)


def cancel_jobs(user, job_ids: list):
    """Cancel running or pending jobs."""
    jobs = DownloadJob.objects.filter(
        user=user,
        id__in=job_ids,
        status__in=[DownloadJob.Status.PENDING, DownloadJob.Status.RUNNING, DownloadJob.Status.RETRYING]
    )
    
    for job in jobs:
        _set(job,
             status=DownloadJob.Status.CANCELLED,
             progress_pct=100,
             message='Cancelled by user',
             finished_at=timezone.now())
    
    return len(jobs)


def cleanup_old_jobs(days: int = 30):
    """Clean up old completed jobs and their files."""
    cutoff_date = timezone.now() - timedelta(days=days)
    old_jobs = DownloadJob.objects.filter(
        finished_at__lt=cutoff_date,
        status__in=[DownloadJob.Status.DONE, DownloadJob.Status.ERROR]
    )
    
    deleted_count = 0
    for job in old_jobs:
        try:
            # Delete associated files
            if job.output_dir_rel:
                output_dir = Path(settings.MEDIA_ROOT) / job.output_dir_rel
                if output_dir.exists():
                    import shutil
                    shutil.rmtree(output_dir)
            
            # Delete job record
            job.delete()
            deleted_count += 1
            
        except Exception as e:
            print(f"Failed to cleanup job {job.id}: {e}")
    
    return deleted_count
'''
            
            tasks_file = self.project_dir / 'app_ytdl_simple' / 'tasks.py'
            logger.debug(f"Writing enhanced tasks to: {tasks_file}")
            write_file_content(tasks_file, tasks_content)
            
            logger.info("✓ Enhanced background tasks created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create enhanced tasks: {e}")
            return False
    
    def create_enhanced_views(self) -> bool:
        """
        Create enhanced views with dashboard, API endpoints, and interactive features.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Enhanced Views ===")
        
        try:
            views_content = '''import json
import yt_dlp
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, FileResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView
from pathlib import Path

from .forms import DownloadBatchForm, JobSearchForm
from .models import DownloadJob, DownloadStats
from .tasks import enqueue_job, retry_failed_jobs, cancel_jobs
from .utils import media_base_for, join_rel, format_file_size


@method_decorator(login_required, name='dispatch')
class DashboardView(ListView):
    """Enhanced dashboard view with statistics and recent activity."""
    
    model = DownloadJob
    template_name = 'app_ytdl_simple/dashboard.html'
    context_object_name = 'recent_jobs'
    paginate_by = 10
    
    def get_queryset(self):
        return (DownloadJob.objects
                .filter(user=self.request.user)
                .order_by('-created_at')
                .select_related()[:10])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create user stats
        stats, created = DownloadStats.objects.get_or_create(user=user)
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_jobs = DownloadJob.objects.filter(
            user=user,
            created_at__gte=week_ago
        )
        
        # Status breakdown
        status_counts = DownloadJob.objects.filter(user=user).values('status').annotate(
            count=Count('id')
        )
        status_dict = {item['status']: item['count'] for item in status_counts}
        
        # File type breakdown
        type_stats = {
            'mp3': DownloadJob.objects.filter(user=user).exclude(path_mp3='').count(),
            'mp4': DownloadJob.objects.filter(user=user).exclude(path_mp4='').count(),
            'transcript': DownloadJob.objects.filter(user=user).exclude(path_txt='').count(),
            'thumbnail': DownloadJob.objects.filter(user=user).exclude(thumbnail_path='').count(),
        }
        
        # Active jobs (currently running)
        active_jobs = DownloadJob.objects.filter(
            user=user,
            status__in=[DownloadJob.Status.PENDING, DownloadJob.Status.RUNNING, DownloadJob.Status.RETRYING]
        ).count()
        
        context.update({
            'stats': stats,
            'status_counts': status_dict,
            'type_stats': type_stats,
            'active_jobs': active_jobs,
            'recent_jobs_count': recent_jobs.count(),
            'week_downloads': recent_jobs.filter(status=DownloadJob.Status.DONE).count(),
        })
        
        return context


@login_required
def job_form(request):
    """Enhanced job creation form with playlist expansion and validation."""
    if request.method == 'POST':
        form = DownloadBatchForm(request.POST)
        if form.is_valid():
            urls = form.cleaned_data['urls_list']
            want_mp3 = form.cleaned_data['want_mp3']
            want_mp4 = form.cleaned_data['want_mp4']
            want_tx = form.cleaned_data['want_transcript']
            want_thumb = form.cleaned_data['want_thumbnail']
            quality = form.cleaned_data['quality']
            subfolder = form.cleaned_data['subfolder']
            organize_by_channel = form.cleaned_data['organize_by_channel']
            organize_by_date = form.cleaned_data['organize_by_date']
            
            # Build requested types string
            req_types = []
            if want_mp3:
                req_types.append('MP3')
            if want_mp4:
                req_types.append('MP4')
            if want_tx:
                req_types.append('TRANSCRIPT')
            if want_thumb:
                req_types.append('THUMBNAIL')
            req_types_str = ','.join(req_types)
            
            created = 0
            expanded = []
            
            # Expand playlists into video URLs
            for url in urls:
                try:
                    with yt_dlp.YoutubeDL({
                        'quiet': True,
                        'extract_flat': True,
                        'skip_download': True
                    }) as ydl:
                        info = ydl.extract_info(url, download=False)
                    
                    if info and 'entries' in info:
                        # Playlist/channel: collect each entry's URL
                        for entry in info['entries']:
                            vid = entry.get('url') or entry.get('id')
                            if vid and not vid.startswith('http'):
                                expanded.append(f"https://www.youtube.com/watch?v={vid}")
                            elif vid:
                                expanded.append(vid)
                    else:
                        expanded.append(url)
                except Exception:
                    expanded.append(url)  # Fallback: treat as single video
            
            # Create jobs
            for u in expanded:
                job = DownloadJob.objects.create(
                    user=request.user,
                    url=u,
                    requested_types=req_types_str,
                    requested_quality=quality,
                    custom_subfolder=subfolder,
                )
                
                # Set organization flags (we'll store these as custom attributes)
                if organize_by_channel:
                    job.organize_by_channel = True
                if organize_by_date:
                    job.organize_by_date = True
                
                enqueue_job(str(job.id))
                created += 1
            
            return redirect('app_ytdl_simple:dashboard')
    else:
        form = DownloadBatchForm()
    
    return render(request, 'app_ytdl_simple/job_form.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class JobListView(ListView):
    """Enhanced job list with filtering and search."""
    
    model = DownloadJob
    template_name = 'app_ytdl_simple/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = DownloadJob.objects.filter(user=self.request.user)
        
        # Apply search filters
        form = JobSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            status = form.cleaned_data.get('status')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            output_type = form.cleaned_data.get('output_type')
            
            if query:
                queryset = queryset.filter(
                    Q(video_title__icontains=query) |
                    Q(channel_name__icontains=query) |
                    Q(url__icontains=query)
                )
            
            if status:
                queryset = queryset.filter(status=status)
            
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
            
            if output_type:
                if output_type == 'mp3':
                    queryset = queryset.exclude(path_mp3='')
                elif output_type == 'mp4':
                    queryset = queryset.exclude(path_mp4='')
                elif output_type == 'transcript':
                    queryset = queryset.exclude(path_txt='')
                elif output_type == 'thumbnail':
                    queryset = queryset.exclude(thumbnail_path='')
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm(self.request.GET)
        return context


@login_required
def job_detail(request, pk):
    """Enhanced job detail view with metadata and download options."""
    job = get_object_or_404(DownloadJob, user=request.user, pk=pk)
    
    # Parse tags from JSON
    tags = []
    if job.tags:
        try:
            tags = json.loads(job.tags)
        except json.JSONDecodeError:
            pass
    
    context = {
        'job': job,
        'tags': tags,
        'available_downloads': job.available_downloads,
    }
    
    return render(request, 'app_ytdl_simple/job_detail.html', context)


@login_required
def job_status_json(request, pk):
    """API endpoint for job status updates."""
    job = get_object_or_404(DownloadJob, user=request.user, pk=pk)
    
    data = {
        'id': str(job.id),
        'status': job.status,
        'progress_pct': job.progress_pct,
        'message': job.message,
        'video_title': job.video_title,
        'duration_formatted': job.duration_formatted,
        'file_size_total': job.file_size_total,
        'available_downloads': job.available_downloads,
        'finished_at': job.finished_at.isoformat() if job.finished_at else None,
    }
    
    return JsonResponse(data)


@login_required
def download_artifact(request, pk, kind: str):
    """Secure file download endpoint."""
    job = get_object_or_404(DownloadJob, user=request.user, pk=pk)
    
    path_mapping = {
        'mp3': job.path_mp3,
        'mp4': job.path_mp4,
        'txt': job.path_txt,
        'txt_plain': job.path_txt_plain,
        'thumbnail': job.thumbnail_path,
    }
    
    rel_path = path_mapping.get(kind)
    if not rel_path:
        raise Http404("File not found")
    
    file_path = Path(settings.MEDIA_ROOT) / rel_path
    if not file_path.exists():
        raise Http404("File not found")
    
    return FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=file_path.name
    )


@login_required
@require_http_methods(["POST"])
def job_retry(request, pk):
    """Retry a failed job."""
    job = get_object_or_404(DownloadJob, user=request.user, pk=pk)
    
    if job.status not in [DownloadJob.Status.ERROR, DownloadJob.Status.CANCELLED]:
        return JsonResponse({'error': 'Job cannot be retried'}, status=400)
    
    # Reset job and enqueue
    retry_count = retry_failed_jobs(request.user, [str(job.id)])
    
    return JsonResponse({
        'success': True,
        'message': f'Job queued for retry',
        'job_id': str(job.id)
    })


@login_required
@require_http_methods(["POST"])
def job_cancel(request, pk):
    """Cancel a running job."""
    job = get_object_or_404(DownloadJob, user=request.user, pk=pk)
    
    if job.status not in [DownloadJob.Status.PENDING, DownloadJob.Status.RUNNING, DownloadJob.Status.RETRYING]:
        return JsonResponse({'error': 'Job cannot be cancelled'}, status=400)
    
    cancel_count = cancel_jobs(request.user, [str(job.id)])
    
    return JsonResponse({
        'success': True,
        'message': f'Job cancelled',
        'job_id': str(job.id)
    })


@login_required
@require_http_methods(["POST"])
def bulk_action(request):
    """Handle bulk actions on jobs."""
    try:
        data = json.loads(request.body)
        action = data.get('action')
        job_ids = data.get('job_ids', [])
        
        if not job_ids:
            return JsonResponse({'error': 'No jobs selected'}, status=400)
        
        # Verify all jobs belong to the user
        user_jobs = DownloadJob.objects.filter(
            user=request.user,
            id__in=job_ids
        ).values_list('id', flat=True)
        
        valid_job_ids = [str(job_id) for job_id in user_jobs]
        
        if action == 'retry':
            count = retry_failed_jobs(request.user, valid_job_ids)
            message = f'Queued {count} jobs for retry'
        elif action == 'cancel':
            count = cancel_jobs(request.user, valid_job_ids)
            message = f'Cancelled {count} jobs'
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'count': count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def user_stats(request):
    """User statistics page."""
    user = request.user
    stats, created = DownloadStats.objects.get_or_create(user=user)
    
    # Additional statistics
    jobs = DownloadJob.objects.filter(user=user)
    
    # Daily download counts (last 30 days)
    daily_stats = []
    for i in range(30):
        date = timezone.now().date() - timedelta(days=i)
        count = jobs.filter(created_at__date=date, status=DownloadJob.Status.DONE).count()
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    daily_stats.reverse()
    
    # Channel breakdown (top 10)
    channel_stats = (jobs.exclude(channel_name='')
                    .values('channel_name')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10])
    
    # File type breakdown with sizes
    type_breakdown = {
        'mp3': {
            'count': jobs.exclude(path_mp3='').count(),
            'total_size': jobs.exclude(path_mp3='').aggregate(Sum('size_mp3'))['size_mp3__sum'] or 0
        },
        'mp4': {
            'count': jobs.exclude(path_mp4='').count(),
            'total_size': jobs.exclude(path_mp4='').aggregate(Sum('size_mp4'))['size_mp4__sum'] or 0
        },
        'transcript': {
            'count': jobs.exclude(path_txt='').count(),
            'total_size': jobs.exclude(path_txt='').aggregate(Sum('size_txt'))['size_txt__sum'] or 0
        }
    }
    
    context = {
        'stats': stats,
        'daily_stats': daily_stats,
        'channel_stats': channel_stats,
        'type_breakdown': type_breakdown,
        'total_duration': jobs.aggregate(Sum('duration_secs'))['duration_secs__sum'] or 0,
    }
    
    return render(request, 'app_ytdl_simple/stats.html', context)


@login_required
def api_queue_status(request):
    """API endpoint for queue status."""
    user = request.user
    
    # Active jobs
    active_jobs = DownloadJob.objects.filter(
        user=user,
        status__in=[DownloadJob.Status.PENDING, DownloadJob.Status.RUNNING, DownloadJob.Status.RETRYING]
    ).values('id', 'video_title', 'status', 'progress_pct', 'message')
    
    # Recent completed jobs
    recent_completed = DownloadJob.objects.filter(
        user=user,
        status=DownloadJob.Status.DONE,
        finished_at__gte=timezone.now() - timedelta(hours=1)
    ).values('id', 'video_title', 'finished_at')
    
    return JsonResponse({
        'active_jobs': list(active_jobs),
        'recent_completed': list(recent_completed),
        'queue_length': len(active_jobs)
    })
'''
            
            views_file = self.project_dir / 'app_ytdl_simple' / 'views.py'
            logger.debug(f"Writing enhanced views to: {views_file}")
            write_file_content(views_file, views_content)
            
            logger.info("✓ Enhanced views created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create enhanced views: {e}")
            return False
    
    def create_app_urls(self) -> bool:
        """
        Create URL configuration for the YouTube downloader app.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating App URLs ===")
        
        try:
            urls_content = '''from django.urls import path
from .views import (
    DashboardView, job_form, JobListView, job_detail, job_status_json,
    download_artifact, job_retry, job_cancel, bulk_action, user_stats,
    api_queue_status
)

app_name = 'app_ytdl_simple'

urlpatterns = [
    # Dashboard and main interface
    path('', DashboardView.as_view(), name='dashboard'),
    path('new/', job_form, name='job_form'),
    
    # Job management
    path('jobs/', JobListView.as_view(), name='job_list'),
    path('jobs/<uuid:pk>/', job_detail, name='job_detail'),
    path('jobs/<uuid:pk>/retry/', job_retry, name='job_retry'),
    path('jobs/<uuid:pk>/cancel/', job_cancel, name='job_cancel'),
    
    # File downloads
    path('jobs/<uuid:pk>/download/<str:kind>/', download_artifact, name='job_download'),
    
    # API endpoints
    path('jobs/<uuid:pk>/status.json', job_status_json, name='job_status_json'),
    path('api/queue-status/', api_queue_status, name='api_queue_status'),
    path('api/bulk-action/', bulk_action, name='bulk_action'),
    
    # Statistics
    path('stats/', user_stats, name='stats'),
]
'''
            
            urls_file = self.project_dir / 'app_ytdl_simple' / 'urls.py'
            logger.debug(f"Writing app URLs to: {urls_file}")
            write_file_content(urls_file, urls_content)
            
            logger.info("✓ App URLs created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create app URLs: {e}")
            return False
    
    def create_admin_interface(self) -> bool:
        """
        Create Django admin interface for the YouTube downloader.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Admin Interface ===")
        
        try:
            admin_content = '''from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import DownloadJob, DownloadStats


@admin.register(DownloadJob)
class DownloadJobAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'video_title_short', 'status', 'progress_pct',
        'created_at', 'file_size_display', 'download_links'
    ]
    list_filter = [
        'status', 'created_at', 'requested_quality',
        'upload_date', 'finished_at'
    ]
    search_fields = [
        'video_title', 'channel_name', 'video_id', 'url',
        'user__username', 'user__email'
    ]
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'finished_at',
        'video_metadata_display', 'file_paths_display',
        'error_details_display'
    ]
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'url', 'status', 'created_at', 'updated_at', 'finished_at')
        }),
        ('Request Configuration', {
            'fields': ('requested_types', 'requested_quality', 'custom_subfolder'),
        }),
        ('Progress & Status', {
            'fields': ('progress_pct', 'message', 'retry_count', 'error_details_display'),
        }),
        ('Video Metadata', {
            'fields': ('video_metadata_display',),
            'classes': ('collapse',)
        }),
        ('Files & Outputs', {
            'fields': ('output_dir_rel', 'file_paths_display'),
            'classes': ('collapse',)
        }),
    )
    
    def video_title_short(self, obj):
        if obj.video_title:
            return obj.video_title[:50] + ('...' if len(obj.video_title) > 50 else '')
        return obj.url[:50] + ('...' if len(obj.url) > 50 else '')
    video_title_short.short_description = 'Title'
    
    def file_size_display(self, obj):
        total_size = obj.file_size_total
        if total_size:
            if total_size < 1024 * 1024:  # Less than 1MB
                return f"{total_size / 1024:.1f} KB"
            elif total_size < 1024 * 1024 * 1024:  # Less than 1GB
                return f"{total_size / (1024 * 1024):.1f} MB"
            else:
                return f"{total_size / (1024 * 1024 * 1024):.1f} GB"
        return "-"
    file_size_display.short_description = 'Total Size'
    
    def download_links(self, obj):
        links = []
        downloads = obj.available_downloads
        for kind, label, size in downloads:
            url = reverse('app_ytdl_simple:job_download', args=[obj.id, kind])
            links.append(f'<a href="{url}" target="_blank">{label}</a>')
        return mark_safe(' | '.join(links)) if links else '-'
    download_links.short_description = 'Downloads'
    
    def video_metadata_display(self, obj):
        metadata = []
        if obj.video_id:
            metadata.append(f"<strong>Video ID:</strong> {obj.video_id}")
        if obj.channel_name:
            metadata.append(f"<strong>Channel:</strong> {obj.channel_name}")
        if obj.duration_secs:
            metadata.append(f"<strong>Duration:</strong> {obj.duration_formatted}")
        if obj.view_count:
            metadata.append(f"<strong>Views:</strong> {obj.view_count:,}")
        if obj.like_count:
            metadata.append(f"<strong>Likes:</strong> {obj.like_count:,}")
        if obj.upload_date:
            metadata.append(f"<strong>Upload Date:</strong> {obj.upload_date}")
        if obj.original_width and obj.original_height:
            metadata.append(f"<strong>Resolution:</strong> {obj.original_width}x{obj.original_height}")
        
        return mark_safe('<br>'.join(metadata)) if metadata else 'No metadata available'
    video_metadata_display.short_description = 'Video Metadata'
    
    def file_paths_display(self, obj):
        paths = []
        if obj.path_mp3:
            size = f" ({obj.size_mp3:,} bytes)" if obj.size_mp3 else ""
            paths.append(f"<strong>MP3:</strong> {obj.path_mp3}{size}")
        if obj.path_mp4:
            size = f" ({obj.size_mp4:,} bytes)" if obj.size_mp4 else ""
            paths.append(f"<strong>MP4:</strong> {obj.path_mp4}{size}")
        if obj.path_txt:
            size = f" ({obj.size_txt:,} bytes)" if obj.size_txt else ""
            paths.append(f"<strong>Transcript:</strong> {obj.path_txt}{size}")
        if obj.thumbnail_path:
            size = f" ({obj.thumbnail_size:,} bytes)" if obj.thumbnail_size else ""
            paths.append(f"<strong>Thumbnail:</strong> {obj.thumbnail_path}{size}")
        
        return mark_safe('<br>'.join(paths)) if paths else 'No files generated'
    file_paths_display.short_description = 'Generated Files'
    
    def error_details_display(self, obj):
        if obj.error_details:
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', obj.error_details)
        return 'No errors'
    error_details_display.short_description = 'Error Details'
    
    actions = ['retry_selected_jobs', 'cancel_selected_jobs', 'cleanup_selected_jobs']
    
    def retry_selected_jobs(self, request, queryset):
        failed_jobs = queryset.filter(status__in=[DownloadJob.Status.ERROR, DownloadJob.Status.CANCELLED])
        count = 0
        for job in failed_jobs:
            from .tasks import enqueue_job
            job.status = DownloadJob.Status.PENDING
            job.progress_pct = 0
            job.message = 'Queued for retry (admin action)'
            job.retry_count = 0
            job.save()
            enqueue_job(str(job.id))
            count += 1
        self.message_user(request, f'Queued {count} jobs for retry.')
    retry_selected_jobs.short_description = 'Retry selected failed jobs'
    
    def cancel_selected_jobs(self, request, queryset):
        active_jobs = queryset.filter(status__in=[
            DownloadJob.Status.PENDING, DownloadJob.Status.RUNNING, DownloadJob.Status.RETRYING
        ])
        count = active_jobs.update(
            status=DownloadJob.Status.CANCELLED,
            progress_pct=100,
            message='Cancelled by admin'
        )
        self.message_user(request, f'Cancelled {count} jobs.')
    cancel_selected_jobs.short_description = 'Cancel selected active jobs'
    
    def cleanup_selected_jobs(self, request, queryset):
        from pathlib import Path
        from django.conf import settings
        import shutil
        
        count = 0
        for job in queryset:
            try:
                if job.output_dir_rel:
                    output_dir = Path(settings.MEDIA_ROOT) / job.output_dir_rel
                    if output_dir.exists():
                        shutil.rmtree(output_dir)
                job.delete()
                count += 1
            except Exception as e:
                self.message_user(request, f'Error cleaning up job {job.id}: {e}', level='ERROR')
        
        self.message_user(request, f'Cleaned up {count} jobs and their files.')
    cleanup_selected_jobs.short_description = 'Delete selected jobs and files'


@admin.register(DownloadStats)
class DownloadStatsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'total_jobs', 'successful_jobs', 'failed_jobs',
        'success_rate_display', 'storage_formatted', 'last_download'
    ]
    list_filter = ['last_download', 'first_download']
    search_fields = ['user__username', 'user__email']
    readonly_fields = [
        'total_jobs', 'successful_jobs', 'failed_jobs',
        'total_files_size', 'first_download', 'last_download', 'updated_at'
    ]
    
    def success_rate_display(self, obj):
        rate = obj.success_rate
        color = 'green' if rate >= 90 else 'orange' if rate >= 70 else 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, rate)
    success_rate_display.short_description = 'Success Rate'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Register models for better admin display
admin.site.site_header = "YouTube Downloader Administration"
admin.site.site_title = "YT-DL Admin"
admin.site.index_title = "Manage Downloads"
'''
            
            admin_file = self.project_dir / 'app_ytdl_simple' / 'admin.py'
            logger.debug(f"Writing admin interface to: {admin_file}")
            write_file_content(admin_file, admin_content)
            
            logger.info("✓ Admin interface created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create admin interface: {e}")
            return False
    
    def create_enhanced_templates(self) -> bool:
        """
        Create enhanced templates with modern UI and interactive features.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Enhanced Templates ===")
        
        try:
            # Find app name from config
            config = self.load_config()
            app_name = config.get('STARTAPP_NAME', 'app_nineteen_o_six')
            
            # Base dashboard template
            dashboard_template = '''{% extends "''' + app_name + '''/base.html" %}
{% load static %}

{% block content %}
<div class="ytdl-dashboard">
    <!-- Header with stats -->
    <div class="dashboard-header">
        <h1>YouTube Downloader</h1>
        <div class="quick-stats">
            <div class="stat-card">
                <h3>{{ stats.total_jobs }}</h3>
                <p>Total Downloads</p>
            </div>
            <div class="stat-card">
                <h3>{{ active_jobs }}</h3>
                <p>Active Jobs</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.storage_formatted }}</h3>
                <p>Storage Used</p>
            </div>
            <div class="stat-card success">
                <h3>{{ stats.success_rate|floatformat:1 }}%</h3>
                <p>Success Rate</p>
            </div>
        </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
        <a href="{% url 'app_ytdl_simple:job_form' %}" class="btn btn-primary">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>
            New Download
        </a>
        <a href="{% url 'app_ytdl_simple:job_list' %}" class="btn btn-secondary">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M3 2.5a2.5 2.5 0 0 1 5 0V3h4.5a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5H3V2.5zm1 .5v3h8V3H4zm7 4H5v5h6V7z"/>
            </svg>
            View All Jobs
        </a>
        <a href="{% url 'app_ytdl_simple:stats' %}" class="btn btn-outline">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                <path d="M4 11H2v3h2v-3zm5-4H7v7h2V7zm5-5v12h-2V2h2zm-2-1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1h-2zM6 7a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7zm-5 4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1v-3z"/>
            </svg>
            Statistics
        </a>
    </div>

    <!-- Active Downloads -->
    {% if active_jobs > 0 %}
    <div class="active-downloads">
        <h2>Active Downloads</h2>
        <div id="active-jobs" class="job-list">
            <!-- Will be populated by JavaScript -->
        </div>
    </div>
    {% endif %}

    <!-- Recent Activity -->
    <div class="recent-activity">
        <h2>Recent Downloads</h2>
        {% if recent_jobs %}
            <div class="job-grid">
                {% for job in recent_jobs %}
                <div class="job-card status-{{ job.status|lower }}">
                    {% if job.thumbnail_url %}
                        <img src="{{ job.thumbnail_url }}" alt="Thumbnail" class="job-thumbnail">
                    {% endif %}
                    <div class="job-info">
                        <h3>{{ job.video_title|default:job.url|truncatechars:50 }}</h3>
                        <p class="job-meta">
                            {% if job.channel_name %}{{ job.channel_name }} • {% endif %}
                            {{ job.created_at|timesince }} ago
                        </p>
                        <div class="job-status">
                            <span class="status-badge status-{{ job.status|lower }}">{{ job.get_status_display }}</span>
                            {% if job.status == 'RUNNING' %}
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {{ job.progress_pct }}%"></div>
                                </div>
                            {% endif %}
                        </div>
                        <div class="job-actions">
                            <a href="{% url 'app_ytdl_simple:job_detail' job.id %}" class="btn btn-sm">View</a>
                            {% for kind, label, size in job.available_downloads %}
                                <a href="{% url 'app_ytdl_simple:job_download' job.id kind %}" class="btn btn-sm btn-download">{{ label }}</a>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="empty-state">
                <svg width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M14.5 3a.5.5 0 0 1 .5.5v9a.5.5 0 0 1-.5.5h-13a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h13zm-13-1A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h13a1.5 1.5 0 0 0 1.5-1.5v-9A1.5 1.5 0 0 0 14.5 2h-13z"/>
                    <path d="M7 6.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1h-4a.5.5 0 0 1-.5-.5zm-1.5 3a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm0 3a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm2-9a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5z"/>
                </svg>
                <h3>No downloads yet</h3>
                <p>Start by downloading your first video!</p>
                <a href="{% url 'app_ytdl_simple:job_form' %}" class="btn btn-primary">Get Started</a>
            </div>
        {% endif %}
    </div>
</div>

<script>
// Auto-refresh active jobs
if ({{ active_jobs }} > 0) {
    setInterval(updateActiveJobs, 3000);
}

function updateActiveJobs() {
    fetch('{% url "app_ytdl_simple:api_queue_status" %}')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('active-jobs');
            if (!container) return;
            
            container.innerHTML = data.active_jobs.map(job => `
                <div class="job-item status-${job.status.toLowerCase()}">
                    <div class="job-info">
                        <h4>${job.video_title || 'Processing...'}</h4>
                        <span class="status">${job.status}</span>
                    </div>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${job.progress_pct}%"></div>
                        <span class="progress-text">${job.progress_pct}%</span>
                    </div>
                    <p class="job-message">${job.message}</p>
                </div>
            `).join('');
            
            // Refresh page if no active jobs remain
            if (data.active_jobs.length === 0) {
                setTimeout(() => location.reload(), 2000);
            }
        })
        .catch(error => console.error('Error updating jobs:', error));
}
</script>
{% endblock %}
'''
            
            # Job form template
            job_form_template = '''{% extends "''' + app_name + '''/base.html" %}
{% load static %}

{% block content %}
<div class="ytdl-form-page">
    <div class="form-header">
        <h1>New Download</h1>
        <p>Download videos, playlists, or entire channels from YouTube</p>
    </div>

    <form method="post" class="ytdl-form">
        {% csrf_token %}
        
        <!-- URL Input -->
        <div class="form-group">
            <label for="{{ form.urls.id_for_label }}">{{ form.urls.label }}</label>
            {{ form.urls }}
            <div class="form-help">{{ form.urls.help_text }}</div>
            {% if form.urls.errors %}
                <div class="form-errors">
                    {% for error in form.urls.errors %}
                        <span class="error">{{ error }}</span>
                    {% endfor %}
                </div>
            {% endif %}
        </div>

        <!-- Output Selection -->
        <div class="form-group">
            <label>Output Types</label>
            <div class="checkbox-group">
                <label class="checkbox-item">
                    {{ form.want_mp3 }}
                    <span class="checkmark"></span>
                    <span class="label-text">{{ form.want_mp3.label }}</span>
                    <small>Audio only (192kbps MP3)</small>
                </label>
                <label class="checkbox-item">
                    {{ form.want_mp4 }}
                    <span class="checkmark"></span>
                    <span class="label-text">{{ form.want_mp4.label }}</span>
                    <small>Full video with audio</small>
                </label>
                <label class="checkbox-item">
                    {{ form.want_transcript }}
                    <span class="checkmark"></span>
                    <span class="label-text">{{ form.want_transcript.label }}</span>
                    <small>Text transcription (English only)</small>
                </label>
                <label class="checkbox-item">
                    {{ form.want_thumbnail }}
                    <span class="checkmark"></span>
                    <span class="label-text">{{ form.want_thumbnail.label }}</span>
                    <small>Video thumbnail image</small>
                </label>
            </div>
        </div>

        <!-- Quality Selection -->
        <div class="form-group">
            <label for="{{ form.quality.id_for_label }}">{{ form.quality.label }}</label>
            {{ form.quality }}
            <div class="form-help">{{ form.quality.help_text }}</div>
        </div>

        <!-- Organization Options -->
        <div class="form-group">
            <label>Organization</label>
            <div class="form-row">
                <div class="form-col">
                    <label for="{{ form.subfolder.id_for_label }}">{{ form.subfolder.label }}</label>
                    {{ form.subfolder }}
                    <div class="form-help">{{ form.subfolder.help_text }}</div>
                </div>
            </div>
            <div class="checkbox-group">
                <label class="checkbox-item">
                    {{ form.organize_by_channel }}
                    <span class="checkmark"></span>
                    <span class="label-text">{{ form.organize_by_channel.label }}</span>
                    <small>{{ form.organize_by_channel.help_text }}</small>
                </label>
                <label class="checkbox-item">
                    {{ form.organize_by_date }}
                    <span class="checkmark"></span>
                    <span class="label-text">{{ form.organize_by_date.label }}</span>
                    <small>{{ form.organize_by_date.help_text }}</small>
                </label>
            </div>
        </div>

        <!-- Form Actions -->
        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-lg">
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                    <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                    <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
                </svg>
                Create Download Jobs
            </button>
            <a href="{% url 'app_ytdl_simple:dashboard' %}" class="btn btn-secondary">Cancel</a>
        </div>

        {% if form.non_field_errors %}
            <div class="form-errors">
                {% for error in form.non_field_errors %}
                    <span class="error">{{ error }}</span>
                {% endfor %}
            </div>
        {% endif %}
    </form>
</div>

<script>
// Form validation and preview
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.ytdl-form');
    const urlTextarea = document.getElementById('{{ form.urls.id_for_label }}');
    
    // Auto-resize textarea
    urlTextarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.max(120, this.scrollHeight) + 'px';
    });
    
    // Form submission feedback
    form.addEventListener('submit', function(e) {
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> Processing URLs...';
    });
});
</script>
{% endblock %}
'''
            
            # CSS styles
            css_content = '''/* YouTube Downloader App Styles */

/* Dashboard */
.ytdl-dashboard {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
}

.dashboard-header {
    margin-bottom: 2rem;
}

.dashboard-header h1 {
    margin: 0 0 1rem 0;
    color: #333;
}

.quick-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-card.success {
    border-color: #10b981;
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
}

.stat-card h3 {
    margin: 0 0 0.5rem 0;
    font-size: 2rem;
    font-weight: 700;
    color: #1f2937;
}

.stat-card p {
    margin: 0;
    color: #6b7280;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Quick Actions */
.quick-actions {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}

.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 0.5rem;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.875rem;
}

.btn-primary {
    background: #3b82f6;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
}

.btn-secondary {
    background: #6b7280;
    color: white;
}

.btn-secondary:hover {
    background: #4b5563;
}

.btn-outline {
    background: transparent;
    color: #3b82f6;
    border: 1px solid #3b82f6;
}

.btn-outline:hover {
    background: #3b82f6;
    color: white;
}

.btn-sm {
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
}

.btn-lg {
    padding: 1rem 2rem;
    font-size: 1rem;
}

/* Job Cards */
.job-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
}

.job-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
}

.job-card:hover {
    transform: translateY(-2px);
}

.job-thumbnail {
    width: 100%;
    height: 180px;
    object-fit: cover;
}

.job-info {
    padding: 1rem;
}

.job-info h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    line-height: 1.4;
    color: #1f2937;
}

.job-meta {
    margin: 0 0 1rem 0;
    color: #6b7280;
    font-size: 0.875rem;
}

.job-status {
    margin-bottom: 1rem;
}

.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-pending {
    background: #fef3c7;
    color: #92400e;
}

.status-running {
    background: #dbeafe;
    color: #1e40af;
}

.status-done {
    background: #d1fae5;
    color: #065f46;
}

.status-error {
    background: #fee2e2;
    color: #991b1b;
}

.progress-bar {
    width: 100%;
    height: 4px;
    background: #e5e7eb;
    border-radius: 2px;
    margin-top: 0.5rem;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: #3b82f6;
    transition: width 0.3s ease;
}

.job-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.btn-download {
    background: #10b981;
    color: white;
}

.btn-download:hover {
    background: #059669;
}

/* Form Styles */
.ytdl-form-page {
    max-width: 600px;
    margin: 0 auto;
    padding: 1rem;
}

.form-header {
    text-align: center;
    margin-bottom: 2rem;
}

.form-header h1 {
    margin: 0 0 0.5rem 0;
    color: #1f2937;
}

.form-header p {
    margin: 0;
    color: #6b7280;
}

.ytdl-form {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #374151;
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    font-size: 1rem;
    transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
    min-height: 120px;
    resize: vertical;
    font-family: monospace;
}

.form-help {
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #6b7280;
}

.form-errors {
    margin-top: 0.5rem;
}

.form-errors .error {
    display: block;
    color: #dc2626;
    font-size: 0.875rem;
    margin-bottom: 0.25rem;
}

.checkbox-group {
    display: grid;
    gap: 0.75rem;
}

.checkbox-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    cursor: pointer;
    padding: 0.75rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    transition: all 0.2s;
}

.checkbox-item:hover {
    border-color: #3b82f6;
    background: #f8fafc;
}

.checkbox-item input[type="checkbox"] {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
}

.checkmark {
    width: 20px;
    height: 20px;
    border: 2px solid #d1d5db;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    flex-shrink: 0;
}

.checkbox-item input:checked + .checkmark {
    background: #3b82f6;
    border-color: #3b82f6;
}

.checkbox-item input:checked + .checkmark::after {
    content: "✓";
    color: white;
    font-size: 14px;
    font-weight: bold;
}

.label-text {
    font-weight: 500;
    color: #1f2937;
}

.checkbox-item small {
    display: block;
    color: #6b7280;
    font-size: 0.75rem;
    margin-top: 0.25rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
}

.form-actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e5e7eb;
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #6b7280;
}

.empty-state svg {
    margin-bottom: 1rem;
    color: #d1d5db;
}

.empty-state h3 {
    margin: 0 0 0.5rem 0;
    color: #374151;
}

.empty-state p {
    margin: 0 0 1.5rem 0;
}

/* Spinner */
.spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid #ffffff33;
    border-top: 2px solid #ffffff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
    .quick-stats {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .job-grid {
        grid-template-columns: 1fr;
    }
    
    .quick-actions {
        flex-direction: column;
    }
    
    .form-actions {
        flex-direction: column;
    }
}
'''
            
            template_dir = self.project_dir / 'app_ytdl_simple' / 'templates' / 'app_ytdl_simple'
            static_css_dir = self.project_dir / 'app_ytdl_simple' / 'static' / 'app_ytdl_simple' / 'css'
            
            # Job list template
            job_list_template = '''{% extends "''' + app_name + '''/base.html" %}
{% load static %}

{% block title %}YouTube Downloads - Job List{% endblock %}

{% block extra_css %}
<link rel="stylesheet" type="text/css" href="{% static 'app_ytdl_simple/css/style.css' %}">
{% endblock %}

{% block content %}
<div class="container">
    <div class="header-section">
        <h1>📥 Download Jobs</h1>
        <p class="subtitle">Manage your YouTube download jobs</p>
    </div>

    <div class="action-bar">
        <a href="{% url 'app_ytdl_simple:dashboard' %}" class="btn btn-secondary">← Back to Dashboard</a>
        <a href="{% url 'app_ytdl_simple:job_form' %}" class="btn btn-primary">+ New Download</a>
    </div>

    {% if jobs %}
        <div class="jobs-grid">
            {% for job in jobs %}
                <div class="job-card" data-status="{{ job.status }}">
                    <div class="job-header">
                        <div class="job-title">
                            {% if job.thumbnail_url %}
                                <img src="{{ job.thumbnail_url }}" alt="Thumbnail" class="job-thumbnail">
                            {% endif %}
                            <div class="job-info">
                                <h3>{{ job.video_title|default:"Processing..." }}</h3>
                                <p class="job-url">{{ job.url|truncatechars:60 }}</p>
                            </div>
                        </div>
                        <div class="job-status">
                            <span class="status-badge status-{{ job.status }}">{{ job.get_status_display }}</span>
                        </div>
                    </div>

                    <div class="job-details">
                        <div class="job-meta">
                            <span class="meta-item">
                                <strong>Types:</strong> {{ job.requested_types }}
                            </span>
                            <span class="meta-item">
                                <strong>Quality:</strong> {{ job.get_requested_quality_display }}
                            </span>
                            <span class="meta-item">
                                <strong>Created:</strong> {{ job.created_at|date:"M d, Y H:i" }}
                            </span>
                        </div>

                        {% if job.status == 'RUNNING' %}
                            <div class="progress-container">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {{ job.progress_pct }}%"></div>
                                </div>
                                <span class="progress-text">{{ job.progress_pct }}%</span>
                            </div>
                        {% endif %}

                        {% if job.error_details %}
                            <div class="error-message">
                                <strong>Error:</strong> {{ job.error_details|truncatechars:100 }}
                            </div>
                        {% endif %}

                        {% if job.status == 'DONE' %}
                            <div class="file-info">
                                {% if job.path_mp3 %}<span class="file-name">MP3 Ready</span>{% endif %}
                                {% if job.path_mp4 %}<span class="file-name">MP4 Ready</span>{% endif %}
                            </div>
                        {% endif %}
                    </div>

                    <div class="job-actions">
                        <a href="{% url 'app_ytdl_simple:job_detail' job.id %}" class="btn btn-sm btn-outline">
                            View Details
                        </a>
                        
                        {% if job.status == 'DONE' %}
                            {% if job.path_mp3 %}
                                <a href="{% url 'app_ytdl_simple:job_download' job.id 'mp3' %}" class="btn btn-sm btn-success">
                                    🎵 MP3
                                </a>
                            {% endif %}
                            {% if job.path_mp4 %}
                                <a href="{% url 'app_ytdl_simple:job_download' job.id 'mp4' %}" class="btn btn-sm btn-success">
                                    🎬 MP4
                                </a>
                            {% endif %}
                        {% endif %}

                        {% if job.status == 'ERROR' %}
                            <button class="btn btn-sm btn-warning retry-btn" data-job-id="{{ job.id }}">
                                🔄 Retry
                            </button>
                        {% endif %}

                        {% if job.status in 'PENDING,RUNNING' %}
                            <button class="btn btn-sm btn-danger cancel-btn" data-job-id="{{ job.id }}">
                                ❌ Cancel
                            </button>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        </div>

        <!-- Pagination -->
        {% if is_paginated %}
            <div class="pagination-container">
                <div class="pagination">
                    {% if page_obj.has_previous %}
                        <a href="?page=1" class="page-link">« First</a>
                        <a href="?page={{ page_obj.previous_page_number }}" class="page-link">‹ Previous</a>
                    {% endif %}

                    <span class="page-info">
                        Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}
                    </span>

                    {% if page_obj.has_next %}
                        <a href="?page={{ page_obj.next_page_number }}" class="page-link">Next ›</a>
                        <a href="?page={{ page_obj.paginator.num_pages }}" class="page-link">Last »</a>
                    {% endif %}
                </div>
            </div>
        {% endif %}

    {% else %}
        <div class="empty-state">
            <div class="empty-icon">📥</div>
            <h3>No download jobs yet</h3>
            <p>Start your first YouTube download!</p>
            <a href="{% url 'app_ytdl_simple:job_form' %}" class="btn btn-primary">+ Create First Download</a>
        </div>
    {% endif %}
</div>

{% block extra_js %}
<script src="{% static 'app_ytdl_simple/js/dashboard.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh for active jobs
    const activeJobs = document.querySelectorAll('[data-status="RUNNING"], [data-status="PENDING"]');
    if (activeJobs.length > 0) {
        setInterval(() => {
            location.reload();
        }, 5000); // Refresh every 5 seconds
    }

    // Handle retry buttons
    document.querySelectorAll('.retry-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const jobId = this.dataset.jobId;
            fetch(`/tools/ytdl/jobs/${jobId}/retry/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to retry job: ' + data.error);
                }
            });
        });
    });

    // Handle cancel buttons
    document.querySelectorAll('.cancel-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const jobId = this.dataset.jobId;
            if (confirm('Are you sure you want to cancel this job?')) {
                fetch(`/tools/ytdl/jobs/${jobId}/cancel/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Failed to cancel job: ' + data.error);
                    }
                });
            }
        });
    });
});
</script>
{% endblock %}
{% endblock %}'''

            # Job detail template
            job_detail_template = '''{% extends "''' + app_name + '''/base.html" %}
{% load static %}

{% block title %}YouTube Download - {{ job.video_title|default:"Job Details" }}{% endblock %}

{% block extra_css %}
<link rel="stylesheet" type="text/css" href="{% static 'app_ytdl_simple/css/style.css' %}">
{% endblock %}

{% block content %}
<div class="container">
    <div class="header-section">
        <h1>📄 Job Details</h1>
        <p class="subtitle">{{ job.video_title|default:"Download Job" }}</p>
    </div>

    <div class="action-bar">
        <a href="{% url 'app_ytdl_simple:job_list' %}" class="btn btn-secondary">← Back to Jobs</a>
        <a href="{% url 'app_ytdl_simple:dashboard' %}" class="btn btn-secondary">Dashboard</a>
        
        {% if job.status == 'DONE' %}
            {% if job.path_mp3 %}
                <a href="{% url 'app_ytdl_simple:job_download' job.id 'mp3' %}" class="btn btn-success">
                    🎵 Download MP3
                </a>
            {% endif %}
            {% if job.path_mp4 %}
                <a href="{% url 'app_ytdl_simple:job_download' job.id 'mp4' %}" class="btn btn-success">
                    🎬 Download MP4
                </a>
            {% endif %}
        {% endif %}
    </div>

    <div class="job-detail-container">
        <!-- Main Job Information -->
        <div class="detail-card">
            <h2>📺 Video Information</h2>
            
            {% if job.thumbnail_url %}
                <div class="thumbnail-container">
                    <img src="{{ job.thumbnail_url }}" alt="Video Thumbnail" class="detail-thumbnail">
                </div>
            {% endif %}

            <div class="detail-grid">
                <div class="detail-item">
                    <label>Title:</label>
                    <span>{{ job.video_title|default:"Not available" }}</span>
                </div>
                
                <div class="detail-item">
                    <label>Original URL:</label>
                    <span><a href="{{ job.url }}" target="_blank">{{ job.url }}</a></span>
                </div>
                
                <div class="detail-item">
                    <label>Video ID:</label>
                    <span>{{ job.video_id|default:"Not available" }}</span>
                </div>
                
                <div class="detail-item">
                    <label>Duration:</label>
                    <span>{{ job.duration_formatted|default:"Not available" }}</span>
                </div>
                
                <div class="detail-item">
                    <label>Channel:</label>
                    <span>{{ job.channel_name|default:"Not available" }}</span>
                </div>
                
                <div class="detail-item">
                    <label>Upload Date:</label>
                    <span>{{ job.upload_date|date:"M d, Y"|default:"Not available" }}</span>
                </div>
                
                <div class="detail-item">
                    <label>View Count:</label>
                    <span>{{ job.view_count|default:"Not available" }}</span>
                </div>
                
                <div class="detail-item">
                    <label>Like Count:</label>
                    <span>{{ job.like_count|default:"Not available" }}</span>
                </div>
            </div>

            {% if job.video_description %}
                <div class="description-section">
                    <label>Description:</label>
                    <div class="description-content">{{ job.video_description|linebreaks|truncatewords:100 }}</div>
                </div>
            {% endif %}
        </div>

        <!-- Download Configuration -->
        <div class="detail-card">
            <h2>⚙️ Download Configuration</h2>
            
            <div class="detail-grid">
                <div class="detail-item">
                    <label>Requested Types:</label>
                    <span>{{ job.requested_types }}</span>
                </div>
                
                <div class="detail-item">
                    <label>Quality:</label>
                    <span>{{ job.get_requested_quality_display }}</span>
                </div>
                
                {% if job.custom_subfolder %}
                <div class="detail-item">
                    <label>Custom Subfolder:</label>
                    <span>{{ job.custom_subfolder }}</span>
                </div>
                {% endif %}
            </div>
        </div>

        <!-- Job Status -->
        <div class="detail-card">
            <h2>📊 Job Status</h2>
            
            <div class="status-section">
                <div class="status-indicator status-{{ job.status }}">
                    <span class="status-badge status-{{ job.status }}">{{ job.get_status_display }}</span>
                </div>
                
                {% if job.status == 'RUNNING' %}
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {{ job.progress_pct }}%"></div>
                        </div>
                        <span class="progress-text">{{ job.progress_pct }}%</span>
                    </div>
                {% endif %}
            </div>

            <div class="detail-grid">
                <div class="detail-item">
                    <label>Created:</label>
                    <span>{{ job.created_at|date:"M d, Y H:i:s" }}</span>
                </div>
                
                <div class="detail-item">
                    <label>Last Updated:</label>
                    <span>{{ job.updated_at|date:"M d, Y H:i:s" }}</span>
                </div>
                
                {% if job.finished_at %}
                <div class="detail-item">
                    <label>Completed:</label>
                    <span>{{ job.finished_at|date:"M d, Y H:i:s" }}</span>
                </div>
                {% endif %}
                
                <div class="detail-item">
                    <label>Retry Count:</label>
                    <span>{{ job.retry_count }}</span>
                </div>
            </div>

            {% if job.error_details %}
                <div class="error-section">
                    <label>Error Details:</label>
                    <div class="error-message">{{ job.error_details }}</div>
                </div>
            {% endif %}
        </div>

        <!-- File Information -->
        {% if job.status == 'DONE' %}
        <div class="detail-card">
            <h2>📁 File Information</h2>
            
            <div class="detail-grid">
                {% if job.path_mp3 %}
                <div class="detail-item">
                    <label>MP3 File:</label>
                    <span>
                        <a href="{% url 'app_ytdl_simple:job_download' job.id 'mp3' %}" class="btn btn-sm btn-outline">
                            📥 Download MP3
                        </a>
                        {% if job.size_mp3 %} ({{ job.size_mp3|filesizeformat }}){% endif %}
                    </span>
                </div>
                {% endif %}
                
                {% if job.path_mp4 %}
                <div class="detail-item">
                    <label>MP4 File:</label>
                    <span>
                        <a href="{% url 'app_ytdl_simple:job_download' job.id 'mp4' %}" class="btn btn-sm btn-outline">
                            📥 Download MP4
                        </a>
                        {% if job.size_mp4 %} ({{ job.size_mp4|filesizeformat }}){% endif %}
                    </span>
                </div>
                {% endif %}
                
                {% if job.path_txt %}
                <div class="detail-item">
                    <label>Transcript:</label>
                    <span>
                        <a href="{% url 'app_ytdl_simple:job_download' job.id 'txt' %}" class="btn btn-sm btn-outline">
                            📄 Download Transcript
                        </a>
                        {% if job.size_txt %} ({{ job.size_txt|filesizeformat }}){% endif %}
                    </span>
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}

        <!-- Actions -->
        <div class="detail-card">
            <h2>⚡ Actions</h2>
            
            <div class="action-buttons">
                {% if job.status == 'ERROR' %}
                    <button class="btn btn-warning retry-btn" data-job-id="{{ job.id }}">
                        🔄 Retry Download
                    </button>
                {% endif %}

                {% if job.status in 'PENDING,RUNNING' %}
                    <button class="btn btn-danger cancel-btn" data-job-id="{{ job.id }}">
                        ❌ Cancel Job
                    </button>
                {% endif %}
                
                <a href="{% url 'app_ytdl_simple:job_form' %}?url={{ job.url|urlencode }}" class="btn btn-secondary">
                    📥 Download Again
                </a>
            </div>
        </div>
    </div>
</div>

{% block extra_js %}
<script src="{% static 'app_ytdl_simple/js/dashboard.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh for active jobs
    {% if job.status in 'RUNNING,PENDING' %}
        setInterval(() => {
            location.reload();
        }, 3000); // Refresh every 3 seconds for active jobs
    {% endif %}

    // Handle action buttons
    document.querySelector('.retry-btn')?.addEventListener('click', function() {
        const jobId = this.dataset.jobId;
        fetch(`/tools/ytdl/jobs/${jobId}/retry/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Failed to retry job: ' + data.error);
            }
        });
    });

    document.querySelector('.cancel-btn')?.addEventListener('click', function() {
        const jobId = this.dataset.jobId;
        if (confirm('Are you sure you want to cancel this job?')) {
            fetch(`/tools/ytdl/jobs/${jobId}/cancel/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Failed to cancel job: ' + data.error);
                }
            });
        }
    });
});
</script>
{% endblock %}
{% endblock %}'''

            # Statistics template
            stats_template = '''{% extends "''' + app_name + '''/base.html" %}
{% load static %}

{% block title %}YouTube Downloader - Statistics{% endblock %}

{% block extra_css %}
<link rel="stylesheet" type="text/css" href="{% static 'app_ytdl_simple/css/style.css' %}">
{% endblock %}

{% block content %}
<div class="container">
    <div class="header-section">
        <h1>📊 Download Statistics</h1>
        <p class="subtitle">Your YouTube download analytics</p>
    </div>

    <div class="action-bar">
        <a href="{% url 'app_ytdl_simple:dashboard' %}" class="btn btn-secondary">← Back to Dashboard</a>
        <a href="{% url 'app_ytdl_simple:job_list' %}" class="btn btn-secondary">View Jobs</a>
    </div>

    <!-- Overview Stats -->
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">📥</div>
            <div class="stat-content">
                <h3>{{ stats.total_jobs }}</h3>
                <p>Total Downloads</p>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-content">
                <h3>{{ stats.successful_jobs }}</h3>
                <p>Successful</p>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">❌</div>
            <div class="stat-content">
                <h3>{{ stats.failed_jobs }}</h3>
                <p>Failed</p>
            </div>
        </div>

        <div class="stat-card">
            <div class="stat-icon">💾</div>
            <div class="stat-content">
                <h3>{{ stats.storage_formatted }}</h3>
                <p>Storage Used</p>
            </div>
        </div>
    </div>

    <!-- Additional Statistics -->
    <div class="detail-cards-container">
        <!-- Download Types -->
        <div class="detail-card">
            <h2>📊 Download Summary</h2>
            <div class="detail-grid">
                <div class="detail-item">
                    <label>Success Rate:</label>
                    <span>{{ stats.success_rate|floatformat:1 }}%</span>
                </div>
                <div class="detail-item">
                    <label>Total Storage:</label>
                    <span>{{ stats.storage_formatted }}</span>
                </div>
                <div class="detail-item">
                    <label>First Download:</label>
                    <span>{{ stats.first_download|date:"M d, Y"|default:"Never" }}</span>
                </div>
                <div class="detail-item">
                    <label>Last Download:</label>
                    <span>{{ stats.last_download|date:"M d, Y"|default:"Never" }}</span>
                </div>
            </div>
        </div>

        <!-- Recent Activity -->
        <div class="detail-card">
            <h2>📅 Recent Activity</h2>
            {% if recent_jobs %}
                <div class="recent-downloads">
                    {% for job in recent_jobs %}
                    <div class="recent-item">
                        <div class="recent-thumbnail">
                            {% if job.thumbnail_url %}
                                <img src="{{ job.thumbnail_url }}" alt="Thumbnail">
                            {% else %}
                                <div class="placeholder-thumbnail">📺</div>
                            {% endif %}
                        </div>
                        <div class="recent-info">
                            <h4>{{ job.video_title|truncatechars:50 }}</h4>
                            <p>{{ job.channel_name|default:"Unknown Channel" }} • {{ job.created_at|timesince }} ago</p>
                            <span class="recent-type">{{ job.requested_types }}</span>
                        </div>
                        <div class="recent-status">
                            <span class="status-badge status-{{ job.status }}">{{ job.get_status_display }}</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <p class="empty-message">No recent downloads.</p>
            {% endif %}
        </div>
    </div>
</div>

{% block extra_js %}
<script src="{% static 'app_ytdl_simple/js/dashboard.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh stats if there are active jobs
    const hasActiveJobs = {{ stats.total_jobs|default:0 }} > {{ stats.successful_jobs|add:stats.failed_jobs|default:0 }};
    if (hasActiveJobs) {
        setInterval(() => {
            location.reload();
        }, 30000); // Refresh every 30 seconds
    }
});
</script>
{% endblock %}
{% endblock %}'''

            # Write templates
            templates = [
                ('dashboard.html', dashboard_template),
                ('job_form.html', job_form_template),
                ('job_list.html', job_list_template),
                ('job_detail.html', job_detail_template),
                ('stats.html', stats_template),
            ]
            
            for template_name, template_content in templates:
                template_file = template_dir / template_name
                logger.debug(f"Writing template: {template_file}")
                write_file_content(template_file, template_content)
            
            # Write CSS
            css_file = static_css_dir / 'style.css'
            logger.debug(f"Writing CSS file: {css_file}")
            write_file_content(css_file, css_content)
            
            logger.info("✓ Enhanced templates created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create enhanced templates: {e}")
            return False
    
    def create_static_assets(self) -> bool:
        """
        Create static assets (CSS, JavaScript) for the YouTube downloader.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Creating Static Assets ===")
        
        try:
            # JavaScript for dashboard functionality
            js_content = '''// YouTube Downloader Dashboard JavaScript

class YTDLDashboard {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupProgressUpdates();
        this.setupBulkActions();
        this.setupAutoRefresh();
    }
    
    setupProgressUpdates() {
        // Auto-update job progress
        const jobCards = document.querySelectorAll('[data-job-id]');
        jobCards.forEach(card => {
            const jobId = card.dataset.jobId;
            const status = card.dataset.status;
            
            if (status === 'RUNNING' || status === 'PENDING') {
                this.updateJobProgress(jobId, card);
            }
        });
    }
    
    async updateJobProgress(jobId, card) {
        try {
            const response = await fetch(`/tools/ytdl/jobs/${jobId}/status.json`);
            const data = await response.json();
            
            // Update progress bar
            const progressBar = card.querySelector('.progress-fill');
            if (progressBar) {
                progressBar.style.width = `${data.progress_pct}%`;
            }
            
            // Update status badge
            const statusBadge = card.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.textContent = data.status;
                statusBadge.className = `status-badge status-${data.status.toLowerCase()}`;
            }
            
            // Update message
            const messageEl = card.querySelector('.job-message');
            if (messageEl) {
                messageEl.textContent = data.message;
            }
            
            // Continue updating if still running
            if (data.status === 'RUNNING' || data.status === 'PENDING') {
                setTimeout(() => this.updateJobProgress(jobId, card), 3000);
            } else if (data.status === 'DONE') {
                // Refresh page to show download links
                setTimeout(() => location.reload(), 2000);
            }
            
        } catch (error) {
            console.error('Error updating job progress:', error);
        }
    }
    
    setupBulkActions() {
        const selectAllBtn = document.getElementById('select-all');
        const bulkActionBtn = document.getElementById('bulk-action');
        const checkboxes = document.querySelectorAll('.job-checkbox');
        
        if (!selectAllBtn || !bulkActionBtn) return;
        
        selectAllBtn.addEventListener('change', (e) => {
            checkboxes.forEach(cb => cb.checked = e.target.checked);
            this.updateBulkActionButton();
        });
        
        checkboxes.forEach(cb => {
            cb.addEventListener('change', () => this.updateBulkActionButton());
        });
        
        bulkActionBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleBulkAction();
        });
    }
    
    updateBulkActionButton() {
        const selectedJobs = document.querySelectorAll('.job-checkbox:checked');
        const bulkActionBtn = document.getElementById('bulk-action');
        
        if (bulkActionBtn) {
            bulkActionBtn.style.display = selectedJobs.length > 0 ? 'inline-flex' : 'none';
            bulkActionBtn.textContent = `Actions (${selectedJobs.length})`;
        }
    }
    
    async handleBulkAction() {
        const selectedJobs = Array.from(document.querySelectorAll('.job-checkbox:checked'))
                                  .map(cb => cb.value);
        
        if (selectedJobs.length === 0) return;
        
        const action = prompt('Enter action: retry, cancel, or delete');
        if (!action || !['retry', 'cancel', 'delete'].includes(action)) return;
        
        try {
            const response = await fetch('/tools/ytdl/api/bulk-action/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    action: action,
                    job_ids: selectedJobs
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert(`Error: ${data.error}`);
            }
            
        } catch (error) {
            console.error('Bulk action error:', error);
            alert('An error occurred while performing the bulk action.');
        }
    }
    
    setupAutoRefresh() {
        // Auto-refresh page if there are active jobs
        const activeJobs = document.querySelectorAll('[data-status="RUNNING"], [data-status="PENDING"]');
        
        if (activeJobs.length > 0) {
            setTimeout(() => {
                location.reload();
            }, 30000); // Refresh every 30 seconds
        }
    }
    
    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new YTDLDashboard();
});

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    if (!seconds) return 'Unknown';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

// URL validation
function isValidYouTubeURL(url) {
    const patterns = [
        /^https?:\\/\\/(www\\.)?youtube\\.com\\/watch\\?v=[\\w-]+/,
        /^https?:\\/\\/(www\\.)?youtu\\.be\\/[\\w-]+/,
        /^https?:\\/\\/(www\\.)?youtube\\.com\\/playlist\\?list=[\\w-]+/,
        /^https?:\\/\\/(www\\.)?youtube\\.com\\/channel\\/[\\w-]+/,
        /^https?:\\/\\/(www\\.)?youtube\\.com\\/user\\/[\\w-]+/,
        /^https?:\\/\\/(www\\.)?youtube\\.com\\/c\\/[\\w-]+/
    ];
    
    return patterns.some(pattern => pattern.test(url));
}
'''
            
            # Additional CSS for job list and detail pages
            additional_css = '''
/* Job List Styles */
.job-list-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
}

.job-list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
    gap: 1rem;
}

.search-form {
    display: flex;
    gap: 1rem;
    align-items: end;
    flex-wrap: wrap;
}

.search-form .form-group {
    margin-bottom: 0;
    min-width: 200px;
}

.job-table {
    width: 100%;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.job-table th,
.job-table td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #e5e7eb;
}

.job-table th {
    background: #f9fafb;
    font-weight: 600;
    color: #374151;
}

.job-table tr:last-child td {
    border-bottom: none;
}

.job-table tr:hover {
    background: #f9fafb;
}

.job-title {
    font-weight: 500;
    color: #1f2937;
    max-width: 300px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.job-channel {
    color: #6b7280;
    font-size: 0.875rem;
}

.job-actions-cell {
    white-space: nowrap;
}

.job-actions-cell .btn {
    margin-right: 0.5rem;
    margin-bottom: 0.25rem;
}

/* Job Detail Styles */
.job-detail-page {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
}

.job-detail-header {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.job-detail-title {
    margin: 0 0 1rem 0;
    color: #1f2937;
}

.job-meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}

.meta-item {
    padding: 1rem;
    background: #f9fafb;
    border-radius: 0.5rem;
}

.meta-label {
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}

.meta-value {
    font-weight: 500;
    color: #1f2937;
}

.download-section {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.download-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
}

.download-item {
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1.5rem;
    text-align: center;
    transition: border-color 0.2s;
}

.download-item:hover {
    border-color: #3b82f6;
}

.download-icon {
    width: 48px;
    height: 48px;
    margin: 0 auto 1rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f3f4f6;
    border-radius: 50%;
    color: #6b7280;
}

.download-title {
    font-weight: 500;
    color: #1f2937;
    margin-bottom: 0.5rem;
}

.download-size {
    color: #6b7280;
    font-size: 0.875rem;
    margin-bottom: 1rem;
}

/* Pagination */
.pagination {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin: 2rem 0;
}

.pagination a,
.pagination span {
    padding: 0.5rem 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.375rem;
    text-decoration: none;
    color: #374151;
    transition: all 0.2s;
}

.pagination a:hover {
    background: #f3f4f6;
    border-color: #d1d5db;
}

.pagination .current {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
}

/* Statistics Page */
.stats-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.stats-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stats-card h3 {
    margin: 0 0 1rem 0;
    color: #1f2937;
    font-size: 1.125rem;
}

.chart-container {
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f9fafb;
    border-radius: 0.5rem;
    color: #6b7280;
}

/* Toast Notifications */
.toast {
    position: fixed;
    top: 1rem;
    right: 1rem;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    padding: 1rem 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    max-width: 400px;
}

.toast.success {
    border-left: 4px solid #10b981;
}

.toast.error {
    border-left: 4px solid #ef4444;
}

.toast.warning {
    border-left: 4px solid #f59e0b;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
    .job-list-header {
        flex-direction: column;
        align-items: stretch;
    }
    
    .search-form {
        flex-direction: column;
    }
    
    .search-form .form-group {
        min-width: auto;
    }
    
    .job-table {
        font-size: 0.875rem;
    }
    
    .job-table th,
    .job-table td {
        padding: 0.75rem 0.5rem;
    }
    
    .job-meta-grid {
        grid-template-columns: 1fr;
    }
    
    .download-grid {
        grid-template-columns: 1fr;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
}
'''
            
            static_dir = self.project_dir / 'app_ytdl_simple' / 'static' / 'app_ytdl_simple'
            
            # Write JavaScript
            js_file = static_dir / 'js' / 'dashboard.js'
            logger.debug(f"Writing JavaScript file: {js_file}")
            write_file_content(js_file, js_content)
            
            # Append additional CSS
            css_file = static_dir / 'css' / 'style.css'
            existing_css = read_file_content(css_file)
            updated_css = existing_css + '\n\n' + additional_css
            write_file_content(css_file, updated_css)
            
            logger.info("✓ Static assets created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create static assets: {e}")
            return False
    
    def update_navigation(self) -> bool:
        """
        Update the main navigation to include YouTube downloader link.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("=== Updating Navigation ===")
        
        try:
            # Find app name from config
            config = self.load_config()
            app_name = config.get('STARTAPP_NAME', 'app_nineteen_o_six')
            
            # Find and update the base template
            base_template_path = self.project_dir / app_name / 'templates' / app_name / 'base.html'
            
            if not base_template_path.exists():
                logger.warning(f"Base template not found at {base_template_path}")
                logger.warning("You may need to manually add the YouTube downloader link to your navigation")
                return True
            
            logger.debug(f"Reading base template: {base_template_path}")
            base_content = read_file_content(base_template_path)
            
            # Check if YouTube downloader link already exists
            if 'app_ytdl_simple:dashboard' in base_content:
                logger.info("YouTube downloader link already exists in navigation")
                return True
            
            # Add YouTube downloader link to navigation
            ytdl_nav_link = '''      <a href="{% url 'app_ytdl_simple:dashboard' %}">YouTube Downloader</a>'''
            
            # Look for the home link and add the YouTube link after it
            if '<a href="{% url \'home\' %}">Home</a>' in base_content:
                base_content = base_content.replace(
                    '<a href="{% url \'home\' %}">Home</a>',
                    '<a href="{% url \'home\' %}">Home</a>\n' + ytdl_nav_link
                )
            elif '<a href="/">Home</a>' in base_content:
                base_content = base_content.replace(
                    '<a href="/">Home</a>',
                    '<a href="/">Home</a>\n' + ytdl_nav_link
                )
            else:
                # Look for nav tag and add after it
                if '<nav>' in base_content:
                    base_content = base_content.replace(
                        '<nav>',
                        '<nav>\n' + ytdl_nav_link
                    )
                else:
                    logger.warning("Could not find navigation section in base template")
                    logger.warning("Please manually add the YouTube downloader link to your navigation")
                    return True
            
            # Save updated template
            logger.debug("Saving updated base template")
            write_file_content(base_template_path, base_content)
            
            logger.info("✓ Navigation updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update navigation: {e}")
            return False
    
    def run_setup(self) -> bool:
        """
        Run the complete YouTube Downloader app setup process.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("🚀 Starting YouTube Downloader App Setup")
        logger.info("=" * 60)
        
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                logger.error("Prerequisites check failed")
                return False
            
            # Check for existing app
            if not self.check_existing_app():
                logger.error("Existing app detected")
                return False
            
            # Execute setup steps
            steps = [
                ("Create App Structure", self.create_app_structure),
                ("Create Enhanced Models", self.create_enhanced_models),
                ("Create Enhanced Forms", self.create_enhanced_forms),
                ("Create Enhanced Utils", self.create_enhanced_utils),
                ("Create Background Tasks", self.create_enhanced_tasks),
                ("Create Enhanced Views", self.create_enhanced_views),
                ("Create App URLs", self.create_app_urls),
                ("Create Enhanced Templates", self.create_enhanced_templates),
                ("Create Static Assets", self.create_static_assets),
                ("Create Admin Interface", self.create_admin_interface),
                ("Update Django Settings", self.update_settings_py),
                ("Update Project URLs", self.update_project_urls),
                ("Update Navigation", self.update_navigation),
                ("Run Migrations", self.run_migrations),
            ]
            
            # Execute each step
            for step_name, step_func in steps:
                logger.info(f"\n--- {step_name} ---")
                if not step_func():
                    logger.error(f"Failed at step: {step_name}")
                    return False
            
            # Success message
            logger.info("\n" + "=" * 60)
            logger.info("🎉 YouTube Downloader App Setup Completed Successfully!")
            logger.info("=" * 60)
            logger.info("\nFeatures installed:")
            logger.info("• Enhanced YouTube downloader with quality selection")
            logger.info("• Interactive dashboard with live progress updates")
            logger.info("• Complete metadata storage (views, likes, thumbnails, etc.)")
            logger.info("• Playlist and channel support with batch processing")
            logger.info("• Advanced file organization (by date, channel, custom folders)")
            logger.info("• Comprehensive error handling and retry functionality")
            logger.info("• User statistics and download history")
            logger.info("• Responsive modern UI with dark/light theme support")
            logger.info("• RESTful API for job status and management")
            
            logger.info("\nNext steps:")
            logger.info("1. Run: python manage.py runserver")
            logger.info("2. Visit: http://127.0.0.1:8000/")
            logger.info("3. Log in with your account")
            logger.info("4. Click 'YouTube Downloader' in the navigation")
            logger.info("5. Start downloading videos, playlists, and channels!")
            
            logger.info("\nAccess URLs:")
            logger.info("• Dashboard: /tools/ytdl/")
            logger.info("• Job History: /tools/ytdl/jobs/")
            logger.info("• Statistics: /tools/ytdl/stats/")
            
            logger.info("\nNote: Ensure FFmpeg is properly installed for audio/video processing!")
            
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
        setup = YouTubeDownloaderSetup()
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
