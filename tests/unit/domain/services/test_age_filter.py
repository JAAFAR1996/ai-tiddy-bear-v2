import pytest
from typing import Protocol
from src.domain.value_objects.age_group import AgeGroup
from src.domain.services.age_filter import AgeFilter

class MockAgeFilter(AgeFilter):
    async def filter_content_by_age(self, content: str, age_group: AgeGroup) -> str:
        # Simple mock implementation for testing purposes
        if age_group == AgeGroup.TODDLER:
            return f"Filtered content for toddler: {content.lower()}"
        elif age_group == AgeGroup.PRESCHOOL:
            return f"Filtered content for preschool: {content.capitalize()}"
        return f"Filtered content: {content}"

@pytest.mark.asyncio
async def test_age_filter_protocol_implementation():
    mock_filter = MockAgeFilter()
    
    # Test with TODDLER age group
    content_toddler = "HELLO WORLD"
    age_group_toddler = AgeGroup.TODDLER
    filtered_content_toddler = await mock_filter.filter_content_by_age(content_toddler, age_group_toddler)
    assert isinstance(filtered_content_toddler, str)
    assert "hello world" in filtered_content_toddler
    assert "Filtered content for toddler:" in filtered_content_toddler

    # Test with PRESCHOOL age group
    content_preschool = "test content"
    age_group_preschool = AgeGroup.PRESCHOOL
    filtered_content_preschool = await mock_filter.filter_content_by_age(content_preschool, age_group_preschool)
    assert isinstance(filtered_content_preschool, str)
    assert "Test content" in filtered_content_preschool
    assert "Filtered content for preschool:" in filtered_content_preschool

    # Test with a different age group (e.g., SCHOOL_AGE)
    content_school_age = "another example"
    age_group_school_age = AgeGroup.SCHOOL_AGE
    filtered_content_school_age = await mock_filter.filter_content_by_age(content_school_age, age_group_school_age)
    assert isinstance(filtered_content_school_age, str)
    assert "Filtered content:" in filtered_content_school_age
    assert "another example" in filtered_content_school_age
