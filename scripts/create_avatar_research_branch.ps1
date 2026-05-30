param(
    [string]$BranchName = "feature/avatar-research"
)

$insideWorkTree = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0 -or $insideWorkTree.Trim() -ne "true") {
    Write-Error "This workspace is not a Git repository. Initialize Git or run this inside the project repository first."
    exit 1
}

git checkout -b $BranchName
New-Item -ItemType Directory -Force -Path "experiments/avatar-research" | Out-Null
@"
# Avatar Research

Experimental MediaPipe, pose dataset, VRM, and avatar playback work belongs here.

Do not import this folder from production frontend or backend code.
"@ | Set-Content -Path "experiments/avatar-research/README.md" -Encoding utf8

git status --short
