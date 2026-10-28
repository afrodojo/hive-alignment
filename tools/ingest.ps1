param(
  [Parameter(Mandatory=$true)] [string]$Title,
  [Parameter(Mandatory=$true)] [string]$Author,
  [Parameter(Mandatory=$true)] [string]$Type, # Book, Publication, Article, Lecture
  [Parameter(Mandatory=$true)] [string]$Category, # Autonomic Science, Strength, Focus, etc.
  [Parameter(Mandatory=$true)] [string]$Summary,
  [Parameter(Mandatory=$true)] [string]$Takeaway,
  [Parameter(Mandatory=$false)] [string]$Tag = "General"
)

$jsonPath = "docs/data/knowledge.json"
$items = @()
if (Test-Path $jsonPath) {
  $items = Get-Content $jsonPath -Raw | ConvertFrom-Json
}

$newItem = [PSCustomObject]@{
  id          = ($Title.ToLower() -replace '[^a-z0-9]', '-').Substring(0, [Math]::Min(25, $Title.Length))
  title       = $Title
  type        = $Type
  author      = $Author
  category    = $Category
  date_added  = (Get-Date -Format "yyyy-MM-dd")
  summary     = $Summary
  takeaway    = $Takeaway
  tag         = $Tag
}

$items += $newItem
$items | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding utf8
Write-Host "Successfully ingested: '$Title' into Knowledge Vault!" -ForegroundColor Green
