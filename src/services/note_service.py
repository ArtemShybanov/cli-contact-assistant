"""
Note service for managing notes attached to contacts.

This service provides business logic for note operations with proper
separation of concerns and dependency injection support.
"""

from typing import List

from src.models.address_book import AddressBook
from src.models.note import Note
from src.utils.validators import is_valid_tag, normalize_tag


class NoteService:
    """
    Service for managing notes attached to contacts.
    
    This class encapsulates all business logic for note operations,
    including CRUD operations and tag management for notes.
    """
    
    def __init__(self, address_book: AddressBook):
        """
        Initialize the note service.
        
        Args:
            address_book: The address book instance to manage notes in
        """
        self.address_book = address_book
    
    def has_contacts(self) -> bool:
        """
        Check if there are any contacts in the address book.
        
        Returns:
            True if there are contacts, False otherwise
        """
        return len(self.address_book.data) > 0
    
    def list_contacts(self) -> list[tuple[str, str]]:
        """
        List all contacts with their phone numbers.
        
        Returns:
            List of tuples (contact_name, phones_str)
        """
        result = []
        for name, record in self.address_book.data.items():
            phones_str = ", ".join(p.value for p in record.phones) if record.phones else "No phone"
            result.append((name, phones_str))
        return sorted(result, key=lambda x: x[0])
    
    # --- Notes management ---
    
    def add_note(self, contact_name: str, note_name: str, content: str = "") -> str:
        """
        Add a note to a contact.
        
        Args:
            contact_name: Contact name
            note_name: Note name/title
            content: Note text content (default: empty string)
            
        Returns:
            Success message
            
        Raises:
            ValueError: If contact not found or note already exists
        """
        record = self.address_book.find(contact_name)
        if record is None:
            raise ValueError(f"Contact '{contact_name}' not found.")
        
        record.add_note(note_name, content)
        return f"Note '{note_name}' added to {contact_name}."
    
    def edit_note(self, contact_name: str, note_name: str, content: str) -> str:
        """
        Edit an existing note's content.
        
        Args:
            contact_name: Contact name
            note_name: Note name
            content: New text content
            
        Returns:
            Success message
            
        Raises:
            ValueError: If contact or note not found
        """
        record = self.address_book.find(contact_name)
        if record is None:
            raise ValueError(f"Contact '{contact_name}' not found.")
        
        record.edit_note(note_name, content)
        return f"Note '{note_name}' updated for {contact_name}."
    
    def delete_note(self, contact_name: str, note_name: str) -> str:
        """
        Delete a note from a contact.
        
        Args:
            contact_name: Contact name
            note_name: Note name
            
        Returns:
            Success message
            
        Raises:
            ValueError: If contact or note not found
        """
        record = self.address_book.find(contact_name)
        if record is None:
            raise ValueError(f"Contact '{contact_name}' not found.")
        
        record.delete_note(note_name)
        return f"Note '{note_name}' deleted from {contact_name}."
    
    def list_notes(self, contact_name: str) -> List[Note]:
        """
        Get list of all notes for a contact.
        
        Args:
            contact_name: Contact name
            
        Returns:
            List of Note objects
            
        Raises:
            ValueError: If contact not found
        """
        record = self.address_book.find(contact_name)
        if record is None:
            raise ValueError(f"Contact '{contact_name}' not found.")
        
        return record.list_notes()
    
    def get_note(self, contact_name: str, note_name: str) -> Note:
        """
        Get a specific note from a contact.
        
        Args:
            contact_name: Contact name
            note_name: Note name
            
        Returns:
            Note object
            
        Raises:
            ValueError: If contact or note not found
        """
        record = self.address_book.find(contact_name)
        if record is None:
            raise ValueError(f"Contact '{contact_name}' not found.")
        
        note = record.find_note(note_name)
        if note is None:
            raise ValueError(f"Note '{note_name}' not found for {contact_name}.")
        
        return note
    
    # --- Note tags management ---
    
    def note_add_tag(self, contact_name: str, note_name: str, tag: str) -> str:
        """
        Add a tag to a note.
        
        Args:
            contact_name: Contact name
            note_name: Note name
            tag: Tag to add
            
        Returns:
            Success message
            
        Raises:
            ValueError: If contact or note not found, or tag format invalid
        """
        record = self.address_book.find(contact_name)
        if record is None:
            raise ValueError(f"Contact '{contact_name}' not found.")
        
        normalized = normalize_tag(tag)
        if not is_valid_tag(normalized):
            raise ValueError(f"Invalid tag: '{tag}'")
        
        record.note_add_tag(note_name, normalized)
        return f"Tag '{normalized}' added to note '{note_name}'."
    
    def note_remove_tag(self, contact_name: str, note_name: str, tag: str) -> str:
        """
        Remove a tag from a note.
        
        Args:
            contact_name: Contact name
            note_name: Note name
            tag: Tag to remove
            
        Returns:
            Success message
            
        Raises:
            ValueError: If contact or note not found
        """
        record = self.address_book.find(contact_name)
        if record is None:
            raise ValueError(f"Contact '{contact_name}' not found.")
        
        normalized = normalize_tag(tag)
        record.note_remove_tag(note_name, normalized)
        return f"Tag '{normalized}' removed from note '{note_name}'."
    
    def note_clear_tags(self, contact_name: str, note_name: str) -> str:
        """
        Clear all tags from a note.
        
        Args:
            contact_name: Contact name
            note_name: Note name
            
        Returns:
            Success message
            
        Raises:
            ValueError: If contact or note not found
        """
        record = self.address_book.find(contact_name)
        if record is None:
            raise ValueError(f"Contact '{contact_name}' not found.")
        
        record.note_clear_tags(note_name)
        return f"All tags cleared from note '{note_name}'."
    
    def note_list_tags(self, contact_name: str, note_name: str) -> list[str]:
        """
        List all tags for a note.
        
        Args:
            contact_name: Contact name
            note_name: Note name
            
        Returns:
            List of tag strings
            
        Raises:
            ValueError: If contact or note not found
        """
        record = self.address_book.find(contact_name)
        if record is None:
            raise ValueError(f"Contact '{contact_name}' not found.")
        
        return record.note_list_tags(note_name)



