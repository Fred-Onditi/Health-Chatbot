$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$result = @{
    success = $false
    repoUrl = $null
    ghUsername = $null
    errors = @()
}

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "git is not installed or not on PATH"
    }
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI (gh) is not installed. Install from https://cli.github.com/"
    }

    $auth = gh auth status 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "GitHub CLI is not authenticated. Run: gh auth login"
    }

    $ghUser = gh api user -q .login
    $result.ghUsername = $ghUser

    if (-not (Test-Path ".git")) {
        git init | Out-Null
    }

    git add app.py main.py requirements.txt example_questions.txt .gitignore *.json
    git add -A

    $status = git status --porcelain
    if ($status) {
        git commit -m @"
Add school health chatbot with Streamlit for health Q&A.

Includes FAQ matching, symptom info, wellness tips, and emergency detection.
"@
    }

    $remote = git remote get-url origin 2>$null
    if (-not $remote) {
        $repoName = "health-chatbot"
        gh repo create $repoName --public --source=. --remote=origin --description "School health chatbot with Streamlit" 2>$null
        if ($LASTEXITCODE -ne 0) {
            $repoName = "health-chatbot-data"
            gh repo create $repoName --public --source=. --remote=origin --description "School health chatbot with Streamlit"
        }
        if ($LASTEXITCODE -ne 0) {
            throw "Could not create GitHub repo. It may already exist under another name."
        }
    }

    $branch = git branch --show-current
    if (-not $branch) {
        git checkout -b main | Out-Null
        $branch = "main"
    }

    git push -u origin $branch
    if ($LASTEXITCODE -ne 0) {
        throw "git push failed"
    }

    $result.repoUrl = gh repo view --json url -q .url
    $result.success = $true
}
catch {
    $result.errors += $_.Exception.Message
}

$result | ConvertTo-Json -Depth 3 | Set-Content -Path "push_result.json" -Encoding UTF8
Write-Output ($result | ConvertTo-Json -Depth 3)
