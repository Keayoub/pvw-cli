<#
.SYNOPSIS
    Exemple d'automatisation complète de synchronisation UC → Glossaires Classiques

.DESCRIPTION
    Ce script démontre un workflow complet d'entreprise pour la synchronisation
    des termes métier entre Unified Catalog et les glossaires classiques.
    
    Scénario : Une entreprise avec plusieurs domaines métier qui souhaite :
    - Maintenir une cohérence entre UC et glossaires classiques
    - Générer des rapports de synchronisation
    - Envoyer des notifications en cas d'échec
    - Logger tous les événements pour audit

.EXAMPLE
    .\Complete-Sync-Example.ps1

.NOTES
    Auteur: Purview CLI Team
    Version: 1.0.0
    Date: 2025-01-15
#>

# ====================================================================
# CONFIGURATION
# ====================================================================

$Config = @{
    # Domaines à synchroniser avec leurs glossaires cibles
    Domains = @(
        @{
            Id = "domain-sales-guid-123"
            Name = "Sales"
            GlossaryGuid = "glossary-sales-guid-456"
            CreateGlossary = $false
            UpdateExisting = $true
            Enabled = $true
        },
        @{
            Id = "domain-marketing-guid-789"
            Name = "Marketing"
            GlossaryGuid = $null  # Auto-détection
            CreateGlossary = $true
            UpdateExisting = $true
            Enabled = $true
        },
        @{
            Id = "domain-finance-guid-012"
            Name = "Finance"
            GlossaryGuid = "glossary-finance-guid-345"
            CreateGlossary = $false
            UpdateExisting = $false  # Seulement création
            Enabled = $true
        },
        @{
            Id = "domain-hr-guid-678"
            Name = "Human Resources"
            GlossaryGuid = $null
            CreateGlossary = $true
            UpdateExisting = $true
            Enabled = $false  # Temporairement désactivé
        }
    )
    
    # Configuration des logs
    Logging = @{
        Directory = "C:\Logs\Purview\Sync"
        MaxSizeMB = 10
        RetentionDays = 30
        Level = "INFO"  # DEBUG, INFO, WARNING, ERROR
    }
    
    # Configuration des rapports
    Reports = @{
        Directory = "C:\Reports\Purview\Sync"
        GenerateHTML = $true
        GenerateCSV = $true
        IncludeDetails = $true
    }
    
    # Configuration des notifications
    Notifications = @{
        Email = @{
            Enabled = $true
            SmtpServer = "smtp.company.com"
            From = "purview-sync@company.com"
            To = @("data-governance@company.com", "admin@company.com")
            OnSuccess = $false
            OnFailure = $true
        }
        Teams = @{
            Enabled = $true
            WebhookUrl = "https://company.webhook.office.com/webhookb2/..."
            OnSuccess = $false
            OnFailure = $true
        }
    }
    
    # Options générales
    General = @{
        DryRun = $false
        PauseBetweenDomains = 3  # secondes
        MaxRetries = 3
        RetryDelay = 5  # secondes
    }
}

# ====================================================================
# FONCTIONS UTILITAIRES
# ====================================================================

function Initialize-Environment {
    # Créer les répertoires nécessaires
    @($Config.Logging.Directory, $Config.Reports.Directory) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
            Write-Host "✓ Répertoire créé: $_" -ForegroundColor Green
        }
    }
    
    # Nettoyer les anciens logs
    $cutoffDate = (Get-Date).AddDays(-$Config.Logging.RetentionDays)
    Get-ChildItem -Path $Config.Logging.Directory -Filter "*.log" |
        Where-Object { $_.LastWriteTime -lt $cutoffDate } |
        Remove-Item -Force
}

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("DEBUG", "INFO", "WARNING", "ERROR")]
        [string]$Level = "INFO",
        [string]$LogFile
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Écrire dans le fichier
    Add-Content -Path $LogFile -Value $logMessage
    
    # Afficher selon le niveau configuré
    $levelOrder = @("DEBUG", "INFO", "WARNING", "ERROR")
    if ($levelOrder.IndexOf($Level) -ge $levelOrder.IndexOf($Config.Logging.Level)) {
        $color = switch ($Level) {
            "DEBUG"   { "Gray" }
            "INFO"    { "White" }
            "WARNING" { "Yellow" }
            "ERROR"   { "Red" }
        }
        Write-Host $logMessage -ForegroundColor $color
    }
}

function Send-EmailNotification {
    param(
        [string]$Subject,
        [string]$Body,
        [switch]$IsError
    )
    
    if (-not $Config.Notifications.Email.Enabled) {
        return
    }
    
    if ($IsError -and -not $Config.Notifications.Email.OnFailure) {
        return
    }
    
    if (-not $IsError -and -not $Config.Notifications.Email.OnSuccess) {
        return
    }
    
    try {
        $emailParams = @{
            SmtpServer = $Config.Notifications.Email.SmtpServer
            From = $Config.Notifications.Email.From
            To = $Config.Notifications.Email.To
            Subject = $Subject
            Body = $Body
            BodyAsHtml = $true
        }
        
        Send-MailMessage @emailParams
        Write-Log "Email envoyé: $Subject" -Level INFO -LogFile $script:LogFile
    }
    catch {
        Write-Log "Erreur d'envoi d'email: $_" -Level ERROR -LogFile $script:LogFile
    }
}

function Send-TeamsNotification {
    param(
        [string]$Title,
        [string]$Message,
        [string]$Color = "0078D4",  # Bleu par défaut
        [switch]$IsError
    )
    
    if (-not $Config.Notifications.Teams.Enabled) {
        return
    }
    
    if ($IsError -and -not $Config.Notifications.Teams.OnFailure) {
        return
    }
    
    if (-not $IsError -and -not $Config.Notifications.Teams.OnSuccess) {
        return
    }
    
    $payload = @{
        "@type" = "MessageCard"
        "@context" = "https://schema.org/extensions"
        "themeColor" = if ($IsError) { "FF0000" } else { $Color }
        "title" = $Title
        "text" = $Message
        "sections" = @(
            @{
                "activityTitle" = "Purview Sync"
                "activitySubtitle" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                "activityImage" = "https://docs.microsoft.com/en-us/azure/purview/media/overview/purview-logo.png"
            }
        )
    } | ConvertTo-Json -Depth 10
    
    try {
        Invoke-RestMethod -Uri $Config.Notifications.Teams.WebhookUrl `
                          -Method Post `
                          -Body $payload `
                          -ContentType "application/json"
        Write-Log "Notification Teams envoyée: $Title" -Level INFO -LogFile $script:LogFile
    }
    catch {
        Write-Log "Erreur d'envoi de notification Teams: $_" -Level ERROR -LogFile $script:LogFile
    }
}

function Sync-Domain {
    param(
        [hashtable]$Domain,
        [int]$RetryCount = 0
    )
    
    Write-Log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -Level INFO -LogFile $script:LogFile
    Write-Log "Synchronisation: $($Domain.Name) ($($Domain.Id))" -Level INFO -LogFile $script:LogFile
    Write-Log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -Level INFO -LogFile $script:LogFile
    
    # Construire la commande
    $cmd = "pvw uc term sync-classic --domain-id `"$($Domain.Id)`""
    
    if ($Domain.GlossaryGuid) {
        $cmd += " --glossary-guid `"$($Domain.GlossaryGuid)`""
    }
    
    if ($Domain.CreateGlossary) {
        $cmd += " --create-glossary"
    }
    
    if ($Domain.UpdateExisting) {
        $cmd += " --update-existing"
    }
    
    if ($Config.General.DryRun) {
        $cmd += " --dry-run"
    }
    
    Write-Log "Commande: $cmd" -Level DEBUG -LogFile $script:LogFile
    
    try {
        # Exécuter la commande
        $output = Invoke-Expression $cmd 2>&1 | Out-String
        
        # Parser les statistiques
        $stats = @{
            Created = 0
            Updated = 0
            Skipped = 0
            Failed = 0
        }
        
        if ($output -match "Created\s+(\d+)") { $stats.Created = [int]$matches[1] }
        if ($output -match "Updated\s+(\d+)") { $stats.Updated = [int]$matches[1] }
        if ($output -match "Skipped\s+(\d+)") { $stats.Skipped = [int]$matches[1] }
        if ($output -match "Failed\s+(\d+)") { $stats.Failed = [int]$matches[1] }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✓ Succès pour $($Domain.Name)" -Level INFO -LogFile $script:LogFile
            Write-Log "  Créés: $($stats.Created) | Mis à jour: $($stats.Updated) | Ignorés: $($stats.Skipped) | Échecs: $($stats.Failed)" `
                      -Level INFO -LogFile $script:LogFile
            
            return @{
                Success = $true
                Stats = $stats
                Output = $output
            }
        }
        else {
            throw "Exit code: $LASTEXITCODE"
        }
    }
    catch {
        Write-Log "✗ Échec pour $($Domain.Name): $_" -Level ERROR -LogFile $script:LogFile
        
        # Retry logic
        if ($RetryCount -lt $Config.General.MaxRetries) {
            Write-Log "Nouvelle tentative ($($RetryCount + 1)/$($Config.General.MaxRetries))..." `
                      -Level WARNING -LogFile $script:LogFile
            Start-Sleep -Seconds $Config.General.RetryDelay
            return Sync-Domain -Domain $Domain -RetryCount ($RetryCount + 1)
        }
        
        return @{
            Success = $false
            Error = $_
            Output = $output
        }
    }
}

function Generate-HTMLReport {
    param(
        [array]$Results,
        [datetime]$StartTime,
        [datetime]$EndTime
    )
    
    $duration = $EndTime - $StartTime
    $totalDomains = $Results.Count
    $successDomains = ($Results | Where-Object { $_.Success }).Count
    $failedDomains = $totalDomains - $successDomains
    
    $totalCreated = ($Results | Where-Object { $_.Success } | ForEach-Object { $_.Stats.Created } | Measure-Object -Sum).Sum
    $totalUpdated = ($Results | Where-Object { $_.Success } | ForEach-Object { $_.Stats.Updated } | Measure-Object -Sum).Sum
    $totalSkipped = ($Results | Where-Object { $_.Success } | ForEach-Object { $_.Stats.Skipped } | Measure-Object -Sum).Sum
    $totalFailed = ($Results | Where-Object { $_.Success } | ForEach-Object { $_.Stats.Failed } | Measure-Object -Sum).Sum
    
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Purview Sync Report - $(Get-Date -Format 'yyyy-MM-dd')</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #0078D4; border-bottom: 3px solid #0078D4; padding-bottom: 10px; }
        h2 { color: #333; margin-top: 30px; }
        .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }
        .metric { background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 36px; font-weight: bold; color: #0078D4; }
        .metric-label { font-size: 14px; color: #666; margin-top: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .warning { background-color: #fff3cd; color: #856404; }
        .danger { background-color: #f8d7da; color: #721c24; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #0078D4; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .status-success { color: #28a745; font-weight: bold; }
        .status-failed { color: #dc3545; font-weight: bold; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Purview Sync Report</h1>
        <p><strong>Date:</strong> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p><strong>Durée:</strong> $($duration.ToString('hh\:mm\:ss'))</p>
        
        <h2>Résumé global</h2>
        <div class="summary">
            <div class="metric">
                <div class="metric-value">$totalDomains</div>
                <div class="metric-label">Domaines traités</div>
            </div>
            <div class="metric success">
                <div class="metric-value">$totalCreated</div>
                <div class="metric-label">Termes créés</div>
            </div>
            <div class="metric warning">
                <div class="metric-value">$totalUpdated</div>
                <div class="metric-label">Termes mis à jour</div>
            </div>
            <div class="metric danger">
                <div class="metric-value">$failedDomains</div>
                <div class="metric-label">Échecs</div>
            </div>
        </div>
        
        <h2>Détails par domaine</h2>
        <table>
            <thead>
                <tr>
                    <th>Domaine</th>
                    <th>Status</th>
                    <th>Créés</th>
                    <th>Mis à jour</th>
                    <th>Ignorés</th>
                    <th>Échecs</th>
                </tr>
            </thead>
            <tbody>
"@
    
    foreach ($result in $Results) {
        $statusClass = if ($result.Success) { "status-success" } else { "status-failed" }
        $statusText = if ($result.Success) { "✓ Succès" } else { "✗ Échec" }
        
        $html += @"
                <tr>
                    <td>$($result.DomainName)</td>
                    <td class="$statusClass">$statusText</td>
                    <td>$($result.Stats.Created)</td>
                    <td>$($result.Stats.Updated)</td>
                    <td>$($result.Stats.Skipped)</td>
                    <td>$($result.Stats.Failed)</td>
                </tr>
"@
    }
    
    $html += @"
            </tbody>
        </table>
        
        <div class="footer">
            <p>Généré automatiquement par Purview CLI Sync Automation</p>
            <p>Log complet disponible: $script:LogFile</p>
        </div>
    </div>
</body>
</html>
"@
    
    $reportPath = Join-Path $Config.Reports.Directory "sync-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').html"
    $html | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Log "Rapport HTML généré: $reportPath" -Level INFO -LogFile $script:LogFile
    
    return $reportPath
}

# ====================================================================
# SCRIPT PRINCIPAL
# ====================================================================

# Initialisation
$script:LogFile = Join-Path $Config.Logging.Directory "sync-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
Initialize-Environment

Write-Log "═══════════════════════════════════════════════════════════" -Level INFO -LogFile $script:LogFile
Write-Log "  Démarrage de la synchronisation automatique" -Level INFO -LogFile $script:LogFile
Write-Log "═══════════════════════════════════════════════════════════" -Level INFO -LogFile $script:LogFile

if ($Config.General.DryRun) {
    Write-Log "⚠ MODE DRY-RUN ACTIVÉ - Aucune modification ne sera appliquée" -Level WARNING -LogFile $script:LogFile
}

$startTime = Get-Date

# Filtrer les domaines activés
$enabledDomains = $Config.Domains | Where-Object { $_.Enabled }
Write-Log "Domaines à traiter: $($enabledDomains.Count)" -Level INFO -LogFile $script:LogFile

# Synchroniser chaque domaine
$results = @()
foreach ($domain in $enabledDomains) {
    $result = Sync-Domain -Domain $domain
    $results += @{
        DomainName = $domain.Name
        DomainId = $domain.Id
        Success = $result.Success
        Stats = $result.Stats
        Error = $result.Error
        Output = $result.Output
    }
    
    # Pause entre les domaines
    if ($domain -ne $enabledDomains[-1]) {
        Start-Sleep -Seconds $Config.General.PauseBetweenDomains
    }
}

$endTime = Get-Date
$duration = $endTime - $startTime

# Générer les rapports
if ($Config.Reports.GenerateHTML) {
    $reportPath = Generate-HTMLReport -Results $results -StartTime $startTime -EndTime $endTime
}

# Statistiques finales
$successCount = ($results | Where-Object { $_.Success }).Count
$failedCount = $results.Count - $successCount

Write-Log "═══════════════════════════════════════════════════════════" -Level INFO -LogFile $script:LogFile
Write-Log "  RÉSUMÉ FINAL" -Level INFO -LogFile $script:LogFile
Write-Log "═══════════════════════════════════════════════════════════" -Level INFO -LogFile $script:LogFile
Write-Log "Durée totale: $($duration.ToString('hh\:mm\:ss'))" -Level INFO -LogFile $script:LogFile
Write-Log "Domaines traités: $($results.Count)" -Level INFO -LogFile $script:LogFile
Write-Log "Succès: $successCount" -Level INFO -LogFile $script:LogFile
Write-Log "Échecs: $failedCount" -Level $(if ($failedCount -gt 0) { "ERROR" } else { "INFO" }) -LogFile $script:LogFile

# Notifications
if ($failedCount -gt 0) {
    $subject = "⚠ Échecs de synchronisation Purview"
    $body = @"
<h2>Alertes de synchronisation</h2>
<p><strong>$failedCount</strong> domaine(s) ont échoué lors de la synchronisation.</p>
<p>Consultez le rapport complet: <a href="file:///$reportPath">$reportPath</a></p>
<p>Log: <a href="file:///$script:LogFile">$script:LogFile</a></p>
"@
    Send-EmailNotification -Subject $subject -Body $body -IsError
    Send-TeamsNotification -Title $subject -Message "Échecs: $failedCount domaines" -IsError
}
elseif ($Config.Notifications.Email.OnSuccess) {
    $subject = "✅ Synchronisation Purview réussie"
    $body = @"
<h2>Synchronisation complétée avec succès</h2>
<p>Tous les domaines ont été synchronisés correctement.</p>
<p>Rapport: <a href="file:///$reportPath">$reportPath</a></p>
"@
    Send-EmailNotification -Subject $subject -Body $body
    Send-TeamsNotification -Title $subject -Message "Tous les domaines synchronisés avec succès"
}

Write-Log "Synchronisation terminée!" -Level INFO -LogFile $script:LogFile

# Code de sortie
exit $(if ($failedCount -gt 0) { 1 } else { 0 })
