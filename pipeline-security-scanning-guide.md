# Adding Automated Security Scanning to CI/CD Pipelines

## Overview
Security scanning in CI/CD pipelines (DevSecOps) involves integrating automated security checks at various stages of the development lifecycle to identify vulnerabilities early when they're cheaper and easier to fix.

## Types of Security Scans

### 1. **SAST (Static Application Security Testing)**
- Scans source code for security vulnerabilities without executing it
- Identifies issues like SQL injection, XSS, hardcoded secrets
- Tools: SonarQube, Checkmarx, Semgrep, CodeQL

### 2. **DAST (Dynamic Application Security Testing)**
- Tests running applications for vulnerabilities
- Simulates attacks on deployed applications
- Tools: OWASP ZAP, Burp Suite

### 3. **SCA (Software Composition Analysis)**
- Scans dependencies and third-party libraries for known vulnerabilities
- Checks against CVE databases
- Tools: Snyk, Dependabot, OWASP Dependency-Check

### 4. **Container Scanning**
- Scans Docker images for vulnerabilities
- Checks base images and layers
- Tools: Trivy, Grype, Clair, Aqua Security

### 5. **Secret Scanning**
- Detects hardcoded secrets, API keys, passwords
- Tools: GitGuardian, TruffleHog, git-secrets

### 6. **Infrastructure as Code (IaC) Scanning**
- Scans Terraform, CloudFormation, Kubernetes manifests
- Tools: Checkov, tfsec, Terrascan

---

## Implementation Strategy

### The Security Scanning Pipeline Flow:
```
Code Commit → Secret Scan → SAST → Build → Container Scan → SCA → Deploy to Test → DAST → Deploy to Production
```

### Best Practices:
1. **Fail Fast**: Run quick scans (secrets, SAST) early
2. **Parallel Execution**: Run multiple scans simultaneously
3. **Threshold-Based Failures**: Fail builds on HIGH/CRITICAL issues only
4. **Developer Feedback**: Provide clear, actionable reports
5. **Continuous Improvement**: Review and tune scan rules regularly

---

## Practical Examples

### Example 1: GitHub Actions Pipeline with Security Scanning

```yaml
name: Secure CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  # Job 1: Secret Scanning
  secret-scan:
    name: Scan for Secrets
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for secret scanning

      # Scan for hardcoded secrets using TruffleHog
      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

      # Alternative: GitGuardian
      # - name: GitGuardian scan
      #   uses: GitGuardian/ggshield-action@v1
      #   env:
      #     GITHUB_PUSH_BEFORE_SHA: ${{ github.event.before }}
      #     GITHUB_PUSH_BASE_SHA: ${{ github.event.base }}
      #     GITHUB_DEFAULT_BRANCH: ${{ github.event.repository.default_branch }}
      #     GITGUARDIAN_API_KEY: ${{ secrets.GITGUARDIAN_API_KEY }}

  # Job 2: SAST - Static Code Analysis
  sast-scan:
    name: Static Application Security Testing
    runs-on: ubuntu-latest
    needs: secret-scan  # Only run if secret scan passes
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Option A: Semgrep (Free, Fast)
      - name: Semgrep Security Scan
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten
            p/cwe-top-25
        # Fail on HIGH severity only
        # continue-on-error: true  # Uncomment to not fail the build

      # Option B: CodeQL (GitHub Native)
      # - name: Initialize CodeQL
      #   uses: github/codeql-action/init@v3
      #   with:
      #     languages: javascript, python  # Adjust to your languages

      # - name: Autobuild
      #   uses: github/codeql-action/autobuild@v3

      # - name: Perform CodeQL Analysis
      #   uses: github/codeql-action/analyze@v3

      # Option C: SonarQube/SonarCloud
      # - name: SonarCloud Scan
      #   uses: SonarSource/sonarcloud-github-action@master
      #   env:
      #     GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      #     SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}

  # Job 3: Dependency Scanning (SCA)
  dependency-scan:
    name: Software Composition Analysis
    runs-on: ubuntu-latest
    needs: secret-scan
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Option A: Snyk (Popular, comprehensive)
      - name: Run Snyk to check for vulnerabilities
        uses: snyk/actions/node@master  # Change to python, docker, etc.
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
        # continue-on-error: true

      # Option B: OWASP Dependency-Check (Free)
      # - name: OWASP Dependency-Check
      #   uses: dependency-check/Dependency-Check_Action@main
      #   with:
      #     project: 'my-project'
      #     path: '.'
      #     format: 'HTML'
      #     args: >
      #       --failOnCVSS 7
      #       --enableRetired

      # Option C: GitHub Dependency Scanning (Native)
      # - name: Dependency Review
      #   uses: actions/dependency-review-action@v4
      #   with:
      #     fail-on-severity: high

  # Job 4: Build Application
  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: [sast-scan, dependency-scan]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Build application
        run: npm run build

      - name: Build Docker image
        run: |
          docker build -t myapp:${{ github.sha }} .
          docker save myapp:${{ github.sha }} -o myapp.tar

      - name: Upload Docker image artifact
        uses: actions/upload-artifact@v4
        with:
          name: docker-image
          path: myapp.tar

  # Job 5: Container Security Scanning
  container-scan:
    name: Container Image Scanning
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Download Docker image
        uses: actions/download-artifact@v4
        with:
          name: docker-image

      - name: Load Docker image
        run: docker load -i myapp.tar

      # Option A: Trivy (Fast, comprehensive, FREE)
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'  # Fail on vulnerabilities

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

      # Option B: Grype
      # - name: Scan image with Grype
      #   uses: anchore/scan-action@v3
      #   with:
      #     image: "myapp:${{ github.sha }}"
      #     fail-build: true
      #     severity-cutoff: high

      # Option C: Snyk Container
      # - name: Snyk Container Scan
      #   uses: snyk/actions/docker@master
      #   env:
      #     SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      #   with:
      #     image: myapp:${{ github.sha }}
      #     args: --severity-threshold=high

  # Job 6: IaC Scanning (if using Terraform/K8s)
  iac-scan:
    name: Infrastructure as Code Scanning
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Option A: Checkov (Multi-cloud, K8s, Dockerfile)
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: ./terraform
          framework: terraform
          soft_fail: false  # Fail on issues
          # skip_check: CKV_AWS_123  # Skip specific checks

      # Option B: tfsec (Terraform focused)
      # - name: tfsec
      #   uses: aquasecurity/tfsec-action@v1.0.0
      #   with:
      #     working_directory: ./terraform
      #     soft_fail: false

      # Option C: Terrascan
      # - name: Terrascan IaC scanner
      #   uses: tenable/terrascan-action@main
      #   with:
      #     iac_type: 'terraform'
      #     iac_dir: './terraform'
      #     policy_type: 'aws'
      #     fail_on_violations: true

  # Job 7: Deploy to Staging
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [container-scan, iac-scan]
    environment: staging
    steps:
      - name: Download Docker image
        uses: actions/download-artifact@v4
        with:
          name: docker-image

      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment..."
          # Add your deployment commands here

  # Job 8: DAST - Dynamic Security Testing
  dast-scan:
    name: Dynamic Application Security Testing
    runs-on: ubuntu-latest
    needs: deploy-staging
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # Option A: OWASP ZAP
      - name: OWASP ZAP Full Scan
        uses: zaproxy/action-full-scan@v0.10.0
        with:
          target: 'https://staging.myapp.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'  # Include API scan
        # allow_issue_writing: false  # Set to true to create GitHub issues

      # Option B: Nuclei (Fast template-based scanning)
      # - name: Nuclei Scan
      #   uses: projectdiscovery/nuclei-action@main
      #   with:
      #     target: https://staging.myapp.com
      #     severity: high,critical

  # Job 9: Security Report Generation
  security-report:
    name: Generate Security Report
    runs-on: ubuntu-latest
    needs: [sast-scan, dependency-scan, container-scan, dast-scan]
    if: always()
    steps:
      - name: Generate Security Summary
        run: |
          echo "## Security Scan Summary" >> $GITHUB_STEP_SUMMARY
          echo "✅ Secret Scanning: Completed" >> $GITHUB_STEP_SUMMARY
          echo "✅ SAST: Completed" >> $GITHUB_STEP_SUMMARY
          echo "✅ SCA: Completed" >> $GITHUB_STEP_SUMMARY
          echo "✅ Container Scan: Completed" >> $GITHUB_STEP_SUMMARY
          echo "✅ DAST: Completed" >> $GITHUB_STEP_SUMMARY
```

---

### Example 2: GitLab CI/CD Pipeline with Security

```yaml
# .gitlab-ci.yml

stages:
  - secrets
  - sast
  - build
  - scan
  - deploy
  - dast

variables:
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

# Secret Scanning
secret-detection:
  stage: secrets
  image: alpine:latest
  script:
    # Using GitLab's native secret detection
    - apk add --no-cache git
    - git clone https://github.com/trufflesecurity/trufflehog.git
    - cd trufflehog && ./trufflehog filesystem ../
  allow_failure: false
  # Alternatively use GitLab's built-in secret detection:
  # include:
  #   - template: Security/Secret-Detection.gitlab-ci.yml

# SAST - Static Application Security Testing
sast:
  stage: sast
  # GitLab provides built-in SAST
  include:
    - template: Security/SAST.gitlab-ci.yml
  variables:
    SAST_EXCLUDED_PATHS: "spec, test, tests, tmp"
  # Manual alternative:
  # image: returntocorp/semgrep
  # script:
  #   - semgrep --config=auto --json --output=sast-report.json .
  # artifacts:
  #   reports:
  #     sast: sast-report.json

# Dependency Scanning
dependency-scanning:
  stage: sast
  # GitLab provides built-in dependency scanning
  include:
    - template: Security/Dependency-Scanning.gitlab-ci.yml
  # Manual alternative with Snyk:
  # image: snyk/snyk:node
  # script:
  #   - snyk test --severity-threshold=high --json > dependency-report.json
  # artifacts:
  #   reports:
  #     dependency_scanning: dependency-report.json

# Build Docker Image
build-image:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $DOCKER_IMAGE .
    - docker push $DOCKER_IMAGE
  dependencies:
    - sast
    - dependency-scanning

# Container Scanning with Trivy
container-scan:
  stage: scan
  image: aquasec/trivy:latest
  script:
    - trivy image --severity HIGH,CRITICAL --exit-code 1 $DOCKER_IMAGE
  # GitLab built-in alternative:
  # include:
  #   - template: Security/Container-Scanning.gitlab-ci.yml

# IaC Scanning
iac-scan:
  stage: scan
  image: bridgecrew/checkov:latest
  script:
    - checkov -d ./terraform --framework terraform --output junitxml > checkov-report.xml
  artifacts:
    reports:
      junit: checkov-report.xml
  allow_failure: false

# Deploy to Staging
deploy-staging:
  stage: deploy
  environment:
    name: staging
  script:
    - echo "Deploying to staging..."
    # Add deployment commands
  only:
    - main

# DAST - Dynamic Application Security Testing
dast:
  stage: dast
  # GitLab provides built-in DAST
  include:
    - template: Security/DAST.gitlab-ci.yml
  variables:
    DAST_WEBSITE: https://staging.myapp.com
    DAST_FULL_SCAN_ENABLED: "true"
  # Manual alternative with OWASP ZAP:
  # image: owasp/zap2docker-stable
  # script:
  #   - zap-baseline.py -t https://staging.myapp.com -r zap-report.html
  # artifacts:
  #   paths:
  #     - zap-report.html
```

---

### Example 3: Jenkins Pipeline (Jenkinsfile)

```groovy
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "myapp:${env.BUILD_ID}"
        SNYK_TOKEN = credentials('snyk-token')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // Stage 1: Secret Scanning
        stage('Secret Scanning') {
            steps {
                script {
                    sh '''
                        docker run --rm -v $(pwd):/repo \
                        trufflesecurity/trufflehog:latest \
                        filesystem /repo --fail --json
                    '''
                }
            }
        }

        // Stage 2: SAST with SonarQube
        stage('SAST - SonarQube') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=myapp \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${SONAR_HOST_URL} \
                            -Dsonar.login=${SONAR_AUTH_TOKEN}
                        """
                    }
                }
            }
        }

        // Stage 3: Dependency Check
        stage('Dependency Scanning') {
            steps {
                // Using OWASP Dependency-Check
                dependencyCheck additionalArguments: '''
                    --scan .
                    --format HTML
                    --format JSON
                    --failOnCVSS 7
                ''', odcInstallation: 'OWASP-DC'

                dependencyCheckPublisher pattern: 'dependency-check-report.json'

                // Alternative: Snyk
                // sh 'snyk test --severity-threshold=high --json > snyk-report.json'
            }
        }

        // Stage 4: Build Application
        stage('Build') {
            steps {
                sh 'npm ci'
                sh 'npm run build'
            }
        }

        // Stage 5: Build Docker Image
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }

        // Stage 6: Container Scanning with Trivy
        stage('Container Scanning') {
            steps {
                sh """
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                    aquasec/trivy:latest image \
                    --severity HIGH,CRITICAL \
                    --exit-code 1 \
                    --no-progress \
                    ${DOCKER_IMAGE}
                """
            }
        }

        // Stage 7: IaC Scanning
        stage('IaC Security Scan') {
            steps {
                sh '''
                    docker run --rm -v $(pwd):/tf bridgecrew/checkov:latest \
                    -d /tf/terraform \
                    --framework terraform \
                    --output junitxml > checkov-report.xml
                '''
            }
        }

        // Stage 8: Deploy to Staging
        stage('Deploy to Staging') {
            steps {
                echo 'Deploying to staging...'
                // Add deployment commands
            }
        }

        // Stage 9: DAST with OWASP ZAP
        stage('DAST') {
            steps {
                sh '''
                    docker run --rm -v $(pwd):/zap/wrk:rw \
                    owasp/zap2docker-stable zap-baseline.py \
                    -t https://staging.myapp.com \
                    -r zap-report.html \
                    -x zap-report.xml
                '''
            }
        }
    }

    post {
        always {
            // Archive security reports
            archiveArtifacts artifacts: '**/zap-report.html, **/dependency-check-report.html', allowEmptyArchive: true

            // Publish test results
            junit '**/zap-report.xml, **/checkov-report.xml'
        }
        failure {
            emailext(
                subject: "Security Scan Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Security vulnerabilities detected. Check ${env.BUILD_URL} for details.",
                to: 'security-team@example.com'
            )
        }
    }
}
```

---

## Tool Comparison Matrix

| Tool | Type | Cost | Best For | Languages |
|------|------|------|----------|-----------|
| **Trivy** | Container/IaC | Free | Container & IaC scanning | All |
| **Snyk** | SCA/Container | Freemium | Dependency scanning | JS, Python, Java, .NET, Go, Ruby, PHP |
| **Semgrep** | SAST | Free | Fast SAST scanning | 30+ languages |
| **SonarQube** | SAST | Freemium | Code quality + security | 25+ languages |
| **OWASP ZAP** | DAST | Free | Web app penetration testing | N/A |
| **Checkov** | IaC | Free | Terraform, K8s, Dockerfile | IaC only |
| **TruffleHog** | Secrets | Free | Secret detection | All |
| **CodeQL** | SAST | Free (GitHub) | Deep code analysis | C/C++, C#, Go, Java, JS, Python, Ruby |

---

## Configuration Files for Security Tools

### 1. Trivy Configuration (.trivyignore)
```
# Ignore specific CVEs that are false positives or accepted risks
CVE-2023-12345
CVE-2023-67890

# Ignore by package
pkg:golang/example.com/package@1.0.0
```

### 2. Semgrep Rules (semgrep.yml)
```yaml
rules:
  - id: hardcoded-password
    pattern: password = "..."
    message: Possible hardcoded password
    severity: ERROR
    languages: [python, javascript]

  - id: sql-injection
    pattern: execute("SELECT * FROM users WHERE id = " + $VAR)
    message: Possible SQL injection
    severity: ERROR
    languages: [python, javascript]
```

### 3. OWASP ZAP Rules (.zap/rules.tsv)
```
# Ignore specific URLs or rules
10021	IGNORE	https://staging.myapp.com/health
10096	IGNORE	https://staging.myapp.com/metrics
```

### 4. Checkov Skip Checks
```hcl
# In Terraform files
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"

  #checkov:skip=CKV_AWS_18:This bucket intentionally allows public access
  acl = "public-read"
}
```

---

## Security Scan Metrics to Track

1. **Mean Time to Remediate (MTTR)**: Time from vulnerability detection to fix
2. **Vulnerability Density**: Number of vulnerabilities per 1000 lines of code
3. **False Positive Rate**: Percentage of reported issues that are false positives
4. **Critical/High Severity Trends**: Track over time
5. **Scan Coverage**: Percentage of code/dependencies scanned
6. **Policy Compliance**: Percentage of scans passing security policies

---

## Interview Talking Points

When discussing security scanning in interviews, mention:

1. **Why You Implemented It**:
   - "To shift security left and catch vulnerabilities early in the development cycle"
   - "Reduce security debt and prevent production incidents"
   - "Meet compliance requirements (SOC2, PCI-DSS, etc.)"

2. **What You Implemented**:
   - "Integrated Trivy for container scanning, catching 15+ critical CVEs before production"
   - "Added Snyk for dependency scanning, reducing vulnerable dependencies by 80%"
   - "Implemented SAST with Semgrep, creating custom rules for our framework"

3. **Results/Impact**:
   - "Reduced security incidents in production by 70%"
   - "Decreased time to detect vulnerabilities from weeks to minutes"
   - "Achieved compliance certification requirements"

4. **Challenges Overcome**:
   - "Tuned scan rules to reduce false positives from 40% to <10%"
   - "Optimized scan times to not slow down developer workflow"
   - "Created developer-friendly reports with clear remediation steps"

---

## Quick Start Commands

### Test Trivy Locally
```bash
# Scan a Docker image
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image nginx:latest

# Scan local filesystem
docker run --rm -v $(pwd):/app aquasec/trivy:latest fs /app
```

### Test Semgrep Locally
```bash
# Install
pip install semgrep

# Run security scan
semgrep --config=auto .

# Run OWASP Top 10 rules
semgrep --config=p/owasp-top-ten .
```

### Test Secret Scanning
```bash
# TruffleHog
docker run --rm -v $(pwd):/repo trufflesecurity/trufflehog:latest filesystem /repo

# GitLeaks
docker run --rm -v $(pwd):/path zricethezav/gitleaks:latest detect --source /path
```

---

## Next Steps

1. Choose 2-3 tools based on your tech stack
2. Start with non-blocking scans (warnings only)
3. Tune rules to reduce false positives
4. Gradually enforce blocking on HIGH/CRITICAL
5. Train team on reading and fixing security issues
6. Set up automated reporting and dashboards
