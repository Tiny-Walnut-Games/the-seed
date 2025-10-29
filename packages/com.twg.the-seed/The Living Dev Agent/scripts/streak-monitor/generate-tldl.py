#!/usr/bin/env python3
"""
Generate TLDL (Tiny Little Dev Logs) entries from streak analysis data.
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import yaml


def load_analysis(analysis_file: Path) -> dict:
    """Load streak analysis JSON."""
    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_template(template_file: Path) -> dict:
    """Load TLDL template YAML."""
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return get_default_template()


def get_default_template() -> dict:
    """Return default TLDL template structure."""
    return {
        'title': '',
        'date': '',
        'category': 'system-health',
        'significance': 'medium',
        'content': '',
        'tags': []
    }


def generate_tldl_content(analysis: dict) -> str:
    """Generate TLDL content from analysis."""
    status = analysis.get('streak_status', 'unknown')
    ratio = analysis.get('implementation_ratio', 0)
    window = analysis.get('evaluation_window', 14)
    
    content_lines = [
        f"## Streak Monitor Alert: {status.upper()}",
        "",
        f"**Implementation Ratio**: {ratio:.3f}",
        f"**Evaluation Window**: {window} days",
        "",
        "### Key Metrics",
        "",
        f"- Total Charters: {analysis.get('total_charters', 0)}",
        f"- Completed: {analysis.get('implementations_completed', 0)}",
        f"- In Progress: {analysis.get('ideas_in_progress', 0)}",
        f"- Abandoned: {analysis.get('ideas_abandoned', 0)}",
        ""
    ]
    
    stalled = analysis.get('stalled_charters', [])
    if stalled:
        content_lines.append("### Stalled Charters")
        content_lines.append("")
        for charter in stalled[:5]:  # Top 5 stalled
            content_lines.append(f"- {charter['title']} ({charter['days_stalled']} days)")
        content_lines.append("")
    
    content_lines.extend([
        "### System Health Analysis",
        "",
        f"The streak monitoring system detected {status} implementation health over the past {window} days. ",
        f"Implementation ratio of {ratio:.3f} indicates ",
    ])
    
    if ratio >= 0.8:
        content_lines.append("excellent momentum in converting ideas to completed implementations.")
    elif ratio >= 0.6:
        content_lines.append("acceptable progress but room for improvement in idea completion rates.")
    elif ratio >= 0.4:
        content_lines.append("concerning patterns requiring attention to charter completion.")
    else:
        content_lines.append("critical gaps requiring immediate intervention and strategy review.")
    
    content_lines.extend([
        "",
        "### Recommended Actions",
        ""
    ])
    
    if status == 'critical':
        content_lines.extend([
            "- Immediate charter audit required",
            "- Review kill criteria for stalled ideas",
            "- Assess resource allocation and capacity",
            "- Consider simplifying charter requirements"
        ])
    elif status == 'concerning':
        content_lines.extend([
            "- Review current charter priorities",
            "- Check for implementation blockers",
            "- Consider pairing/collaboration on stalled ideas",
            "- Evaluate charter complexity vs capacity"
        ])
    else:
        content_lines.extend([
            "- Maintain current implementation pace",
            "- Continue monitoring for early warning signs",
            "- Document successful patterns for replication"
        ])
    
    return "\n".join(content_lines)


def generate_tldl_entry(analysis: dict, template: dict, output_path: Path) -> dict:
    """Generate complete TLDL entry."""
    status = analysis.get('streak_status', 'unknown')
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    tldl_entry = {
        'title': f"Streak Monitor Alert: {status.upper()}",
        'date': date_str,
        'category': 'system-health',
        'significance': 'high' if status == 'critical' else 'medium' if status == 'concerning' else 'low',
        'tags': ['streak-monitor', 'idea-health', 'automation', status],
        'metrics': {
            'implementation_ratio': analysis.get('implementation_ratio', 0),
            'total_charters': analysis.get('total_charters', 0),
            'completed': analysis.get('implementations_completed', 0),
            'stalled': len(analysis.get('stalled_charters', [])),
            'evaluation_window_days': analysis.get('evaluation_window', 14)
        }
    }
    
    # Generate markdown content
    content = generate_tldl_content(analysis)
    
    # Create YAML frontmatter
    frontmatter = yaml.dump(tldl_entry, default_flow_style=False, sort_keys=False)
    
    # Combine into full TLDL entry
    full_entry = f"---\n{frontmatter}---\n\n{content}\n"
    
    return full_entry


def main():
    parser = argparse.ArgumentParser(description='Generate TLDL entry from streak analysis')
    parser.add_argument('--analysis-file', required=True, help='Path to streak analysis JSON')
    parser.add_argument('--template', required=False, help='Path to TLDL template YAML')
    parser.add_argument('--output', required=True, help='Output TLDL entry path')
    
    args = parser.parse_args()
    
    analysis_file = Path(args.analysis_file)
    if not analysis_file.exists():
        print(f"Error: Analysis file not found: {analysis_file}", file=sys.stderr)
        sys.exit(1)
    
    # Load analysis data
    analysis = load_analysis(analysis_file)
    
    # Load template if provided
    template_path = Path(args.template) if args.template else None
    template = load_template(template_path) if template_path else get_default_template()
    
    # Generate TLDL entry
    output_path = Path(args.output)
    tldl_entry = generate_tldl_entry(analysis, template, output_path)
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(tldl_entry)
    
    print(f"✅ TLDL entry generated: {output_path}")


if __name__ == '__main__':
    main()