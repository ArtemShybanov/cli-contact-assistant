"""
Parameter validators for CLI commands.

Each validator function is used as a Typer callback to validate
command arguments at the parameter level. This provides better UX
by showing users exactly which parameter has an invalid value.

When adding new fields with validation:
1. Create a validator function here following the template
2. Use it as callback in the command parameter definition
3. Typer will automatically show which parameter failed

Example:
    @app.command()
    def add_command(
        phone: str = typer.Argument(..., callback=validate_phone),
    ):
        ...
"""

import typer
from datetime import datetime


def validate_phone(value: str) -> str:
    """
    Validate phone number format for CLI input.
    
    Phone numbers must be exactly 10 digits.
    
    Args:
        value: Phone number string
        
    Returns:
        Validated phone number
        
    Raises:
        typer.BadParameter: If phone format is invalid
    """
    if not value.isdigit():
        raise typer.BadParameter("Phone number must contain only digits")
    if len(value) != 10:
        raise typer.BadParameter("Phone number must be exactly 10 digits")
    return value


def validate_birthday(value: str) -> str:
    """
    Validate birthday date format for CLI input.
    
    Birthdays must be in DD.MM.YYYY format.
    
    Args:
        value: Birthday string in DD.MM.YYYY format
        
    Returns:
        Validated birthday string
        
    Raises:
        typer.BadParameter: If date format is invalid
    """
    try:
        datetime.strptime(value, "%d.%m.%Y")
        return value
    except ValueError:
        raise typer.BadParameter(
            "Invalid date format. Use DD.MM.YYYY (e.g., 25.12.1990)"
        )


def validate_email(value: str) -> str:
    """
    Validate email format for CLI input.
    
    Example validator for future use with email validation library.
    
    Args:
        value: Email string
        
    Returns:
        Validated email string
        
    Raises:
        typer.BadParameter: If email format is invalid
    """
    if "@" not in value or "." not in value:
        raise typer.BadParameter("Invalid email format")
    return value

import re

_TAG_RE = re.compile(r"^[a-z0-9_-]{1,32}$")

def normalize_tag(tag: str) -> str:
    # trim → collapse spaces → lowercase
    return " ".join(tag.strip().split()).lower()

def is_valid_tag(tag: str) -> bool:
    # empty tags already handled in normalize_tag
    return bool(tag) and bool(_TAG_RE.match(tag))

def split_tags_string(s: str) -> list[str]:
    # "ai, ML ,  python" -> ["ai", "ML", "python"] (without normalization)
    if not s:
        return []
    return [p for p in (part.strip() for part in s.split(",")) if p]