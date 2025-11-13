"""
Tests for ContactService.

This module contains comprehensive tests for all contact service operations.
"""

import pytest
from datetime import datetime, timedelta
from src.models.address_book import AddressBook
from src.models.record import Record
from src.services.contact_service import ContactService, ContactSortBy


@pytest.fixture
def address_book():
    """Create an empty address book for testing."""
    return AddressBook()


@pytest.fixture
def contact_service(address_book):
    """Create a contact service with an empty address book."""
    return ContactService(address_book)


@pytest.fixture
def populated_service():
    """Create a contact service with some test data."""
    book = AddressBook()
    record = Record("John")
    record.add_phone("1234567890")
    record.add_birthday("15.05.1990")
    book.add_record(record)
    return ContactService(book)

@pytest.fixture
def sorting_service():
    """Create a contact service with multiple contacts for sorting tests."""
    book = AddressBook()

    pavlo = Record("Pavlo")
    pavlo.add_phone("3333333333")
    pavlo.add_birthday("15.05.1990")
    pavlo.add_tag("ml")
    pavlo.add_tag("ai")
    book.add_record(pavlo)

    anna = Record("Anna")
    anna.add_phone("1111111111")
    anna.add_birthday("01.01.1980")
    anna.add_tag("ai")
    book.add_record(anna)

    illia = Record("Illia")
    illia.add_phone("2222222222")
    # no birthday, no tags
    book.add_record(illia)

    return ContactService(book)


class TestAddContact:
    """Tests for add_contact method."""
    
    def test_add_new_contact(self, contact_service):
        """Test adding a new contact."""
        result = contact_service.add_contact("Alice", "1234567890")
        assert result == "Contact added."
        assert contact_service.address_book.find("Alice") is not None
    
    def test_add_phone_to_existing_contact(self, populated_service):
        """Test adding a phone to an existing contact."""
        result = populated_service.add_contact("John", "0987654321")
        assert result == "Contact updated."
        record = populated_service.address_book.find("John")
        assert len(record.phones) == 2
    
    def test_add_contact_with_invalid_phone(self, contact_service):
        """Test adding a contact with invalid phone number."""
        with pytest.raises(ValueError):
            contact_service.add_contact("Bob", "invalid")


class TestChangeContact:
    """Tests for change_contact method."""
    
    def test_change_existing_phone(self, populated_service):
        """Test changing an existing phone number."""
        result = populated_service.change_contact("John", "1234567890", "0987654321")
        assert result == "Contact updated."
        record = populated_service.address_book.find("John")
        assert record.find_phone("0987654321") is not None
        assert record.find_phone("1234567890") is None
    
    def test_change_phone_contact_not_found(self, contact_service):
        """Test changing phone for non-existent contact."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.change_contact("NonExistent", "1234567890", "0987654321")
    
    def test_change_phone_number_not_found(self, populated_service):
        """Test changing a phone number that doesn't exist."""
        with pytest.raises(ValueError):
            populated_service.change_contact("John", "9999999999", "0987654321")


class TestGetPhone:
    """Tests for get_phone method."""
    
    def test_get_phone_for_existing_contact(self, populated_service):
        """Test getting phone for existing contact."""
        result = populated_service.get_phone("John")
        assert "1234567890" in result
    
    def test_get_phone_contact_not_found(self, contact_service):
        """Test getting phone for non-existent contact."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.get_phone("NonExistent")
    
    def test_get_phone_no_phones(self, contact_service):
        """Test getting phone for contact with no phones."""
        service = contact_service
        record = Record("NoPhone")
        service.address_book.add_record(record)
        result = service.get_phone("NoPhone")
        assert "No phones" in result


class TestGetAllContacts:
    """Tests for get_all_contacts method."""
    
    def test_get_all_contacts_empty(self, contact_service):
        """Test getting all contacts when address book is empty."""
        result = contact_service.get_all_contacts()
        assert "Address book is empty" in result or result == ""
    
    def test_get_all_contacts_populated(self, populated_service):
        """Test getting all contacts with data."""
        result = populated_service.get_all_contacts()
        assert "John" in result
        assert "1234567890" in result


class TestBirthday:
    """Tests for birthday-related methods."""
    
    def test_add_birthday(self, contact_service):
        """Test adding a birthday to a contact."""
        contact_service.add_contact("Alice", "1234567890")
        result = contact_service.add_birthday("Alice", "10.03.1995")
        assert result == "Birthday added."
    
    def test_add_birthday_contact_not_found(self, contact_service):
        """Test adding birthday to non-existent contact."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.add_birthday("NonExistent", "10.03.1995")
    
    def test_add_birthday_invalid_format(self, contact_service):
        """Test adding birthday with invalid format."""
        contact_service.add_contact("Alice", "1234567890")
        with pytest.raises(ValueError):
            contact_service.add_birthday("Alice", "invalid-date")
    
    def test_get_birthday(self, populated_service):
        """Test getting birthday for a contact."""
        result = populated_service.get_birthday("John")
        assert "15.05.1990" in result
    
    def test_get_birthday_not_set(self, contact_service):
        """Test getting birthday when not set."""
        contact_service.add_contact("Alice", "1234567890")
        result = contact_service.get_birthday("Alice")
        assert "No birthday set" in result
    
    def test_get_birthday_contact_not_found(self, contact_service):
        """Test getting birthday for non-existent contact."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.get_birthday("NonExistent")
    
    def test_get_upcoming_birthdays_none(self, contact_service):
        """Test getting upcoming birthdays when none exist."""
        result = contact_service.get_upcoming_birthdays()
        assert "No upcoming birthdays" in result
    
    def test_get_upcoming_birthdays_within_week(self, contact_service):
        """Test getting birthdays within the next week."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_in_5_days = today + timedelta(days=5)
        birthday_str = birthday_in_5_days.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result = contact_service.get_upcoming_birthdays()
        assert "John" in result
        assert "No upcoming birthdays" not in result
    
    def test_get_upcoming_birthdays_today(self, contact_service):
        """Test that get_upcoming_birthdays includes today's birthday."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_str = today.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result = contact_service.get_upcoming_birthdays()
        assert "John" in result
    
    def test_get_upcoming_birthdays_past_birthday(self, contact_service):
        """Test that get_upcoming_birthdays excludes past birthdays."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_yesterday = today - timedelta(days=1)
        birthday_str = birthday_yesterday.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result = contact_service.get_upcoming_birthdays()
        assert "No upcoming birthdays" in result
    
    def test_get_upcoming_birthdays_too_far_in_future(self, contact_service):
        """Test that get_upcoming_birthdays excludes birthdays more than 7 days away."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_in_8_days = today + timedelta(days=8)
        birthday_str = birthday_in_8_days.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result = contact_service.get_upcoming_birthdays()
        assert "No upcoming birthdays" in result
    
    def test_get_upcoming_birthdays_multiple_contacts(self, contact_service):
        """Test that get_upcoming_birthdays returns multiple contacts."""
        today = datetime.today().date()
        
        contact_service.add_contact("John", "1234567890")
        john_birthday = (today + timedelta(days=2)).strftime("%d.%m.2000")
        contact_service.add_birthday("John", john_birthday)
        
        contact_service.add_contact("Jane", "0987654321")
        jane_birthday = (today + timedelta(days=5)).strftime("%d.%m.2000")
        contact_service.add_birthday("Jane", jane_birthday)
        
        result = contact_service.get_upcoming_birthdays()
        assert "John" in result
        assert "Jane" in result
    
    def test_get_upcoming_birthdays_weekend_adjustment(self, contact_service):
        """Test that birthdays on weekends are moved to Monday."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        
        next_saturday = today + timedelta(days=days_until_saturday)
        birthday_str = next_saturday.strftime("%d.%m.2000")
        
        if days_until_saturday <= 7:
            contact_service.add_birthday("John", birthday_str)
            result = contact_service.get_upcoming_birthdays()
            
            if "John" in result:
                lines = result.split('\n')
                for line in lines:
                    if "John" in line:
                        date_str = line.split(': ')[1]
                        congratulation_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                        assert congratulation_date.weekday() == 0
    
    def test_get_upcoming_birthdays_custom_days(self, contact_service):
        """Test that get_upcoming_birthdays accepts custom days parameter."""
        contact_service.add_contact("John", "1234567890")
        
        today = datetime.today().date()
        birthday_in_10_days = today + timedelta(days=10)
        birthday_str = birthday_in_10_days.strftime("%d.%m.2000")
        
        contact_service.add_birthday("John", birthday_str)
        
        result_7_days = contact_service.get_upcoming_birthdays(days=7)
        assert "No upcoming birthdays" in result_7_days
        
        result_14_days = contact_service.get_upcoming_birthdays(days=14)
        assert "John" in result_14_days


class TestHasContacts:
    """Tests for has_contacts method."""
    
    def test_has_contacts_empty(self, contact_service):
        """Test has_contacts with empty address book."""
        assert contact_service.has_contacts() is False
    
    def test_has_contacts_populated(self, populated_service):
        """Test has_contacts with populated address book."""
        assert populated_service.has_contacts() is True

class TestSorting:
    """Tests for contact sorting logic."""

    def test_list_contacts_sort_by_name(self, sorting_service):
        """Contacts are sorted alphabetically by name (case-insensitive)."""
        items = sorting_service.list_contacts(sort_by=ContactSortBy.NAME)
        names = [name for name, _ in items]
        assert names == ["Anna", "Illia", "Pavlo"]

    def test_list_contacts_sort_by_phone(self, sorting_service):
        """Contacts are sorted by first phone number."""
        items = sorting_service.list_contacts(sort_by=ContactSortBy.PHONE)
        names = [name for name, _ in items]
        # 1111111111 < 2222222222 < 3333333333
        assert names == ["Anna", "Illia", "Pavlo"]

    def test_list_contacts_sort_by_birthday(self, sorting_service):
        """Contacts are sorted by birthday, contacts without birthday go last."""
        items = sorting_service.list_contacts(sort_by=ContactSortBy.BIRTHDAY)
        names = [name for name, _ in items]
        # Anna: 01.01.1980, Pavlo: 15.05.1990, Illia: no birthday -> last
        assert names == ["Anna", "Pavlo", "Illia"]

    def test_list_contacts_sort_by_tag_count(self, sorting_service):
        """Contacts are sorted by tag count in descending order."""
        items = sorting_service.list_contacts(sort_by=ContactSortBy.TAG_COUNT)
        names = [name for name, _ in items]
        # Pavlo: 2 tags, Anna: 1 tag, Illia: 0 tags
        assert names == ["Pavlo", "Anna", "Illia"]

    def test_list_contacts_sort_by_tag_name(self, sorting_service):
        """
        Contacts are sorted by tag names; contacts without tags use empty string
        and therefore go first.
        """
        items = sorting_service.list_contacts(sort_by=ContactSortBy.TAG_NAME)
        names = [name for name, _ in items]
        # Illia: no tags -> key="", Anna: "ai", Pavlo: "ai,ml"/"ml,ai" -> above Anna
        assert names[0] == "Illia"
        assert names.index("Anna") < names.index("Pavlo")

    def test_get_all_contacts_uses_list_contacts_sorting(self, sorting_service, monkeypatch):
        """get_all_contacts should respect sort_by and use list_contacts under the hood."""
        calls = []

        def fake_list_contacts(sort_by):
            calls.append(sort_by)
            # return in sorted order to verify output
            return [("X", sorting_service.address_book.find("Pavlo"))]

        monkeypatch.setattr(sorting_service, "list_contacts", fake_list_contacts)

        result = sorting_service.get_all_contacts(sort_by=ContactSortBy.NAME)
        assert "Contact name: X" in result
        # to be sure, that sort_by is passed to list_contacts
        assert calls == [ContactSortBy.NAME]


class TestTagManagement:
    """Tests for tag management methods."""
    
    def test_add_tag_to_contact(self, populated_service):
        """Test adding a tag to a contact."""
        result = populated_service.add_tag("John", "work")
        assert "added" in result.lower()
        tags = populated_service.list_tags("John")
        assert "work" in tags
    
    def test_add_tag_normalizes_to_lowercase(self, populated_service):
        """Test tags are normalized to lowercase."""
        populated_service.add_tag("John", "Work")
        tags = populated_service.list_tags("John")
        assert "work" in tags
        assert "Work" not in tags
    
    def test_add_tag_to_non_existent_contact(self, contact_service):
        """Test adding tag to non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.add_tag("NonExistent", "work")
    
    def test_remove_tag_from_contact(self, populated_service):
        """Test removing a tag from a contact."""
        populated_service.add_tag("John", "work")
        populated_service.add_tag("John", "important")
        
        result = populated_service.remove_tag("John", "work")
        assert "removed" in result.lower()
        tags = populated_service.list_tags("John")
        assert "work" not in tags
        assert "important" in tags
    
    def test_remove_tag_normalizes(self, populated_service):
        """Test remove_tag normalizes tag names."""
        populated_service.add_tag("John", "work")
        populated_service.remove_tag("John", "Work")  # Uppercase
        tags = populated_service.list_tags("John")
        assert "work" not in tags
    
    def test_remove_tag_from_non_existent_contact(self, contact_service):
        """Test removing tag from non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.remove_tag("NonExistent", "work")
    
    def test_clear_tags_from_contact(self, populated_service):
        """Test clearing all tags from a contact."""
        populated_service.add_tag("John", "work")
        populated_service.add_tag("John", "important")
        
        result = populated_service.clear_tags("John")
        assert "cleared" in result.lower()
        tags = populated_service.list_tags("John")
        assert tags == []
    
    def test_clear_tags_from_non_existent_contact(self, contact_service):
        """Test clearing tags from non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.clear_tags("NonExistent")
    
    def test_list_tags_for_contact(self, populated_service):
        """Test listing all tags for a contact."""
        populated_service.add_tag("John", "work")
        populated_service.add_tag("John", "important")
        populated_service.add_tag("John", "urgent")
        
        tags = populated_service.list_tags("John")
        assert len(tags) == 3
        assert "work" in tags
        assert "important" in tags
        assert "urgent" in tags
    
    def test_list_tags_for_contact_without_tags(self, populated_service):
        """Test listing tags for contact without tags."""
        tags = populated_service.list_tags("John")
        assert tags == []
    
    def test_list_tags_for_non_existent_contact(self, contact_service):
        """Test listing tags for non-existent contact raises error."""
        with pytest.raises(ValueError, match="not found"):
            contact_service.list_tags("NonExistent")
    
    def test_add_invalid_tag_raises_error(self, populated_service):
        """Test adding invalid tag raises error."""
        with pytest.raises(ValueError, match="Invalid tag"):
            populated_service.add_tag("John", "")
    
    def test_add_tag_with_special_characters_invalid(self, populated_service):
        """Test adding tag with invalid special characters raises error."""
        with pytest.raises(ValueError, match="Invalid tag"):
            populated_service.add_tag("John", "tag@#$")


class TestTagSearch:
    """Tests for tag search methods."""
    
    def test_find_by_tags_all_with_list(self, sorting_service):
        """Test finding contacts with all specified tags (list input)."""
        # Pavlo has ['ml', 'ai'], Anna has ['ai']
        results = sorting_service.find_by_tags_all(["ml", "ai"])
        assert len(results) == 1
        assert results[0][0] == "Pavlo"
    
    def test_find_by_tags_all_with_string(self, sorting_service):
        """Test finding contacts with all specified tags (string input)."""
        results = sorting_service.find_by_tags_all("ml,ai")
        assert len(results) == 1
        assert results[0][0] == "Pavlo"
    
    def test_find_by_tags_all_no_matches(self, sorting_service):
        """Test finding contacts when no one has all tags."""
        results = sorting_service.find_by_tags_all(["ml", "nonexistent"])
        assert results == []
    
    def test_find_by_tags_all_empty_tags(self, sorting_service):
        """Test finding contacts with empty tag list."""
        results = sorting_service.find_by_tags_all([])
        assert results == []
    
    def test_find_by_tags_all_single_tag(self, sorting_service):
        """Test finding contacts with single tag."""
        results = sorting_service.find_by_tags_all(["ai"])
        assert len(results) == 2  # Both Pavlo and Anna have 'ai'
        names = [name for name, _ in results]
        assert "Pavlo" in names
        assert "Anna" in names
    
    def test_find_by_tags_any_with_list(self, sorting_service):
        """Test finding contacts with any of specified tags (list input)."""
        results = sorting_service.find_by_tags_any(["ml", "ai"])
        assert len(results) == 2  # Both have at least one tag
        names = [name for name, _ in results]
        assert "Pavlo" in names
        assert "Anna" in names
    
    def test_find_by_tags_any_with_string(self, sorting_service):
        """Test finding contacts with any of specified tags (string input)."""
        results = sorting_service.find_by_tags_any("ml,ai")
        assert len(results) == 2
    
    def test_find_by_tags_any_no_matches(self, sorting_service):
        """Test finding contacts when no one has any of the tags."""
        results = sorting_service.find_by_tags_any(["nonexistent", "alsononexistent"])
        assert results == []
    
    def test_find_by_tags_any_empty_tags(self, sorting_service):
        """Test finding contacts with empty tag list."""
        results = sorting_service.find_by_tags_any([])
        assert results == []
    
    def test_find_by_tags_any_single_tag(self, sorting_service):
        """Test finding contacts with single tag."""
        results = sorting_service.find_by_tags_any(["ml"])
        assert len(results) == 1
        assert results[0][0] == "Pavlo"
    
    def test_prepare_tags_with_invalid_tag(self, contact_service):
        """Test _prepare_tags with invalid tag."""
        with pytest.raises(ValueError, match="Invalid tag"):
            contact_service._prepare_tags(["valid", ""])
    
    def test_prepare_tags_with_string_input(self, contact_service):
        """Test _prepare_tags with comma-separated string."""
        result = contact_service._prepare_tags("work,important")
        assert result == ["work", "important"]
    
    def test_prepare_tags_with_whitespace(self, contact_service):
        """Test _prepare_tags handles whitespace correctly."""
        result = contact_service._prepare_tags(" work , important ")
        assert result == ["work", "important"]


class TestIterNameRecord:
    """Tests for _iter_name_record helper method."""
    
    def test_iter_name_record_normal(self, populated_service):
        """Test iterating over name-record pairs."""
        items = list(populated_service._iter_name_record())
        assert len(items) == 1
        assert items[0][0] == "John"
    
    def test_iter_name_record_with_broken_addressbook(self, contact_service):
        """Test _iter_name_record with broken address book structure."""
        # Replace address_book.data with something that's not a dict
        contact_service.address_book.data = "not_a_dict"
        
        with pytest.raises(RuntimeError, match="not recognized"):
            list(contact_service._iter_name_record())


class TestCalculateUpcomingBirthdays:
    """Tests for _calculate_upcoming_birthdays method."""
    
    def test_calculate_with_contact_without_birthday(self, sorting_service):
        """Test calculation includes contacts without birthdays gracefully."""
        # Illia has no birthday, should be skipped
        results = sorting_service._calculate_upcoming_birthdays(days=365)
        # Should not crash, just skip Illia
        names = [r["name"] for r in results]
        assert "Illia" not in names
    
    def test_calculate_upcoming_birthdays_weekend_adjustment(self):
        """Test that weekend birthdays are adjusted to Monday."""
        book = AddressBook()
        record = Record("Weekend")
        
        # Find a Saturday birthday in the near future
        today = datetime.today().date()
        days_ahead = (5 - today.weekday()) % 7  # Days until next Saturday
        if days_ahead == 0:
            days_ahead = 7  # If today is Saturday, use next Saturday
        
        saturday = today + timedelta(days=days_ahead)
        birthday_str = saturday.strftime("%d.%m") + ".1990"
        record.add_birthday(birthday_str)
        book.add_record(record)
        
        service = ContactService(book)
        results = service._calculate_upcoming_birthdays(days=14)
        
        if results:  # Only test if birthday is in range
            # Congratulation date should be Monday (2 days after Saturday)
            congrat_date_str = results[0]["congratulation_date"]
            congrat_date = datetime.strptime(congrat_date_str, "%d.%m.%Y").date()
            assert congrat_date.weekday() == 0  # Monday


# --- Note Management Tests ---