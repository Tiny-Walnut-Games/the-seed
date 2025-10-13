# Alchemist Faculty Scripts

This directory contains Python scripts for the Alchemist Faculty narrative → evidence distillation pipeline.

## Scripts

### `generate_manifest.py`
Main script for generating experiment manifests from Gu Pot GitHub issues.

```bash
# Generate manifest for specific issue
python generate_manifest.py --issue-number 123 --repo owner/repo --output gu_pot/issue-123/

# Generate from issue URL
python generate_manifest.py --issue-url https://github.com/owner/repo/issues/123

# Batch processing
python generate_manifest.py --batch --issues-file issues_list.txt --output-dir gu_pot/
```

### `validate_setup.py`
Setup validation script that checks dependencies and project structure.

```bash
# Check if Alchemist Faculty is ready to use
python validate_setup.py
```

## Dependencies

Install required packages:
```bash
pip install PyYAML requests argparse
```

Or install from project requirements:
```bash
pip install -r ../../requirements.txt
```

## Usage

1. **First-time setup**: Run `python validate_setup.py`
2. **Generate manifests**: Use `generate_manifest.py` with appropriate flags
3. **Integration**: Scripts integrate with Unity tools and GitHub automation

## Configuration

Scripts support:
- GitHub token authentication via `--github-token` or environment variable
- Multiple output formats (YAML, JSON)
- Dry-run mode for testing
- Verbose logging for debugging

## Integration Points

- **Unity Editor**: C# tools can call Python scripts or vice versa
- **GitHub API**: Automatic issue data fetching with authentication
- **TWG-TLDA Ecosystem**: Compatible with Chronicle Keeper, Pet Events, etc.

See `docs/faculty/alchemist/quickstart-guide.md` for complete usage instructions.