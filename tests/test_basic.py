"""Basic tests to ensure the project setup is working correctly."""

import pytest
from mindbridge import __author__, __version__


class TestBasicSetup:
    """Test basic project setup and configuration."""

    def test_version_is_defined(self) -> None:
        """Test that version is properly defined."""
        assert __version__ == "0.1.0"

    def test_author_is_defined(self) -> None:
        """Test that author is properly defined."""
        assert __author__ == "Mindbridge Team"

    def test_package_imports(self) -> None:
        """Test that the main package can be imported."""
        import mindbridge

        assert mindbridge is not None

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("hello", "hello"),
            ("", ""),
            ("test string", "test string"),
        ],
    )
    def test_parametrized_example(self, test_input: str, expected: str) -> None:
        """Example parametrized test."""
        assert test_input == expected


class TestProjectStructure:
    """Test project structure and organization."""

    def test_src_directory_exists(self) -> None:
        """Test that src directory structure is correct."""
        import os

        assert os.path.exists("src/mindbridge")
        assert os.path.exists("src/mindbridge/__init__.py")

    def test_tests_directory_exists(self) -> None:
        """Test that tests directory structure is correct."""
        import os

        assert os.path.exists("tests")
        assert os.path.exists("tests/__init__.py")
        assert os.path.exists("tests/conftest.py")
