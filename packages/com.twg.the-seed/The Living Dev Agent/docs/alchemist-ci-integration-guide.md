# Alchemist Report Synthesis CLI - CI Integration Guide

This document provides guidance for integrating the Alchemist report synthesis CLI tool into CI/CD pipelines.

## GitHub Actions Integration

### Basic Workflow Example

```yaml
name: Alchemist Report Synthesis
on:
  push:
    paths:
      - 'gu_pot/*/claims/**'
      - 'assets/experiments/*/claims/**'

jobs:
  synthesize-reports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install PyYAML requests
          
      - name: Generate reports for all experiments
        run: |
          for exp_dir in gu_pot/issue-*/; do
            if [ -d "$exp_dir" ]; then
              echo "Processing $exp_dir"
              python scripts/alchemist-faculty/report_synthesizer.py \
                --experiment-dir "$exp_dir" \
                --output "$exp_dir/report/report_v$(date +%Y%m%d_%H%M%S).md" \
                --verbose
            fi
          done
          
      - name: Commit generated reports
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add gu_pot/*/report/
          git commit -m "Auto-generated reports from claims data" || exit 0
          git push
```

### Advanced Workflow with Validation

```yaml
name: Alchemist Validation and Report Synthesis
on:
  pull_request:
    paths:
      - 'gu_pot/**'
      - 'assets/experiments/**'

jobs:
  validate-and-synthesize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: pip install PyYAML requests
        
      - name: Validate evidence paths
        run: |
          validation_failed=0
          for exp_dir in gu_pot/issue-*/; do
            if [ -d "$exp_dir" ]; then
              echo "Validating $exp_dir"
              if ! python scripts/alchemist-faculty/report_synthesizer.py \
                --experiment-dir "$exp_dir" \
                --validate-only; then
                validation_failed=1
              fi
            fi
          done
          
          if [ $validation_failed -eq 1 ]; then
            echo "❌ Evidence validation failed for one or more experiments"
            exit 1
          else
            echo "✅ All evidence paths validated successfully"
          fi
          
      - name: Generate reports on validation success
        run: |
          for exp_dir in gu_pot/issue-*/; do
            if [ -d "$exp_dir" ]; then
              python scripts/alchemist-faculty/report_synthesizer.py \
                --experiment-dir "$exp_dir" \
                --output "$exp_dir/report/report_v$(date +%Y%m%d_%H%M%S).md"
            fi
          done
          
      - name: Upload reports as artifacts
        uses: actions/upload-artifact@v3
        with:
          name: alchemist-reports
          path: gu_pot/*/report/*.md
```

## Docker Integration

### Dockerfile for Report Synthesis

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY scripts/requirements.txt .
RUN pip install -r requirements.txt

# Copy scripts
COPY scripts/alchemist-faculty/ ./scripts/alchemist-faculty/

# Set executable permissions
RUN chmod +x scripts/alchemist-faculty/report_synthesizer.py

ENTRYPOINT ["python", "scripts/alchemist-faculty/report_synthesizer.py"]
```

### Docker Compose for Local Development

```yaml
version: '3.8'
services:
  alchemist:
    build: .
    volumes:
      - .:/app
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    command: --experiment-dir gu_pot/issue-123/ --output reports/report.md
```

## Jenkins Pipeline Integration

```groovy
pipeline {
    agent any
    
    environment {
        GITHUB_TOKEN = credentials('github-token')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install PyYAML requests'
            }
        }
        
        stage('Validate Evidence') {
            steps {
                script {
                    def experiments = sh(
                        script: 'find gu_pot -name "issue-*" -type d',
                        returnStdout: true
                    ).trim().split('\n')
                    
                    for (exp in experiments) {
                        sh """
                            python scripts/alchemist-faculty/report_synthesizer.py \\
                                --experiment-dir ${exp} \\
                                --validate-only
                        """
                    }
                }
            }
        }
        
        stage('Generate Reports') {
            steps {
                script {
                    def experiments = sh(
                        script: 'find gu_pot -name "issue-*" -type d',
                        returnStdout: true
                    ).trim().split('\n')
                    
                    for (exp in experiments) {
                        sh """
                            python scripts/alchemist-faculty/report_synthesizer.py \\
                                --experiment-dir ${exp} \\
                                --output ${exp}/report/report_${BUILD_NUMBER}.md
                        """
                    }
                }
            }
        }
        
        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: 'gu_pot/*/report/*.md', fingerprint: true
            }
        }
    }
    
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'gu_pot',
                reportFiles: '*/report/*.md',
                reportName: 'Alchemist Reports'
            ])
        }
    }
}
```

## Environment Variables

The CLI tool supports the following environment variables:

- `GITHUB_TOKEN`: GitHub personal access token for API access
- `ALCHEMIST_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ALCHEMIST_OUTPUT_FORMAT`: Default output format preference

## Error Handling

### Common CI Issues and Solutions

1. **Missing Evidence Paths**
   ```bash
   # Use validation mode to identify issues
   python report_synthesizer.py --experiment-dir $EXP_DIR --validate-only
   
   # Exit code 1 indicates validation failure
   if [ $? -ne 0 ]; then
     echo "Evidence validation failed - check experiment setup"
     exit 1
   fi
   ```

2. **Permission Issues**
   ```bash
   # Ensure scripts are executable
   chmod +x scripts/alchemist-faculty/report_synthesizer.py
   
   # Or run with python explicitly
   python scripts/alchemist-faculty/report_synthesizer.py
   ```

3. **Missing Dependencies**
   ```bash
   # Install dependencies in CI
   pip install PyYAML requests
   
   # Or use requirements file
   pip install -r scripts/requirements.txt
   ```

## Performance Considerations

- **Report generation time**: 2-10 seconds for 10-50 claims
- **Memory usage**: Minimal - processes claims sequentially
- **Scaling**: Linear with number of claims processed
- **Parallel processing**: Use separate jobs for multiple experiments

## Monitoring and Alerts

### Slack Integration Example

```yaml
- name: Notify on report generation
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: success
    text: '✅ Alchemist reports generated successfully'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

- name: Notify on validation failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    text: '❌ Alchemist evidence validation failed'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Testing in CI

```yaml
- name: Run Alchemist CLI tests
  run: |
    python tests/test_alchemist_report_synthesizer.py
    
- name: Test CLI with sample data
  run: |
    python scripts/alchemist-faculty/report_synthesizer.py \
      --manifest assets/experiments/school/test_manifest.yaml \
      --claims-dir assets/experiments/school/claims/ \
      --output /tmp/test_report.md \
      --verbose
```

## Security Considerations

- Store GitHub tokens as secrets, not in plain text
- Use least-privilege tokens with minimal required scopes
- Validate input paths to prevent directory traversal
- Run in isolated containers when possible
- Audit generated reports for sensitive information

This integration guide ensures the Alchemist report synthesis CLI tool can be effectively deployed in various CI/CD environments while maintaining security and reliability.
