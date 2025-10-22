"""
EXP-09 CLI - STAT7 Retrieval API Command Line Interface

Click-based CLI for interacting with the EXP-09 API service.
Supports both local and remote instances for concurrent query testing.
Designed for EXP-10 (Narrative Preservation) validation.
"""

import click
import json
import requests
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    """HTTP client for EXP-09 API Service"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def single_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single query"""
        response = self.session.post(
            f"{self.base_url}/query",
            json=query_data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def bulk_query(self, queries: List[Dict[str, Any]], concurrency: int = 5, include_narrative: bool = False) -> Dict[str, Any]:
        """Execute bulk concurrent queries"""
        payload = {
            "queries": queries,
            "concurrency_level": concurrency,
            "include_narrative_analysis": include_narrative
        }
        response = self.session.post(
            f"{self.base_url}/bulk_query",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        response = self.session.get(f"{self.base_url}/metrics", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def reset_metrics(self) -> Dict[str, Any]:
        """Reset service metrics"""
        response = self.session.post(f"{self.base_url}/metrics/reset", timeout=5)
        response.raise_for_status()
        return response.json()


@click.group()
@click.option("--api-url", default="http://localhost:8000", help="API service URL")
@click.pass_context
def cli(ctx, api_url):
    """EXP-09 CLI - STAT7 Retrieval API Command Line Interface"""
    ctx.ensure_object(dict)
    ctx.obj["client"] = APIClient(api_url)
    ctx.obj["api_url"] = api_url


@cli.command()
@click.pass_context
def health(ctx):
    """Check API service health"""
    client = ctx.obj["client"]
    health_data = client.health_check()
    
    click.echo("\n" + "="*60)
    click.echo("EXP-09 API Service Health Check")
    click.echo("="*60)
    
    if health_data.get("status") == "healthy":
        click.secho("✓ Service is healthy", fg="green")
        click.echo(f"  Status: {health_data.get('status')}")
        click.echo(f"  Uptime: {health_data.get('uptime_seconds', 0):.1f}s")
        click.echo(f"  Total Queries: {health_data.get('total_queries', 0)}")
        click.echo(f"  Concurrent Queries: {health_data.get('concurrent_queries', 0)}")
        click.echo(f"  Max Concurrent Observed: {health_data.get('max_concurrent_observed', 0)}")
        click.echo(f"  Hybrid Queries: {health_data.get('hybrid_queries', 0)}")
        click.echo(f"  Errors: {health_data.get('errors', 0)}")
    else:
        click.secho("✗ Service is unhealthy", fg="red")
        click.echo(f"  Error: {health_data.get('error')}")
    
    click.echo()


@cli.command()
@click.option("--query-id", required=True, help="Unique query identifier")
@click.option("--semantic", help="Semantic search query")
@click.option("--hybrid", is_flag=True, help="Enable STAT7 hybrid scoring")
@click.option("--max-results", default=10, help="Maximum results to return")
@click.option("--confidence", default=0.6, help="Confidence threshold")
@click.option("--weight-semantic", default=0.6, help="Semantic weight in hybrid mode")
@click.option("--weight-stat7", default=0.4, help="STAT7 weight in hybrid mode")
@click.option("--json-output", is_flag=True, help="Output as JSON")
@click.pass_context
def query(ctx, query_id, semantic, hybrid, max_results, confidence, weight_semantic, weight_stat7, json_output):
    """Execute a single semantic or hybrid query"""
    client = ctx.obj["client"]
    
    if not semantic:
        click.secho("Error: --semantic query required", fg="red")
        return
    
    query_data = {
        "query_id": query_id,
        "mode": "semantic_similarity",
        "semantic_query": semantic,
        "max_results": max_results,
        "confidence_threshold": confidence,
        "stat7_hybrid": hybrid,
        "weight_semantic": weight_semantic,
        "weight_stat7": weight_stat7
    }
    
    try:
        click.echo(f"\nExecuting query '{query_id}'...")
        result = client.single_query(query_data)
        
        if json_output:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("\n" + "="*60)
            click.echo(f"Query: {result.get('query_id')}")
            click.echo("="*60)
            click.echo(f"Results: {result.get('result_count')}")
            click.echo(f"Execution Time: {result.get('execution_time_ms'):.1f}ms")
            
            if result.get('semantic_similarity'):
                click.echo(f"Semantic Similarity: {result.get('semantic_similarity'):.3f}")
            if result.get('stat7_resonance'):
                click.echo(f"STAT7 Resonance: {result.get('stat7_resonance'):.3f}")
            
            # Show narrative analysis
            if result.get('narrative_analysis'):
                narr = result['narrative_analysis']
                click.echo(f"\nNarrative Analysis:")
                click.echo(f"  Coherence Score: {narr.get('coherence_score', 0):.3f}")
                click.echo(f"  Narrative Threads: {narr.get('narrative_threads', 0)}")
                click.echo(f"  Analysis: {narr.get('analysis')}")
            
            # Show results
            click.echo(f"\nTop Results ({min(3, len(result.get('results', [])))}):")
            for i, res in enumerate(result.get('results', [])[:3], 1):
                click.echo(f"  {i}. Score: {res.get('relevance_score', 0):.3f} | {res.get('content', 'N/A')[:50]}...")
            
            click.echo()
    
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red")


@cli.command()
@click.option("--num-queries", default=5, help="Number of concurrent queries")
@click.option("--concurrency", default=5, help="Concurrency level")
@click.option("--semantic", multiple=True, help="Semantic queries (can specify multiple)")
@click.option("--hybrid", is_flag=True, help="Enable STAT7 hybrid for all queries")
@click.option("--json-output", is_flag=True, help="Output as JSON")
@click.pass_context
def bulk(ctx, num_queries, concurrency, semantic, hybrid, json_output):
    """Execute multiple concurrent queries"""
    client = ctx.obj["client"]
    
    # Generate queries
    if semantic:
        queries_to_run = semantic
    else:
        queries_to_run = [
            "find wisdom about resilience",
            "retrieve stories of growth",
            "locate patterns in narrative",
            "search for entanglement signals",
            "discover narrative coherence"
        ][:num_queries]
    
    query_data = [
        {
            "query_id": f"bulk_query_{i}",
            "mode": "semantic_similarity",
            "semantic_query": q,
            "max_results": 10,
            "confidence_threshold": 0.6,
            "stat7_hybrid": hybrid,
            "weight_semantic": 0.6,
            "weight_stat7": 0.4
        }
        for i, q in enumerate(queries_to_run)
    ]
    
    try:
        click.echo(f"\nExecuting {len(query_data)} concurrent queries (concurrency={concurrency})...")
        start_time = time.time()
        
        result = client.bulk_query(query_data, concurrency=concurrency, include_narrative=True)
        
        elapsed = time.time() - start_time
        
        if json_output:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("\n" + "="*60)
            click.echo("Bulk Query Results")
            click.echo("="*60)
            click.echo(f"Batch ID: {result.get('batch_id')}")
            click.echo(f"Total Queries: {result.get('total_queries')}")
            click.echo(f"Successful: {result.get('successful')} ✓")
            click.echo(f"Failed: {result.get('failed')} ✗")
            click.echo(f"Total Execution Time: {result.get('execution_time_ms'):.1f}ms")
            click.echo(f"Avg Query Time: {result.get('avg_query_time_ms'):.1f}ms")
            
            # Narrative analysis for entire batch
            if result.get('batch_narrative_analysis'):
                narr = result['batch_narrative_analysis']
                click.echo(f"\nBatch Narrative Analysis:")
                click.echo(f"  Coherence Score: {narr.get('coherence_score', 0):.3f}")
                click.echo(f"  Total Narrative Threads: {narr.get('narrative_threads', 0)}")
                click.echo(f"  Total Results: {narr.get('result_count', 0)}")
                click.echo(f"  Analysis: {narr.get('analysis')}")
            
            # Per-query summary
            click.echo(f"\nPer-Query Summary (first 3):")
            for res in result.get('results', [])[:3]:
                click.echo(f"  {res.get('query_id')}: {res.get('result_count')} results in {res.get('execution_time_ms'):.1f}ms")
            
            click.echo()
    
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red")


@cli.command()
@click.option("--json-output", is_flag=True, help="Output as JSON")
@click.pass_context
def metrics(ctx, json_output):
    """Get API service metrics"""
    client = ctx.obj["client"]
    
    try:
        metrics_data = client.get_metrics()
        
        if json_output:
            click.echo(json.dumps(metrics_data, indent=2))
        else:
            click.echo("\n" + "="*60)
            click.echo("EXP-09 API Service Metrics")
            click.echo("="*60)
            click.echo(f"Timestamp: {metrics_data.get('timestamp')}")
            click.echo(f"Total Queries: {metrics_data.get('total_queries')}")
            click.echo(f"Concurrent Queries: {metrics_data.get('concurrent_queries')}")
            click.echo(f"Max Concurrent: {metrics_data.get('max_concurrent')}")
            click.echo(f"Hybrid Queries: {metrics_data.get('hybrid_queries')}")
            click.echo(f"Errors: {metrics_data.get('errors')}")
            click.echo()
    
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red")


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to reset metrics?")
@click.pass_context
def reset_metrics(ctx):
    """Reset API service metrics"""
    client = ctx.obj["client"]
    
    try:
        result = client.reset_metrics()
        click.secho(f"✓ {result.get('status')}", fg="green")
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg="red")


@cli.command()
@click.option("--num-scenarios", default=3, help="Number of concurrent test scenarios")
@click.option("--queries-per-scenario", default=10, help="Queries per scenario")
@click.option("--use-hybrid", is_flag=True, help="Use STAT7 hybrid scoring")
@click.option("--output-file", help="Save results to file")
@click.pass_context
def stress_test(ctx, num_scenarios, queries_per_scenario, use_hybrid, output_file):
    """Run EXP-10 narrative preservation stress test"""
    client = ctx.obj["client"]
    
    click.echo("\n" + "="*60)
    click.echo("EXP-10 Narrative Preservation Stress Test")
    click.echo("="*60)
    click.echo(f"Scenarios: {num_scenarios}")
    click.echo(f"Queries/Scenario: {queries_per_scenario}")
    click.echo(f"Use Hybrid: {use_hybrid}")
    click.echo()
    
    # Reset metrics first
    client.reset_metrics()
    
    results_summary = {
        "start_time": datetime.now().isoformat(),
        "scenarios": [],
        "total_coherence_score": 0.0
    }
    
    # Run multiple scenarios
    scenario_queries = [
        "what defines resilience in narrative",
        "how do characters grow through adversity",
        "what patterns emerge in story arcs",
        "how are themes interconnected",
        "what is the core message preserved"
    ]
    
    for scenario in range(num_scenarios):
        click.echo(f"Scenario {scenario + 1}/{num_scenarios}...")
        
        queries = []
        for q in range(queries_per_scenario):
            query_text = scenario_queries[q % len(scenario_queries)]
            queries.append({
                "query_id": f"stress_s{scenario}_q{q}",
                "mode": "semantic_similarity",
                "semantic_query": query_text,
                "max_results": 5,
                "stat7_hybrid": use_hybrid,
                "weight_semantic": 0.6,
                "weight_stat7": 0.4
            })
        
        try:
            result = client.bulk_query(queries, concurrency=10, include_narrative=True)
            
            scenario_result = {
                "scenario": scenario,
                "queries": len(queries),
                "successful": result.get('successful'),
                "failed": result.get('failed'),
                "avg_query_time_ms": result.get('avg_query_time_ms'),
                "batch_coherence": result.get('batch_narrative_analysis', {}).get('coherence_score', 0)
            }
            
            results_summary["scenarios"].append(scenario_result)
            results_summary["total_coherence_score"] += scenario_result["batch_coherence"]
            
            click.echo(f"  ✓ {result.get('successful')}/{len(queries)} queries successful")
            click.echo(f"  Coherence: {scenario_result['batch_coherence']:.3f}")
            
        except Exception as e:
            click.secho(f"  ✗ Scenario failed: {str(e)}", fg="red")
    
    # Summary
    avg_coherence = results_summary["total_coherence_score"] / max(1, num_scenarios)
    results_summary["average_coherence"] = avg_coherence
    results_summary["end_time"] = datetime.now().isoformat()
    
    click.echo("\n" + "="*60)
    click.echo("Stress Test Summary")
    click.echo("="*60)
    click.echo(f"Scenarios Completed: {len(results_summary['scenarios'])}/{num_scenarios}")
    click.echo(f"Average Coherence Score: {avg_coherence:.3f}")
    click.echo(f"Result: {'PASS ✓' if avg_coherence > 0.7 else 'FAIL ✗'}")
    click.echo()
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results_summary, f, indent=2)
        click.echo(f"Results saved to: {output_file}")


if __name__ == "__main__":
    cli(obj={})