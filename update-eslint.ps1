$excludes = @("monorepo-manager", "@dimaslanjaka/eslint-base-config")

$workspaces = yarn workspaces list --json | ConvertFrom-Json

foreach ($ws in $workspaces) {
    if ($excludes -notcontains $ws.name) {
        Write-Host "Adding eslint to $($ws.name)..."
        yarn workspace $ws.name add -D eslint@^9 --mode=skip-build
    } else {
        Write-Host "Skipping $($ws.name)..."
    }
}