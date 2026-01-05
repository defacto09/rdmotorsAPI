"""Tests for utility functions"""
import pytest
from rdmotorsAPI.utils import (
    validate_vin,
    parse_date,
    normalize_int,
    get_pagination_params,
    get_photo_url
)


class TestValidateVIN:
    """Test VIN validation"""
    
    def test_valid_vin(self):
        """Test valid VIN"""
        assert validate_vin("1HGBH41JXMN109186") is True
    
    def test_invalid_vin_too_short(self):
        """Test VIN that's too short"""
        assert validate_vin("123456") is False
    
    def test_invalid_vin_too_long(self):
        """Test VIN that's too long"""
        assert validate_vin("1HGBH41JXMN1091867") is False
    
    def test_invalid_vin_with_special_chars(self):
        """Test VIN with special characters"""
        assert validate_vin("1HGBH41JXMN10918-") is False
    
    def test_empty_vin(self):
        """Test empty VIN"""
        assert validate_vin("") is False
    
    def test_none_vin(self):
        """Test None VIN"""
        assert validate_vin(None) is False


class TestParseDate:
    """Test date parsing"""
    
    def test_valid_date(self):
        """Test valid date string"""
        result = parse_date("2024-01-15")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    def test_invalid_date(self):
        """Test invalid date string"""
        assert parse_date("invalid-date") is None
    
    def test_empty_date(self):
        """Test empty date string"""
        assert parse_date("") is None
    
    def test_none_date(self):
        """Test None date"""
        assert parse_date(None) is None


class TestNormalizeInt:
    """Test integer normalization"""
    
    def test_valid_int(self):
        """Test valid integer"""
        assert normalize_int("123") == 123
        assert normalize_int(123) == 123
    
    def test_invalid_int(self):
        """Test invalid integer"""
        assert normalize_int("abc") is None
    
    def test_empty_string(self):
        """Test empty string"""
        assert normalize_int("") is None
        assert normalize_int(" ") is None
    
    def test_none_value(self):
        """Test None value"""
        assert normalize_int(None) is None


class TestGetPhotoURL:
    """Test photo URL generation"""
    
    def test_get_photo_url(self):
        """Test photo URL generation"""
        url = get_photo_url("test.jpg")
        assert "test.jpg" in url
        assert url.startswith("http")
