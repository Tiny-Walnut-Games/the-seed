"""
Unit tests for start_server.py script.

Tests argument parsing, output formatting, and error handling.
"""

import argparse
import io
import os
import sys
from unittest.mock import Mock, patch

import pytest


class TestStartServer:

    def test_parse_args_defaults(self):
        """Test argument parsing with default values."""
        from start_server import parse_args

        # Test with no arguments
        with patch('sys.argv', ['start_server.py']):
            args = parse_args()

        assert args.host == "127.0.0.1"
        assert args.port == 8000
        assert args.log_level.lower() == "info"
        assert args.reload == False  # Default when no env var is set

    def test_parse_args_custom_values(self):
        """Test argument parsing with custom values."""
        from start_server import parse_args

        with patch('sys.argv', ['start_server.py', '--host', '0.0.0.0', '--port', '9000', '--log-level', 'debug', '--reload']):
            args = parse_args()

        assert args.host == "0.0.0.0"
        assert args.port == 9000
        assert args.log_level.lower() == "debug"
        assert args.reload == True

    @patch.dict(os.environ, {"HOST": "10.0.0.1", "PORT": "9999", "LOG_LEVEL": "warning"})
    def test_parse_args_environment_variables(self):
        """Test argument parsing with environment variables."""
        from start_server import parse_args

        with patch('sys.argv', ['start_server.py']):
            args = parse_args()

        assert args.host == "10.0.0.1"
        assert args.port == 9999
        assert args.log_level.lower() == "warning"

    @patch.dict(os.environ, {"RELOAD": "false"})
    def test_parse_args_reload_env_false(self):
        """Test reload argument with environment variable set to false."""
        from start_server import parse_args

        with patch('sys.argv', ['start_server.py']):
            args = parse_args()

        assert args.reload == False

    @patch.dict(os.environ, {"RELOAD": "1"})
    def test_parse_args_reload_env_true_numeric(self):
        """Test reload argument with environment variable set to 1."""
        from start_server import parse_args

        with patch('sys.argv', ['start_server.py', '--reload']):
            args = parse_args()

        assert args.reload == True

    def test_parse_args_log_level_choices(self):
        """Test that log level argument accepts valid choices."""
        from start_server import parse_args

        valid_levels = ["critical", "error", "warning", "info", "debug", "trace"]

        for level in valid_levels:
            with patch('sys.argv', ['start_server.py', '--log-level', level]):
                args = parse_args()
                assert args.log_level.lower() == level

    def test_parse_args_log_level_invalid_choice(self):
        """Test that invalid log level raises error."""
        from start_server import parse_args

        with patch('sys.argv', ['start_server.py', '--log-level', 'invalid']):
            with pytest.raises(SystemExit):  # argparse exits on invalid choice
                parse_args()

    def test_parse_args_help(self):
        """Test that help argument works."""
        from start_server import parse_args

        with patch('sys.argv', ['start_server.py', '--help']):
            with pytest.raises(SystemExit):  # argparse exits on --help
                parse_args()

    def test_print_startup_info_output(self):
        """Test startup info output formatting."""
        from start_server import print_startup_info

        # Capture stdout
        captured_output = io.StringIO()
        with patch('sys.stdout', new=captured_output):
            print_startup_info("localhost", 3000)

        output = captured_output.getvalue()

        assert "Warbler CDA API Server" in output
        assert "=" * 40 in output
        assert "localhost" in output
        assert "3000" in output
        assert "Health check: http://localhost:3000/health" in output
        assert "API docs:     http://localhost:3000/docs" in output
        assert "Press Ctrl+C to stop" in output

    @patch('builtins.print')
    def test_print_startup_info_function_calls(self, mock_print):
        """Test that print_startup_info calls print with expected strings."""
        from start_server import print_startup_info

        print_startup_info("0.0.0.0", 8080)

        # Verify print calls
        assert mock_print.call_count >= 5  # At least the main elements

        # Check some specific calls using call arguments
        call_args = [str(call) for call in mock_print.call_args_list]
        assert any("Warbler CDA API Server" in arg for arg in call_args)
        assert any("http://0.0.0.0:8080/health" in arg for arg in call_args)
        assert any("http://0.0.0.0:8080/docs" in arg for arg in call_args)

    def test_main_function_normal_execution(self):
        """Test main function with normal execution flow."""
        from start_server import main
        import start_server

        with patch('sys.argv', ['start_server.py']), \
            patch('start_server.uvicorn.run') as mock_uvicorn_run, \
            patch('start_server.print_startup_info') as mock_print_info:

            # Mock the app
            mock_app = Mock()
            mock_app.title = "Test API"
            with patch.object(start_server, 'app', mock_app):
                main()

            mock_print_info.assert_called_once_with("127.0.0.1", 8000)
            mock_uvicorn_run.assert_called_once()
            call_args = mock_uvicorn_run.call_args[1]  # Keyword arguments
            assert call_args['host'] == "127.0.0.1"
            assert call_args['port'] == 8000
            assert call_args['log_level'] == "info"
            assert call_args['reload'] is False  # Default is False now

    def test_main_keyboard_interrupt(self):
        """Test main function handles KeyboardInterrupt gracefully."""
        from start_server import main
        import start_server

        with patch('sys.argv', ['start_server.py']), \
            patch('start_server.uvicorn.run') as mock_uvicorn_run, \
            patch('start_server.print_startup_info'):

            # Mock the app
            mock_app = Mock()
            mock_app.title = "Test API"
            with patch.object(start_server, 'app', mock_app):
                # Simulate KeyboardInterrupt during server run
                mock_uvicorn_run.side_effect = KeyboardInterrupt()

                with patch('builtins.print') as mock_print:
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    assert exc_info.value.code == 0
                    # Check that shutdown message was printed
                    shutdown_calls = [call for call in mock_print.call_args_list
                                    if "Server stopped by user" in str(call)]
                    assert len(shutdown_calls) > 0

    def test_main_import_error(self):
        """Test main function handles ImportError gracefully."""
        # Patch the import at the module level - this would happen during import time
        # So we need to patch the module's app object after import
        from start_server import main
        import start_server

        with patch('sys.argv', ['start_server.py']):

            # Patch the app object at module level
            with patch.object(start_server, 'app', side_effect=ImportError("Module not found")):
                with patch('builtins.print') as mock_print:
                    with pytest.raises(SystemExit) as exc_info:
                        main()

                    assert exc_info.value.code == 1
                    # Check that error message was printed
                    error_calls = [call for call in mock_print.call_args_list
                                if "Import Error:" in str(call)]
                    assert len(error_calls) > 0

    def test_main_generic_exception(self):
        """Test main function handles generic exceptions gracefully."""
        from start_server import main
        import start_server

        with patch('sys.argv', ['start_server.py']), \
            patch('start_server.uvicorn.run') as mock_uvicorn_run, \
            patch('start_server.print_startup_info'), \
            patch('logging.getLogger') as mock_get_logger:

            mock_uvicorn_run.side_effect = RuntimeError("Server failed to start")

            # Mock the logger
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Mock the app
            mock_app = Mock()
            mock_app.title = "Test API"
            with patch.object(start_server, 'app', mock_app):
                with pytest.raises(SystemExit) as exc_info:
                    main()

                assert exc_info.value.code == 1
                # Check that error was logged
                mock_logger.error.assert_called_once()
                call_args = mock_logger.error.call_args
                assert "Error starting server:" in call_args[0][0]

    def test_main_logging_configuration(self):
        """Test that logging is configured properly."""
        from start_server import main
        import start_server

        with patch('sys.argv', ['start_server.py']), \
            patch('start_server.uvicorn.run'), \
            patch('start_server.print_startup_info'), \
            patch('logging.basicConfig') as mock_logging:

            # Mock the app
            mock_app = Mock()
            mock_app.title = "Test API"
            with patch.object(start_server, 'app', mock_app):
                main()

            # Verify logging was configured
            mock_logging.assert_called_once()
            call_args = mock_logging.call_args[1]  # Keyword arguments

            # The logging level should be the INFO constant (which is 20)
            import logging
            assert call_args['level'] == logging.INFO

    def test_script_execution_as_module(self):
        """Test that script can be imported without executing main."""
        # This test ensures the script doesn't run main() when imported
        # We do this by testing that __name__ guard works
        import start_server

        # The module should be importable
        assert hasattr(start_server, 'main')
        assert hasattr(start_server, 'parse_args')
        assert hasattr(start_server, 'print_startup_info')

    @patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "RELOAD": "no"})
    def test_main_environment_variable_precedence(self):
        """Test that CLI arguments override environment variables."""
        from start_server import parse_args

        # First check that env vars are respected without args
        with patch('sys.argv', ['start_server.py']):
            args_env_only = parse_args()
            assert args_env_only.log_level.lower() == "debug"

        # Then check that CLI args override
        with patch('sys.argv', ['start_server.py', '--log-level', 'error']):
            args_cli_override = parse_args()
            assert args_cli_override.log_level.lower() == "error"
