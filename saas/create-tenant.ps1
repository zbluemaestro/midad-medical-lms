<#
.SYNOPSIS
    Provisions a new isolated Frappe LMS tenant containerized site from Windows.
.EXAMPLE
    .\create-tenant.ps1 -TenantSlug "academy-alpha"
#>
param (
    [Parameter(Mandatory=$true)]
    [string]$TenantSlug,
    [Parameter(Mandatory=$false)]
    [string]$CustomDomain = ""
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Provisioning LMS Tenant: $TenantSlug" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$container = "lms-frappe-bench"
$cmd = "bash /workspace/saas/create-tenant.sh $TenantSlug $CustomDomain"

docker exec -it $container bash -c "$cmd"
