# Firebase Setup Helper

## Issues Identified

1. **Firebase CLI PATH Issue**: Firebase CLI is installed but not in your system PATH
2. **Firebase Project Issue**: The configured project `part-108-parser` doesn't exist in your account

## Quick Fixes

### Temporary PATH Fix (Current Session Only)

Run this in PowerShell before using Firebase commands:

```powershell
$env:PATH += ";$env:APPDATA\npm"
```

### Permanent PATH Fix

**Option 1: Run the helper script (Recommended)**
```powershell
.\fix-firebase-path.ps1
```

**Option 2: Manual fix**
1. Open System Properties (Win + R, type `sysdm.cpl`, press Enter)
2. Go to "Advanced" tab → Click "Environment Variables"
3. Under "User variables", select "Path" → Click "Edit"
4. Click "New" and add: `C:\Users\kevin\AppData\Roaming\npm`
5. Click OK on all dialogs
6. Restart PowerShell

### Firebase Project Options

You currently have access to:
- `jengappa-blast` (already switched to this)

**Option 1: Use existing project**
The project has been switched to `jengappa-blast`. Update `.firebaserc` if you want to keep this:
```json
{
  "projects": {
    "default": "jengappa-blast"
  }
}
```

**Option 2: Create a new Firebase project**
1. Go to https://console.firebase.google.com/
2. Create a new project (e.g., `part-108-parser` or `bvlos-ratio`)
3. Then run:
```powershell
$env:PATH += ";$env:APPDATA\npm"
firebase use <your-new-project-id>
```

## Deploying

After fixing PATH, you can deploy from the root directory:

```powershell
# Add PATH for this session
$env:PATH += ";$env:APPDATA\npm"

# Deploy hosting
firebase deploy --only hosting
```

Or use the helper script:
```powershell
.\setup-firebase.ps1
```

## Files Created

- `fix-firebase-path.ps1` - Script to permanently fix PATH
- `setup-firebase.ps1` - Setup helper script with diagnostics

