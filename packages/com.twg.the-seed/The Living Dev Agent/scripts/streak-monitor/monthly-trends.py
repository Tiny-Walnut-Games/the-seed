#!/usr/bin/env python3
"""
Analyze monthly streak trends from archived daily data.
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any


def load_archive_files(archive_path: Path, year: int, month: int) -> List[Dict[str, Any]]:
    """Load all archive files for a specific month."""
    month_path = archive_path / str(year) / f"{month:02d}"
    
    if not month_path.exists():
        return []
    
    archives = []
    for file_path in sorted(month_path.glob('streak-*.json')):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['_source_file'] = file_path.name
                archives.append(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {file_path}: {e}", file=sys.stderr)
            continue
    
    return archives


def calculate_trends(archives: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate trend statistics from archived data."""
    if not archives:
        return {
            'error': 'No archive data available',
            'days_analyzed': 0
        }
    
    # Aggregate statistics
    total_days = len(archives)
    ratios = []
    status_counts = defaultdict(int)
    daily_implementations = []
    daily_charters = []
    
    for archive in archives:
        ratio = archive.get('implementation_ratio', 0)
        status = archive.get('streak_status', 'unknown')
        implementations = archive.get('implementations_completed', 0)
        charters = archive.get('total_charters', 0)
        
        ratios.append(ratio)
        status_counts[status] += 1
        daily_implementations.append(implementations)
        daily_charters.append(charters)
    
    # Calculate trends
    avg_ratio = sum(ratios) / len(ratios) if ratios else 0
    min_ratio = min(ratios) if ratios else 0
    max_ratio = max(ratios) if ratios else 0
    
    # Determine overall trend direction
    if len(ratios) >= 2:
        first_half = sum(ratios[:len(ratios)//2]) / (len(ratios)//2)
        second_half = sum(ratios[len(ratios)//2:]) / (len(ratios) - len(ratios)//2)
        
        if second_half > first_half + 0.1:
            trend_direction = 'improving'
        elif second_half < first_half - 0.1:
            trend_direction = 'declining'
        else:
            trend_direction = 'stable'
    else:
        trend_direction = 'insufficient_data'
    
    # Calculate velocity (implementation rate)
    total_implementations = sum(daily_implementations)
    total_charters = max(daily_charters) if daily_charters else 0
    implementation_velocity = total_implementations / total_days if total_days > 0 else 0
    
    trends = {
        'period': {
            'days_analyzed': total_days,
            'first_date': archives[0].get('timestamp', 'unknown'),
            'last_date': archives[-1].get('timestamp', 'unknown')
        },
        'implementation_ratio': {
            'average': round(avg_ratio, 3),
            'minimum': round(min_ratio, 3),
            'maximum': round(max_ratio, 3),
            'trend': trend_direction
        },
        'status_distribution': dict(status_counts),
        'status_percentages': {
            status: round(count / total_days * 100, 1)
            for status, count in status_counts.items()
        },
        'implementation_metrics': {
            'total_implementations': total_implementations,
            'total_charters_peak': total_charters,
            'daily_velocity': round(implementation_velocity, 2),
            'average_daily_implementations': round(sum(daily_implementations) / total_days, 2) if total_days > 0 else 0
        },
        'health_assessment': determine_health_assessment(status_counts, total_days, trend_direction),
        'recommendations': generate_recommendations(avg_ratio, trend_direction, status_counts, total_days)
    }
    
    return trends


def determine_health_assessment(status_counts: Dict[str, int], total_days: int, trend: str) -> str:
    """Determine overall health assessment."""
    critical_pct = status_counts.get('critical', 0) / total_days * 100 if total_days > 0 else 0
    concerning_pct = status_counts.get('concerning', 0) / total_days * 100 if total_days > 0 else 0
    
    if critical_pct > 50:
        return 'critical'
    elif critical_pct > 20 or concerning_pct > 50:
        return 'concerning'
    elif trend == 'declining':
        return 'warning'
    else:
        return 'healthy'


def generate_recommendations(avg_ratio: float, trend: str, status_counts: Dict[str, int], total_days: int) -> List[str]:
    """Generate actionable recommendations based on trends."""
    recommendations = []
    
    if trend == 'declining':
        recommendations.append("📉 Implementation ratio is declining. Review charter priorities and blockers.")
    elif trend == 'improving':
        recommendations.append("📈 Positive trend detected. Document successful patterns for replication.")
    
    if avg_ratio < 0.5:
        recommendations.append("⚠️ Low average implementation ratio. Consider charter scope review.")
    
    critical_days = status_counts.get('critical', 0)
    if critical_days > total_days * 0.2:
        recommendations.append(f"🚨 Critical status appeared {critical_days} days this month. Urgent intervention needed.")
    
    if not recommendations:
        recommendations.append("✅ Implementation health is stable. Continue current practices.")
    
    return recommendations


def main():
    parser = argparse.ArgumentParser(description='Analyze monthly streak trends')
    parser.add_argument('--archive-path', required=True, help='Path to streak archives directory')
    parser.add_argument('--output', required=True, help='Output trends JSON file path')
    parser.add_argument('--year', type=int, help='Year to analyze (defaults to current)')
    parser.add_argument('--month', type=int, help='Month to analyze (defaults to current)')
    
    args = parser.parse_args()
    
    # Determine year and month
    now = datetime.now()
    year = args.year if args.year else now.year
    month = args.month if args.month else now.month
    
    archive_path = Path(args.archive_path)
    if not archive_path.exists():
        print(f"Error: Archive path not found: {archive_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load archive files
    archives = load_archive_files(archive_path, year, month)
    
    if not archives:
        print(f"Warning: No archive data found for {year}-{month:02d}", file=sys.stderr)
    
    # Calculate trends
    trends = calculate_trends(archives)
    trends['analysis_metadata'] = {
        'year': year,
        'month': month,
        'generated_at': datetime.now().isoformat()
    }
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(trends, f, indent=2)
    
    print(f"✅ Monthly trends analysis generated: {output_path}")
    print(f"📊 Analyzed {trends['period']['days_analyzed']} days of data")
    print(f"📈 Trend: {trends['implementation_ratio']['trend']}")


if __name__ == '__main__':
    main()