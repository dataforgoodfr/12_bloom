# DO NOT USE THIS FILE DIRECTLY (it has not been tested)

param(
  [ValidateSet("actualize", "custom", "full_rebuild")]
  [string]$Mode = "actualize",

  [string]$Start = $null,
  [string]$End = $null,

  [string]$Target = "my_model+"
)

# Sécurité : forcer start/end si mode custom
if ($Mode -eq "custom" -and (-not $Start -or -not $End)) {
  Write-Error "❌ Le mode 'custom' nécessite obligatoirement les paramètres -Start et -End."
  exit 1
}

# Définir les variables d’environnement si nécessaire
if ($Mode -eq "full_rebuild" -or $Mode -eq "actualize") {
  $env:AIS_POSITION_CREATED_AT_FIRST = "2024-05-31 00:00:00+00"

  $endDate = (Get-Date).Date.AddDays(2).ToString("yyyy-MM-dd")
  $env:AIS_POSITION_CREATED_AT_END = "$endDate 00:00:00+00"
}

# Construction du bloc YAML pour --vars
$vars = "mode: `"$Mode`""
if ($Start) { $vars += "`nstart: `"$Start`"" }
if ($End)   { $vars += "`nend: `"$End`"" }

# Forcer BATCH_SIZE = 'day' si full_rebuild
if ($Mode -eq "full_rebuild") {
  $vars += "`nBATCH_SIZE: `"day`""
}

# Affichage des infos
Write-Host "▶ Running dbt in mode: $Mode"
Write-Host "▶ Target model(s): $Target"
Write-Host "▶ Variables:"
Write-Host $vars

# Exécution dbt
dbt runss -m $Target --event-time-start "$Start" --event-time-end "$End" --vars $vars