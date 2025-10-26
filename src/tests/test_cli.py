"""Tests for the CLI interface."""

from iot_rag.cli import main


class TestCLI:
    def test_cli_main(self, capsys):
        """Test the main function of the CLI."""
        main()
        captured = capsys.readouterr()
        assert "Internet of Things" in captured.out
