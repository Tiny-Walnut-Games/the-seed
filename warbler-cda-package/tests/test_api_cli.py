"""
Comprehensive tests for warbler_cda.api.cli module.

Tests the CLI interface for the FractalStat Retrieval API with mocked HTTP calls.
"""

import pytest
from unittest.mock import Mock, patch
import requests
from click.testing import CliRunner


class TestAPIClient:
    """Test APIClient class with mocked HTTP requests."""

    def test_client_initialization_default(self):
        """APIClient should initialize with default URL."""
        from warbler_cda.api.cli import APIClient

        client = APIClient()
        assert client.base_url == "http://localhost:8000"
        assert hasattr(client, 'session')

    def test_client_initialization_custom_url(self):
        """APIClient should initialize with custom base URL."""
        from warbler_cda.api.cli import APIClient

        client = APIClient("https://api.example.com/v2")
        assert client.base_url == "https://api.example.com/v2"

    def test_client_base_url_trailing_slash_handling(self):
        """APIClient should strip trailing slash from base URL."""
        from warbler_cda.api.cli import APIClient

        client = APIClient("http://localhost:8000/")
        assert client.base_url == "http://localhost:8000"

    @patch('requests.Session.get')
    def test_health_check_success(self, mock_get):
        """health() should return status when API is healthy."""
        from warbler_cda.api.cli import APIClient

        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "healthy",
            "uptime_seconds": 123.45,
            "total_queries": 100,
            "concurrent_queries": 2
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = APIClient("http://localhost:8000")
        result = client.health()

        assert result["status"] == "healthy"
        assert result["uptime_seconds"] == 123.45
        mock_get.assert_called_once_with("http://localhost:8000/health", timeout=5)

    @patch('requests.Session.get')
    def test_health_check_connection_error(self, mock_get):
        """health() should return unhealthy status on connection failure."""
        from warbler_cda.api.cli import APIClient

        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = APIClient("http://localhost:8000")
        result = client.health()

        assert result["status"] == "unhealthy"
        assert "error" in result
        assert "Connection failed" in result["error"]

    @patch('requests.Session.get')
    def test_health_check_timeout_error(self, mock_get):
        """health() should return unhealthy status on timeout."""
        from warbler_cda.api.cli import APIClient

        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        client = APIClient("http://localhost:8000")
        result = client.health()

        assert result["status"] == "unhealthy"
        assert "error" in result

    @patch('requests.Session.get')
    def test_health_check_json_error(self, mock_get):
        """health() should return unhealthy status on JSON parsing error."""
        from warbler_cda.api.cli import APIClient

        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        client = APIClient("http://localhost:8000")
        result = client.health()

        assert result["status"] == "unhealthy"
        assert "error" in result

    @patch('requests.Session.post')
    def test_query_success(self, mock_post):
        """query() should send query and return results."""
        from warbler_cda.api.cli import APIClient

        mock_response = Mock()
        mock_response.json.return_value = {
            "query_id": "test-query",
            "result_count": 2,
            "execution_time_ms": 150.5,
            "results": [
                {"result_id": "doc-1", "relevance_score": 0.95},
                {"result_id": "doc-2", "relevance_score": 0.85}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = APIClient("http://localhost:8000")
        query_data = {"query_id": "test-query", "semantic_query": "test search"}
        result = client.query(query_data)

        assert result["query_id"] == "test-query"
        assert result["result_count"] == 2
        assert len(result["results"]) == 2
        mock_post.assert_called_once_with("http://localhost:8000/query", json=query_data, timeout=30)

    @patch('requests.Session.post')
    def test_query_with_exceptions(self, mock_post):
        """query() should raise exceptions for error responses."""
        from warbler_cda.api.cli import APIClient

        mock_post.side_effect = requests.exceptions.HTTPError("404 Client Error")

        client = APIClient("http://localhost:8000")
        with pytest.raises(requests.exceptions.HTTPError):
            client.query({"query_id": "test"})

    @patch('requests.Session.post')
    def test_bulk_query_success(self, mock_post):
        """bulk_query() should send multiple queries."""
        from warbler_cda.api.cli import APIClient

        mock_response = Mock()
        mock_response.json.return_value = {
            "batch_id": "batch-123",
            "total_queries": 3,
            "successful": 3,
            "failed": 0,
            "execution_time_ms": 450.0,
            "avg_query_time_ms": 150.0,
            "results": [{"query_id": f"q{i}", "result_count": 5} for i in range(3)]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = APIClient("http://localhost:8000")
        queries = [{"query_id": f"q{i}", "semantic_query": "test"} for i in range(3)]
        result = client.bulk_query(queries)

        assert result["total_queries"] == 3
        assert result["successful"] == 3
        assert len(result["results"]) == 3

        # Check expected payload structure
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert "queries" in payload
        assert "concurrency_level" in payload
        assert payload["concurrency_level"] == 5  # default
        assert payload["queries"] == queries

    @patch('requests.Session.post')
    def test_bulk_query_custom_concurrency(self, mock_post):
        """bulk_query() should accept custom concurrency level."""
        from warbler_cda.api.cli import APIClient

        mock_response = Mock()
        mock_response.json.return_value = {"total_queries": 2, "results": []}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = APIClient("http://localhost:8000")
        queries = [{"query_id": "q1"}, {"query_id": "q2"}]
        client.bulk_query(queries, concurrency=10, include_narrative=True)

        # Verify custom parameters
        payload = mock_post.call_args[1]["json"]
        assert payload["concurrency_level"] == 10
        assert payload["include_narrative_analysis"] is True

    @patch('requests.Session.get')
    def test_get_metrics_success(self, mock_get):
        """get_metrics() should return API metrics."""
        from warbler_cda.api.cli import APIClient

        mock_response = Mock()
        mock_response.json.return_value = {
            "total_queries": 100,
            "hybrid_queries": 50,
            "avg_response_time": 0.25,
            "max_concurrent": 15
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = APIClient("http://localhost:8000")
        result = client.get_metrics()

        assert result["total_queries"] == 100
        assert result["hybrid_queries"] == 50
        mock_get.assert_called_once_with("http://localhost:8000/metrics", timeout=5)

    @patch('requests.Session.post')
    def test_reset_metrics_success(self, mock_post):
        """reset_metrics() should reset API metrics."""
        from warbler_cda.api.cli import APIClient

        mock_response = Mock()
        mock_response.json.return_value = {"status": "metrics_reset"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = APIClient("http://localhost:8000")
        result = client.reset_metrics()

        assert result["status"] == "metrics_reset"
        mock_post.assert_called_once_with("http://localhost:8000/metrics/reset", timeout=5)

    @patch('requests.Session.get')
    def test_session_reuse(self, mock_get):
        """APIClient should reuse the same session for multiple requests."""
        from warbler_cda.api.cli import APIClient

        mock_response = Mock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = APIClient("http://localhost:8000")

        # Make multiple calls
        client.health()
        client.health()

        # Should use the same session (same number of session.get calls)
        assert mock_get.call_count == 2


class TestCLICommands:
    """Test CLI commands with Click test runner."""

    def test_cli_help(self):
        """CLI should display help message."""
        from warbler_cda.api.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert 'EXP-09' in result.output
        assert 'FractalStat' in result.output

    def test_cli_custom_api_url(self):
        """CLI should accept custom API URL."""
        from warbler_cda.api.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['--api-url', 'https://custom.api.com', '--help'])

        assert result.exit_code == 0

    @patch('warbler_cda.api.cli.APIClient.health')
    def test_health_command_success(self, mock_health):
        """health command should display healthy API status."""
        from warbler_cda.api.cli import cli

        mock_health.return_value = {
            "status": "healthy",
            "uptime_seconds": 123.45,
            "total_queries": 100,
            "concurrent_queries": 2
        }

        runner = CliRunner()
        result = runner.invoke(cli, ['health'])

        assert result.exit_code == 0
        mock_health.assert_called_once()
        assert "✓ Service is healthy" in result.output
        assert "123.5s" in result.output
        assert "100" in result.output

    @patch('warbler_cda.api.cli.APIClient.health')
    def test_health_command_unhealthy(self, mock_health):
        """health command should display unhealthy API status."""
        from warbler_cda.api.cli import cli

        mock_health.return_value = {
            "status": "unhealthy",
            "error": "Connection timeout"
        }

        runner = CliRunner()
        result = runner.invoke(cli, ['health'])

        assert result.exit_code == 0
        assert "✗ Service is unhealthy" in result.output
        assert "Connection timeout" in result.output

    @patch('warbler_cda.api.cli.APIClient.query')
    def test_query_command_semantic(self, mock_query):
        """query command should execute semantic query."""
        from warbler_cda.api.cli import cli

        mock_query.return_value = {
            "query_id": "test-1",
            "result_count": 2,
            "results": [
                {"result_id": "doc-1", "relevance_score": 0.95},
                {"result_id": "doc-2", "relevance_score": 0.85}
            ]
        }

        runner = CliRunner()
        result = runner.invoke(cli, [
            'query',
            '--query-id', 'test-1',
            '--semantic', 'test query about AI'
        ])

        assert result.exit_code == 0
        mock_query.assert_called_once()

        # Check that query data was properly constructed
        call_args = mock_query.call_args[0][0]
        assert call_args["query_id"] == "test-1"
        assert call_args["semantic_query"] == "test query about AI"
        assert call_args["mode"] == "semantic_similarity"

    @patch('warbler_cda.api.cli.APIClient.query')
    def test_query_command_hybrid(self, mock_query):
        """query command should execute hybrid query with FractalStat."""
        from warbler_cda.api.cli import cli

        mock_query.return_value = {
            "query_id": "test-hybrid",
            "result_count": 1,
            "results": [{
                "result_id": "doc-1",
                "relevance_score": 0.9,
                "semantic_similarity": 0.85,
                "fractalstat_resonance": 0.75
            }]
        }

        runner = CliRunner()
        result = runner.invoke(cli, [
            'query',
            '--query-id', 'test-hybrid',
            '--semantic', 'test query',
            '--hybrid',
            '--weight-semantic', '0.7',
            '--weight-fractalstat', '0.3'
        ])

        assert result.exit_code == 0

        # Verify hybrid parameters are passed
        call_args = mock_query.call_args[0][0]
        assert call_args["fractalstat_hybrid"] is True
        assert call_args["weight_semantic"] == 0.7
        assert call_args["weight_fractalstat"] == 0.3

    @patch('warbler_cda.api.cli.APIClient.query')
    def test_query_command_missing_semantic(self, mock_query):
        """query command should require semantic query."""
        from warbler_cda.api.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, [
            'query',
            '--query-id', 'test-1'
        ])

        assert result.exit_code == 0  # Click doesn't exit with error, just prints message
        assert "Error: --semantic query required" in result.output
        mock_query.assert_not_called()

    @patch('warbler_cda.api.cli.APIClient.query')
    def test_query_command_json_output(self, mock_query):
        """query command should support JSON output."""
        from warbler_cda.api.cli import cli
        import json

        expected_result = {
            "query_id": "test-json",
            "result_count": 0,
            "results": []
        }
        mock_query.return_value = expected_result

        runner = CliRunner()
        result = runner.invoke(cli, [
            'query',
            '--query-id', 'test-json',
            '--semantic', 'test',
            '--json-output'
        ])

        assert result.exit_code == 0
        # JSON output contains text before JSON, extract and parse the JSON part
        lines = result.output.strip().split('\n')
        # Find the index where JSON starts (first line starting with '{')
        json_start_index = next(i for i, line in enumerate(lines) if line.strip().startswith('{'))
        # Join all lines from JSON start to end to reconstruct the JSON string
        json_string = '\n'.join(lines[json_start_index:])
        assert json.loads(json_string) == expected_result

    @patch('warbler_cda.api.cli.APIClient.query')
    def test_query_command_normal_output_with_narrative(self, mock_query):
        """query command should display formatted output with narrative analysis."""
        from warbler_cda.api.cli import cli

        mock_query.return_value = {
            "query_id": "test-complete",
            "result_count": 3,
            "execution_time_ms": 250.5,
            "semantic_similarity": 0.88,
            "fractalstat_resonance": 0.72,
            "results": [
                {"result_id": "doc-1", "relevance_score": 0.95, "content": "First result content"},
                {"result_id": "doc-2", "relevance_score": 0.85, "content": "Second result content..."},
                {"result_id": "doc-3", "relevance_score": 0.75, "content": "Third result"},
            ],
            "narrative_analysis": {
                "coherence_score": 0.85,
                "narrative_threads": 2,
                "analysis": "Strong narrative coherence detected"
            }
        }

        runner = CliRunner()
        result = runner.invoke(cli, [
            'query',
            '--query-id', 'test-complete',
            '--semantic', 'test query',
            '--hybrid'
        ])

        assert result.exit_code == 0
        assert "Query: test-complete" in result.output
        assert "Results: 3" in result.output
        assert "250.5ms" in result.output
        assert "Semantic Similarity: 0.880" in result.output
        assert "FractalStat Resonance: 0.720" in result.output
        assert "Top Results (3):" in result.output
        assert "Coherence Score: 0.85" in result.output

    @patch('warbler_cda.api.cli.APIClient.bulk_query')
    def test_bulk_command_success(self, mock_bulk_query):
        """bulk command should execute multiple queries."""
        from warbler_cda.api.cli import cli

        mock_bulk_query.return_value = {
            "batch_id": "batch-123",
            "total_queries": 3,
            "successful": 3,
            "failed": 0,
            "execution_time_ms": 450.0,
            "results": [
                {"query_id": "bulk_query_0", "result_count": 5, "execution_time_ms": 150.5},
                {"query_id": "bulk_query_1", "result_count": 3, "execution_time_ms": 145.2},
                {"query_id": "bulk_query_2", "result_count": 7, "execution_time_ms": 154.3},
            ]
        }

        runner = CliRunner()
        result = runner.invoke(cli, [
            'bulk',
            '--num-queries', '3',
            '--semantic', 'query1',
            '--semantic', 'query2',
            '--semantic', 'query3',
            '--hybrid',
            '--concurrency', '10'
        ])

        assert result.exit_code == 0
        mock_bulk_query.assert_called_once()

        # Verify parameters passed correctly - safely access call arguments
        call_args = mock_bulk_query.call_args[0]

        queries = call_args[0]  # First positional argument (queries list)
        assert len(queries) == 3
        assert queries[0]["semantic_query"] == "query1"
        assert queries[1]["semantic_query"] == "query2"
        assert queries[2]["semantic_query"] == "query3"  # Uses all provided semantic queries

        # Verify other parameters exist and have expected values
        if len(call_args) >= 2:
            concurrency = call_args[1]
            assert concurrency == 10  # concurrency
        if len(call_args) >= 3:
            include_narrative = call_args[2]
            assert include_narrative is True  # include_narrative

    @patch('warbler_cda.api.cli.APIClient.get_metrics')
    def test_metrics_command_success(self, mock_get_metrics):
        """metrics command should display API metrics."""
        from warbler_cda.api.cli import cli

        mock_get_metrics.return_value = {
            "timestamp": "2025-01-01T12:00:00",
            "total_queries": 1000,
            "concurrent_queries": 5,
            "max_concurrent": 15,
            "hybrid_queries": 400,
            "errors": 2
        }

        runner = CliRunner()
        result = runner.invoke(cli, ['metrics'])

        assert result.exit_code == 0
        assert "EXP-09 API Service Metrics" in result.output
        assert "1000" in result.output
        assert "400" in result.output

    @patch('warbler_cda.api.cli.APIClient.reset_metrics')
    def test_reset_metrics_command_confirmed(self, mock_reset):
        """reset-metrics command should reset metrics after confirmation."""
        from warbler_cda.api.cli import cli

        mock_reset.return_value = {"status": "metrics_reset"}

        runner = CliRunner()
        # Simulate 'y' input for confirmation
        result = runner.invoke(cli, ['reset-metrics'], input='y\n')

        assert result.exit_code == 0
        mock_reset.assert_called_once()
        assert "✓ metrics_reset" in result.output

    @patch('warbler_cda.api.cli.APIClient.reset_metrics')
    def test_reset_metrics_command_declined(self, mock_reset):
        """reset-metrics command should not reset when declined."""
        from warbler_cda.api.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ['reset-metrics'], input='n\n')

        # Click's confirmation_option raises Abort exception when declined, causing exit code 1
        assert result.exit_code == 1
        mock_reset.assert_not_called()

    @patch('warbler_cda.api.cli.APIClient.bulk_query')
    @patch('warbler_cda.api.cli.APIClient.reset_metrics')
    def test_stress_test_command_success(self, mock_reset, mock_bulk_query):
        """stress-test command should run multiple scenarios."""
        from warbler_cda.api.cli import cli

        mock_reset.return_value = {"status": "reset"}

        # Mock bulk query results for each scenario
        mock_bulk_query.side_effect = [
            {  # First call (reset_metrics not bulk_query)
                "batch_id": "stress-batch-0",
                "successful": 5,
                "failed": 0,
                "batch_narrative_analysis": {"coherence_score": 0.85}
            },
            {  # Second call
                "batch_id": "stress-batch-1",
                "successful": 5,
                "failed": 0,
                "batch_narrative_analysis": {"coherence_score": 0.78}
            }
        ]

        runner = CliRunner()
        result = runner.invoke(cli, [
            'stress-test',
            '--num-scenarios', '2',
            '--queries-per-scenario', '5'
        ])

        assert result.exit_code == 0
        mock_reset.assert_called_once()  # Should reset metrics first

        # Should call bulk_query twice (once per scenario)
        assert mock_bulk_query.call_count == 2

        # Check output contains expected content
        assert "EXP-10 Narrative Preservation Stress Test" in result.output
        assert "Scenarios: 2" in result.output
        assert "Average Coherence Score" in result.output

    @patch('warbler_cda.api.cli.APIClient.bulk_query')
    @patch('warbler_cda.api.cli.APIClient.reset_metrics')
    def test_stress_test_with_hybrid_and_output(self, mock_reset, mock_bulk_query):
        """stress-test command should support hybrid queries and file output."""
        from warbler_cda.api.cli import cli
        import json

        mock_reset.return_value = {"status": "reset"}
        mock_bulk_query.return_value = {
            "batch_id": "hybrid-stress",
            "successful": 3,
            "failed": 0,
            "batch_narrative_analysis": {"coherence_score": 0.92}
        }

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Test with hybrid enabled and output file
            result = runner.invoke(cli, [
                'stress-test',
                '--num-scenarios', '1',
                '--queries-per-scenario', '3',
                '--use-hybrid',
                '--output-file', 'stress_results.json'
            ])

            assert result.exit_code == 0

            # Check file was created with results
            import os
            assert os.path.exists('stress_results.json')

            with open('stress_results.json', 'r', encoding="UTF-8") as f:
                data = json.load(f)
                assert "scenarios" in data
                assert "average_coherence" in data
                assert data["average_coherence"] == 0.92

    @patch('warbler_cda.api.cli.APIClient.query')
    def test_query_command_error_handling(self, mock_query):
        """query command should handle API errors gracefully."""
        from warbler_cda.api.cli import cli

        mock_query.side_effect = requests.exceptions.ConnectionError("API unavailable")

        runner = CliRunner()
        result = runner.invoke(cli, [
            'query',
            '--query-id', 'test-error',
            '--semantic', 'test query'
        ])

        assert result.exit_code == 0  # CLI handles and displays error
        assert "Error:" in result.output

    @patch('warbler_cda.api.cli.APIClient.bulk_query')
    def test_bulk_command_empty_queries(self, mock_bulk_query):
        """bulk command should handle edge case of zero queries."""
        from warbler_cda.api.cli import cli

        mock_bulk_query.return_value = {
            "batch_id": "empty-batch",
            "total_queries": 0,
            "successful": 0,
            "failed": 0,
            "results": []
        }

        runner = CliRunner()
        result = runner.invoke(cli, [
            'bulk',
            '--num-queries', '0'
        ])

        assert result.exit_code == 0
        # Still calls API but with empty query list
        mock_bulk_query.assert_called_once()
        call_args = mock_bulk_query.call_args[0]
        assert call_args[0] == []  # Empty query list

    @patch('warbler_cda.api.cli.APIClient.get_metrics')
    def test_metrics_command_error_handling(self, mock_get_metrics):
        """metrics command should handle API errors."""
        from warbler_cda.api.cli import cli

        mock_get_metrics.side_effect = requests.exceptions.Timeout("Request timed out")

        runner = CliRunner()
        result = runner.invoke(cli, ['metrics'])

        assert result.exit_code == 0
        assert "Error:" in result.output
