#!/usr/bin/env python3
"""
Generate badge JSON for streak status display.
Compatible with shields.io endpoint format.
"""
import argparse
import json
import sys
from pathlib import Path


def load_analysis(analysis_file: Path) -> dict:
    """Load streak analysis JSON."""
    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def determine_badge_color(status: str, ratio: float) -> str:
    """Determine badge color based on status and ratio."""
    if status == 'critical':
        return 'red'
    elif status == 'concerning':
        return 'orange'
    elif ratio >= 0.9:
        return 'brightgreen'
    elif ratio >= 0.7:
        return 'green'
    else:
        return 'yellowgreen'


def generate_badge_data(analysis: dict) -> dict:
    """Generate badge JSON data."""
    status = analysis.get('streak_status', 'unknown')
    ratio = analysis.get('implementation_ratio', 0)
    implementations = analysis.get('implementations_completed', 0)
    total = analysis.get('total_charters', 0)
    
    color = determine_badge_color(status, ratio)
    
    # Generate shields.io compatible badge data
    badge_data = {
        'schemaVersion': 1,
        'label': 'idea health',
        'message': f"{ratio:.1%} ({implementations}/{total})",
        'color': color,
        'namedLogo': 'github',
        'logoColor': 'white',
        'style': 'flat-square'
    }
    
    # Additional metadata
    badge_data['metadata'] = {
        'status': status,
        'implementation_ratio': ratio,
        'implementations_completed': implementations,
        'total_charters': total,
        'evaluation_window_days': analysis.get('evaluation_window', 14),
        'stalled_count': len(analysis.get('stalled_charters', [])),
        'generated_at': analysis.get('timestamp', 'unknown')
    }
    
    return badge_data


def generate_github_badge_url(badge_data: dict) -> str:
    """Generate GitHub-compatible badge URL."""
    label = badge_data['label'].replace(' ', '%20')
    message = badge_data['message'].replace(' ', '%20')
    color = badge_data['color']
    
    return f"https://img.shields.io/badge/{label}-{message}-{color}?style=flat-square&logo=github"


def generate_markdown_badge(badge_data: dict, badge_url: str) -> str:
    """Generate markdown badge snippet."""
    status = badge_data['metadata']['status']
    
    return f"![Idea Health: {status}]({badge_url})"


def main():
    parser = argparse.ArgumentParser(description='Generate badge JSON from streak analysis')
    parser.add_argument('--analysis-file', required=True, help='Path to streak analysis JSON')
    parser.add_argument('--output', required=True, help='Output badge JSON file path')
    parser.add_argument('--include-url', action='store_true', help='Include badge URL in output')
    parser.add_argument('--include-markdown', action='store_true', help='Include markdown snippet in output')
    
    args = parser.parse_args()
    
    analysis_file = Path(args.analysis_file)
    if not analysis_file.exists():
        print(f"Error: Analysis file not found: {analysis_file}", file=sys.stderr)
        sys.exit(1)
    
    # Load analysis data
    analysis = load_analysis(analysis_file)
    
    # Generate badge data
    badge_data = generate_badge_data(analysis)
    
    # Add optional fields
    if args.include_url:
        badge_data['badge_url'] = generate_github_badge_url(badge_data)
    
    if args.include_markdown:
        badge_url = badge_data.get('badge_url', generate_github_badge_url(badge_data))
        badge_data['markdown'] = generate_markdown_badge(badge_data, badge_url)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(badge_data, f, indent=2)
    
    print(f"✅ Badge JSON generated: {output_path}")
    
    # Print badge URL if generated
    if 'badge_url' in badge_data:
        print(f"🔗 Badge URL: {badge_data['badge_url']}")


if __name__ == '__main__':
    main()