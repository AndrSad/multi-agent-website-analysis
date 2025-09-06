"""
Basic tests that don't require external dependencies
"""

def test_basic_math():
    """Test basic math operations"""
    assert 2 + 2 == 4
    assert 3 * 3 == 9
    assert 10 / 2 == 5


def test_string_operations():
    """Test string operations"""
    text = "Hello, World!"
    assert len(text) == 13
    assert "Hello" in text
    assert text.upper() == "HELLO, WORLD!"


def test_list_operations():
    """Test list operations"""
    numbers = [1, 2, 3, 4, 5]
    assert len(numbers) == 5
    assert sum(numbers) == 15
    assert max(numbers) == 5
    assert min(numbers) == 1


def test_dict_operations():
    """Test dictionary operations"""
    data = {"name": "test", "value": 42}
    assert "name" in data
    assert data["value"] == 42
    assert len(data) == 2
