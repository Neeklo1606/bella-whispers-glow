# Bella Deployment Script for Windows/Cursor
# This script commits changes, pushes to git, and deploys to server

param(
    [string]$CommitMessage = "Deploy: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    [switch]$SkipCommit = $false
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

Write-Info "=== Bella Deployment Script ==="
Write-Host ""

# Step 1: Check git status
Write-Info "Step 1: Checking git status..."
$gitStatus = git status --porcelain

if ($gitStatus -and -not $SkipCommit) {
    Write-Info "Uncommitted changes detected"
    
    # Step 2: Add all changes
    Write-Info "Step 2: Staging changes..."
    git add .
    
    # Step 3: Commit changes
    Write-Info "Step 3: Committing changes..."
    git commit -m $CommitMessage
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to commit changes"
        exit 1
    }
    
    Write-Info "Changes committed successfully"
} elseif ($SkipCommit) {
    Write-Warning "Skipping commit (--SkipCommit flag set)"
} else {
    Write-Info "No uncommitted changes"
}

# Step 4: Push to repository
if (-not $SkipCommit) {
    Write-Info "Step 4: Pushing to repository..."
    git push origin main 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        # Try master branch if main fails
        git push origin master 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to push to repository"
            exit 1
        }
    }
    
    Write-Info "Code pushed to repository"
}

# Step 5: Deploy to server
Write-Info "Step 5: Deploying to server..."
Write-Host ""

$sshKey = "$env:USERPROFILE\.ssh\id_ed25519"
$server = "root@155.212.210.214"
$deployScript = "/var/www/bella/deploy.sh"

# Execute deployment script on server (use deployment/deploy.sh directly for reliability)
$deployScriptReal = "/var/www/bella/deployment/deploy.sh"
ssh -i $sshKey $server "bash $deployScriptReal"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment failed"
    exit 1
}

Write-Host ""
Write-Info "Deployment completed successfully!"
Write-Info "Application is available at: https://app.bellahasias.ru"
