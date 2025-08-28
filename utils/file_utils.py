"""
File and directory utilities for Django setup automation.
"""
import os
import subprocess
from pathlib import Path
from typing import Union, Optional, List

# Initialize paths - handling both frozen (PyInstaller) and regular Python execution
SCRIPT_DIR = Path(__file__).resolve().parent


def resolve_path(path_input: Union[str, Path], base_dir: Optional[Path] = None) -> Path:
    """
    Resolve a path input to an absolute Path object.
    
    Args:
        path_input: Input path (string or Path object)
        base_dir: Base directory for relative paths (defaults to current working directory)
        
    Returns:
        Resolved absolute Path object
    """
    if base_dir is None:
        base_dir = Path.cwd()
    
    path = Path(path_input)
    
    if path.is_absolute():
        return path.resolve()
    else:
        return (base_dir / path).resolve()


def ensure_directory_exists(directory_path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path object of the created/existing directory
        
    Raises:
        OSError: If directory creation fails
    """
    dir_path = resolve_path(directory_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def check_file_exists(file_path: Union[str, Path]) -> bool:
    """
    Check if a file exists.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file exists, False otherwise
    """
    return resolve_path(file_path).exists()


def check_directory_exists(directory_path: Union[str, Path]) -> bool:
    """
    Check if a directory exists.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists, False otherwise
    """
    return resolve_path(directory_path).is_dir()


def write_file_content(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Raises:
        OSError: If file writing fails
    """
    resolved_path = resolve_path(file_path)
    ensure_directory_exists(resolved_path.parent)
    
    with open(resolved_path, 'w', encoding=encoding) as f:
        f.write(content)


def read_file_content(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    Read content from a file.
    
    Args:
        file_path: Path to the file
        encoding: File encoding (default: utf-8)
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        OSError: If file reading fails
    """
    resolved_path = resolve_path(file_path)
    
    with open(resolved_path, 'r', encoding=encoding) as f:
        return f.read()


def run_command(command: Union[str, List[str]], cwd: Optional[Union[str, Path]] = None, 
                capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """
    Run a system command.
    
    Args:
        command: Command to run (string or list of arguments)
        cwd: Working directory for the command
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise exception on non-zero exit code
        
    Returns:
        CompletedProcess instance
        
    Raises:
        subprocess.CalledProcessError: If command fails and check=True
    """
    if cwd is not None:
        cwd = resolve_path(cwd)
    
    if isinstance(command, str):
        return subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=capture_output, 
            text=True, 
            check=check
        )
    else:
        return subprocess.run(
            command, 
            cwd=cwd, 
            capture_output=capture_output, 
            text=True, 
            check=check
        )


def check_command_available(command: str) -> bool:
    """
    Check if a command is available in the system PATH.
    
    Args:
        command: Command name to check
        
    Returns:
        True if command is available, False otherwise
    """
    try:
        # Try different version flags depending on the command
        version_flags = ["--version", "-version", "--help", "-h"]
        
        # Special case for ffmpeg which uses -version (single dash)
        if command.lower() in ['ffmpeg', 'ffprobe']:
            version_flags = ["-version", "--version", "--help"]
        
        for flag in version_flags:
            try:
                result = run_command(f"{command} {flag}", capture_output=True, check=False)
                # Command is available if it runs without throwing an exception
                # and returns any exit code (some commands return non-zero for version info)
                if result.returncode is not None:
                    return True
            except Exception:
                continue
                
        return False
    except Exception:
        return False


def is_directory_empty(directory_path: Union[str, Path]) -> bool:
    """
    Check if a directory is empty.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory is empty, False otherwise
    """
    dir_path = resolve_path(directory_path)
    if not dir_path.is_dir():
        return True
    
    try:
        next(dir_path.iterdir())
        return False
    except StopIteration:
        return True


def get_django_project_files() -> List[str]:
    """
    Get list of typical Django project files that indicate an existing project.
    
    Returns:
        List of file/directory names
    """
    return [
        'manage.py',
        'settings.py',
        'urls.py',
        'wsgi.py',
        'asgi.py'
    ]


def check_django_project_exists(directory_path: Union[str, Path] = None) -> bool:
    """
    Check if a Django project already exists in the specified directory.
    
    Args:
        directory_path: Directory to check (defaults to current directory)
        
    Returns:
        True if Django project files are found, False otherwise
    """
    if directory_path is None:
        directory_path = Path.cwd()
    else:
        directory_path = resolve_path(directory_path)
    
    django_files = get_django_project_files()
    
    # Check for manage.py in the current directory
    if (directory_path / 'manage.py').exists():
        return True
    
    # Check for any subdirectory containing Django project files
    for item in directory_path.iterdir():
        if item.is_dir():
            django_file_count = sum(1 for file in django_files if (item / file).exists())
            if django_file_count >= 3:  # If 3 or more Django files found
                return True
    
    return False
