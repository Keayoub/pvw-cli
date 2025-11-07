<#
.SYNOPSIS
    Script de synchronisation automatique des termes Unified Catalog vers les glossaires classiques

.DESCRIPTION
    Ce script automatise la synchronisation des termes métier du Unified Catalog de Microsoft Purview
    vers les glossaires classiques. Il peut être planifié pour maintenir une cohérence entre les deux systèmes.

.PARAMETER DomainIds
    Liste des GUIDs de domaines UC à synchroniser. Si vide, synchronise tous les domaines accessibles.

.PARAMETER CreateGlossaries
    Si spécifié, crée automatiquement les glossaires classiques pour les domaines qui n'en ont pas.

.PARAMETER UpdateExisting
    Si spécifié, met à jour les termes existants dans les glossaires classiques.

.PARAMETER DryRun
    Si spécifié, exécute en mode prévisualisation sans appliquer de modifications.

.PARAMETER LogFile
    Chemin du fichier de log. Par défaut : sync-uc-classic-YYYYMMDD-HHMMSS.log

.EXAMPLE
    .\Sync-UCToClassicGlossary.ps1 -DomainIds "abc-123", "def-456" -CreateGlossaries

.EXAMPLE
    .\Sync-UCToClassicGlossary.ps1 -DomainIds "abc-123" -UpdateExisting -DryRun

.EXAMPLE
    .\Sync-UCToClassicGlossary.ps1 -CreateGlossaries -UpdateExisting -LogFile "C:\Logs\sync.log"

.NOTES
    Auteur: Purview CLI
    Version: 1.0.0
    Prérequis: 
    - Purview CLI installé (pvw command available)
    - Authentification Azure configurée
    - Permissions: Data Curator sur Purview
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string[]]$DomainIds = @(),
    
    [Parameter(Mandatory=$false)]
    [switch]$CreateGlossaries,
    
    [Parameter(Mandatory=$false)]
    [switch]$UpdateExisting,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [string]$LogFile = "sync-uc-classic-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
)

# Configuration
$ErrorActionPreference = "Continue"
$VerbosePreference = "Continue"

# Fonction de logging
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Écrire dans le fichier
    Add-Content -Path $LogFile -Value $logMessage
    
    # Afficher avec couleur
    $color = switch ($Level) {
        "INFO"    { "White" }
        "WARNING" { "Yellow" }
        "ERROR"   { "Red" }
        "SUCCESS" { "Green" }
    }
    Write-Host $logMessage -ForegroundColor $color
}

# Fonction pour vérifier si pvw est disponible
function Test-PurviewCLI {
    try {
        $null = Get-Command pvw -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Fonction pour obtenir tous les domaines si la liste est vide
function Get-AllDomains {
    Write-Log "Récupération de tous les domaines UC..." -Level INFO
    
    try {
        $result = pvw uc domain list --output json 2>&1 | ConvertFrom-Json
        
        if ($result -is [array]) {
            $domainList = $result | ForEach-Object { $_.id }
        }
        elseif ($result.value) {
            $domainList = $result.value | ForEach-Object { $_.id }
        }
        else {
            $domainList = @()
        }
        
        Write-Log "Trouvé $($domainList.Count) domaine(s)" -Level SUCCESS
        return $domainList
    }
    catch {
        Write-Log "Erreur lors de la récupération des domaines: $_" -Level ERROR
        return @()
    }
}

# Fonction pour synchroniser un domaine
function Sync-Domain {
    param(
        [string]$DomainId
    )
    
    Write-Log "========================================" -Level INFO
    Write-Log "Synchronisation du domaine: $DomainId" -Level INFO
    
    # Construire la commande
    $cmd = "pvw uc term sync-classic --domain-id `"$DomainId`""
    
    if ($CreateGlossaries) {
        $cmd += " --create-glossary"
    }
    
    if ($UpdateExisting) {
        $cmd += " --update-existing"
    }
    
    if ($DryRun) {
        $cmd += " --dry-run"
    }
    
    Write-Log "Commande: $cmd" -Level INFO
    
    try {
        # Exécuter la commande
        $output = Invoke-Expression $cmd 2>&1
        
        # Capturer le code de sortie
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Synchronisation réussie pour $DomainId" -Level SUCCESS
            
            # Parser l'output pour extraire les statistiques
            $outputStr = $output -join "`n"
            if ($outputStr -match "Created\s+(\d+)") {
                $created = $matches[1]
                Write-Log "  - Termes créés: $created" -Level INFO
            }
            if ($outputStr -match "Updated\s+(\d+)") {
                $updated = $matches[1]
                Write-Log "  - Termes mis à jour: $updated" -Level INFO
            }
            if ($outputStr -match "Skipped\s+(\d+)") {
                $skipped = $matches[1]
                Write-Log "  - Termes ignorés: $skipped" -Level INFO
            }
            if ($outputStr -match "Failed\s+(\d+)") {
                $failed = $matches[1]
                if ([int]$failed -gt 0) {
                    Write-Log "  - Termes en échec: $failed" -Level WARNING
                }
            }
            
            return $true
        }
        else {
            Write-Log "Échec de synchronisation pour $DomainId (Exit code: $LASTEXITCODE)" -Level ERROR
            Write-Log "Output: $output" -Level ERROR
            return $false
        }
    }
    catch {
        Write-Log "Exception lors de la synchronisation de $DomainId : $_" -Level ERROR
        return $false
    }
}

# ========================================
# SCRIPT PRINCIPAL
# ========================================

Write-Log "========================================" -Level INFO
Write-Log "Démarrage du script de synchronisation" -Level INFO
Write-Log "========================================" -Level INFO

# Vérifier que pvw est disponible
if (-not (Test-PurviewCLI)) {
    Write-Log "Purview CLI (pvw) n'est pas disponible. Veuillez l'installer." -Level ERROR
    exit 1
}

Write-Log "Purview CLI détecté" -Level SUCCESS

# Configuration du mode
if ($DryRun) {
    Write-Log "MODE DRY-RUN: Aucune modification ne sera appliquée" -Level WARNING
}

# Obtenir la liste des domaines à synchroniser
$domainsToSync = if ($DomainIds.Count -eq 0) {
    Write-Log "Aucun domaine spécifié, récupération de tous les domaines..." -Level INFO
    Get-AllDomains
}
else {
    $DomainIds
}

if ($domainsToSync.Count -eq 0) {
    Write-Log "Aucun domaine à synchroniser. Arrêt." -Level WARNING
    exit 0
}

Write-Log "Nombre de domaines à synchroniser: $($domainsToSync.Count)" -Level INFO

# Statistiques globales
$stats = @{
    Total = $domainsToSync.Count
    Success = 0
    Failed = 0
}

# Synchroniser chaque domaine
foreach ($domainId in $domainsToSync) {
    $result = Sync-Domain -DomainId $domainId
    
    if ($result) {
        $stats.Success++
    }
    else {
        $stats.Failed++
    }
    
    # Pause entre les domaines pour éviter le throttling
    Start-Sleep -Seconds 2
}

# Résumé final
Write-Log "========================================" -Level INFO
Write-Log "RÉSUMÉ DE LA SYNCHRONISATION" -Level INFO
Write-Log "========================================" -Level INFO
Write-Log "Domaines traités: $($stats.Total)" -Level INFO
Write-Log "Succès: $($stats.Success)" -Level SUCCESS
Write-Log "Échecs: $($stats.Failed)" -Level $(if ($stats.Failed -gt 0) { "ERROR" } else { "INFO" })

if ($stats.Failed -eq 0) {
    Write-Log "Toutes les synchronisations ont réussi! ✅" -Level SUCCESS
    exit 0
}
else {
    Write-Log "Certaines synchronisations ont échoué. Consultez les logs." -Level WARNING
    exit 1
}
