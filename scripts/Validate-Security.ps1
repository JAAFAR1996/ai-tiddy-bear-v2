# Security Validation Script for AI Teddy Bear Docker Infrastructure
# PowerShell version for Windows environments

param(
    [switch]$Detailed = $false
)

# Colors for output
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue
$White = [System.ConsoleColor]::White

function Write-ColoredOutput {
    param(
        [string]$Message,
        [System.ConsoleColor]$Color = $White
    )
    $originalColor = [Console]::ForegroundColor
    [Console]::ForegroundColor = $Color
    Write-Host $Message
    [Console]::ForegroundColor = $originalColor
}

function Log-Info { param([string]$Message) Write-ColoredOutput "[INFO] $Message" $Blue }
function Log-Success { param([string]$Message) Write-ColoredOutput "[SUCCESS] $Message" $Green }
function Log-Warning { param([string]$Message) Write-ColoredOutput "[WARNING] $Message" $Yellow }
function Log-Error { param([string]$Message) Write-ColoredOutput "[ERROR] $Message" $Red }

# Validation counters
$script:TotalChecks = 0
$script:PassedChecks = 0
$script:FailedChecks = 0

function Increment-Check {
    param([string]$Result)
    $script:TotalChecks++
    if ($Result -eq "pass") {
        $script:PassedChecks++
    } else {
        $script:FailedChecks++
    }
}

function Test-DockerImages {
    Log-Info "Validating Docker image security..."

    $dockerfiles = @("Dockerfile", "Dockerfile.production")

    foreach ($dockerfile in $dockerfiles) {
        if (Test-Path $dockerfile) {
            Log-Success "Found $dockerfile"
            Increment-Check "pass"

            $content = Get-Content $dockerfile -Raw

            # Check for pinned base images (no latest tags)
            if ($content -match "FROM.*:latest") {
                Log-Error "$dockerfile uses latest tag - security violation"
                Increment-Check "fail"
            } else {
                Log-Success "$dockerfile uses pinned base image tags"
                Increment-Check "pass"
            }

            # Check for non-root user
            if ($content -match "USER.*[^0]") {
                Log-Success "$dockerfile runs as non-root user"
                Increment-Check "pass"
            } else {
                Log-Error "$dockerfile missing non-root user directive"
                Increment-Check "fail"
            }

            # Check for SHA256 digests
            if ($content -match "@sha256:") {
                Log-Success "$dockerfile uses SHA256 pinned images"
                Increment-Check "pass"
            } else {
                Log-Error "$dockerfile missing SHA256 pinned images"
                Increment-Check "fail"
            }

            # Check for multi-stage builds
            $fromCount = ([regex]::Matches($content, "FROM.*as.*")).Count
            if ($fromCount -ge 2) {
                Log-Success "$dockerfile uses multi-stage builds"
                Increment-Check "pass"
            } else {
                Log-Warning "$dockerfile should use multi-stage builds"
                Increment-Check "fail"
            }

        } else {
            Log-Error "$dockerfile not found"
            Increment-Check "fail"
        }
    }
}

function Test-DockerCompose {
    Log-Info "Validating Docker Compose security configurations..."

    $composeFiles = @("docker-compose.prod.yml", "docker-compose.production.yml")

    foreach ($composeFile in $composeFiles) {
        if (Test-Path $composeFile) {
            Log-Success "Found $composeFile"
            Increment-Check "pass"

            $content = Get-Content $composeFile -Raw

            # Check for non-root users
            if ($content -match "user:.*[^:]0") {
                Log-Success "$composeFile configures non-root users"
                Increment-Check "pass"
            } else {
                Log-Error "$composeFile missing non-root user configurations"
                Increment-Check "fail"
            }

            # Check for security options
            if ($content -match "security_opt:" -and $content -match "no-new-privileges:true") {
                Log-Success "$composeFile has security options configured"
                Increment-Check "pass"
            } else {
                Log-Error "$composeFile missing security options"
                Increment-Check "fail"
            }

            # Check for capability dropping
            if ($content -match "cap_drop:" -and $content -match "ALL") {
                Log-Success "$composeFile drops all capabilities"
                Increment-Check "pass"
            } else {
                Log-Error "$composeFile missing capability restrictions"
                Increment-Check "fail"
            }

            # Check for localhost-only port bindings
            if ($content -match "127\.0\.0\.1:") {
                Log-Success "$composeFile binds sensitive ports to localhost only"
                Increment-Check "pass"
            } else {
                Log-Warning "$composeFile may expose ports to all interfaces"
                Increment-Check "fail"
            }

        } else {
            Log-Error "$composeFile not found"
            Increment-Check "fail"
        }
    }
}

function Test-EntrypointScript {
    Log-Info "Validating docker-entrypoint.sh security..."

    $entrypoint = "docker-entrypoint.sh"
    if (Test-Path $entrypoint) {
        Log-Success "Found $entrypoint"
        Increment-Check "pass"

        $content = Get-Content $entrypoint -Raw

        # Check for strict error handling
        if ($content -match "set -euo pipefail") {
            Log-Success "$entrypoint uses strict error handling"
            Increment-Check "pass"
        } else {
            Log-Error "$entrypoint missing strict error handling"
            Increment-Check "fail"
        }

        # Check for signal handling
        if ($content -match "trap.*cleanup" -and $content -match "SIGTERM|SIGINT") {
            Log-Success "$entrypoint has proper signal handling"
            Increment-Check "pass"
        } else {
            Log-Error "$entrypoint missing signal handling"
            Increment-Check "fail"
        }

        # Check for environment validation
        if ($content -match "validate_environment") {
            Log-Success "$entrypoint validates environment variables"
            Increment-Check "pass"
        } else {
            Log-Error "$entrypoint missing environment validation"
            Increment-Check "fail"
        }

        # Check for security checks
        if ($content -match "security_checks") {
            Log-Success "$entrypoint includes security checks"
            Increment-Check "pass"
        } else {
            Log-Error "$entrypoint missing security checks"
            Increment-Check "fail"
        }

    } else {
        Log-Error "$entrypoint not found"
        Increment-Check "fail"
    }
}

function Test-HardcodedSecrets {
    Log-Info "Checking for hardcoded secrets..."

    $secretPatterns = @(
        "password.*=.*[`"'][^`"']*[`"']",
        "secret.*=.*[`"'][^`"']*[`"']",
        "key.*=.*[`"'][^`"']*[`"']",
        "token.*=.*[`"'][^`"']*[`"']",
        "api_key.*=.*[`"'][^`"']*[`"']"
    )

    $filesToCheck = @("Dockerfile", "Dockerfile.production", "docker-compose.prod.yml", "docker-compose.production.yml", "docker-entrypoint.sh")
    $secretsFound = $false

    foreach ($file in $filesToCheck) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            foreach ($pattern in $secretPatterns) {
                if ($content -match $pattern -and $content -notmatch "{\$" -and $content -notmatch "example" -and $content -notmatch "#") {
                    Log-Error "Potential hardcoded secret found in $file"
                    $secretsFound = $true
                }
            }
        }
    }

    if (-not $secretsFound) {
        Log-Success "No hardcoded secrets detected"
        Increment-Check "pass"
    } else {
        Increment-Check "fail"
    }
}

function Test-SecurityScanning {
    Log-Info "Validating security scanning integration..."

    $dockerfiles = @("Dockerfile", "Dockerfile.production")
    foreach ($dockerfile in $dockerfiles) {
        if (Test-Path $dockerfile) {
            $content = Get-Content $dockerfile -Raw

            # Check for Trivy integration
            if ($content -match "trivy") {
                Log-Success "$dockerfile includes Trivy security scanning"
                Increment-Check "pass"
            } else {
                Log-Error "$dockerfile missing Trivy security scanning"
                Increment-Check "fail"
            }

            # Check for security scanning stage
            if ($content -match "security-scanner") {
                Log-Success "$dockerfile has dedicated security scanning stage"
                Increment-Check "pass"
            } else {
                Log-Error "$dockerfile missing security scanning stage"
                Increment-Check "fail"
            }
        }
    }
}

function Show-Summary {
    Write-Host ""
    Write-ColoredOutput "========================================" $Blue
    Write-ColoredOutput "SECURITY VALIDATION SUMMARY" $Blue
    Write-ColoredOutput "========================================" $Blue
    Write-Host "Total checks: $script:TotalChecks"
    Write-Host "Passed: $script:PassedChecks"
    Write-Host "Failed: $script:FailedChecks"

    if ($script:TotalChecks -gt 0) {
        $passPercentage = [math]::Round(($script:PassedChecks / $script:TotalChecks) * 100, 1)
        Write-Host "Pass rate: $passPercentage%"

        if ($script:FailedChecks -eq 0) {
            Log-Success "ALL SECURITY CHECKS PASSED! 🎉"
            Write-Host ""
            Write-ColoredOutput "✅ Container runs as non-root user" $Green
            Write-ColoredOutput "✅ All base images are pinned to exact versions" $Green
            Write-ColoredOutput "✅ Security scanning is integrated" $Green
            Write-ColoredOutput "✅ Proper signal handling implemented" $Green
            Write-ColoredOutput "✅ No hardcoded secrets detected" $Green
            Write-ColoredOutput "✅ Security options are configured" $Green
            return 0
        } elseif ($passPercentage -ge 80) {
            Log-Warning "SECURITY VALIDATION PASSED WITH WARNINGS"
            Write-Host "Some non-critical security issues were found but overall security posture is good."
            return 1
        } else {
            Log-Error "SECURITY VALIDATION FAILED"
            Write-Host "Critical security issues were found that must be addressed."
            return 2
        }
    }
    return 2
}

# Main execution
Write-Host "========================================"
Write-Host "AI Teddy Bear Security Validation Report"
Write-Host "========================================"
Write-Host "Date: $(Get-Date)"
Write-Host "Validating Docker infrastructure security..."
Write-Host ""

# Run all validation checks
Test-DockerImages
Test-DockerCompose
Test-EntrypointScript
Test-HardcodedSecrets
Test-SecurityScanning

# Show final summary
$exitCode = Show-Summary
exit $exitCode
