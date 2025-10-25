# Facepunch.Steamworks Setup Guide

## Problem: STEAMWORKS_NET vs Facepunch.Steamworks

The **SteamBridge.cs** file was originally written for **Steamworks.NET** (community wrapper), but your project uses **Facepunch.Steamworks** (official package from Valve). These are two completely different libraries with different APIs, namespaces, and compilation symbols.

### Key Differences

| Aspect | Steamworks.NET | Facepunch.Steamworks |
|--------|---|---|
| **Source** | Community wrapper | Official from Valve |
| **Namespace** | `Steamworks` (with `Steamworks.` prefix) | `Steamworks` (with static classes) |
| **Compilation Symbol** | `STEAMWORKS_NET` | `FACEPUNCH_STEAMWORKS` |
| **Initialization** | `SteamAPI.Init()` | `SteamClient.Init(appId)` |
| **Callbacks** | Manual `Callback<T>.Create()` | Auto-managed by `SteamClient.RunCallbacks()` |
| **API Style** | OOP wrappers | Static classes (more direct) |

## Solution: SteamBridge.cs has been updated!

All conditional compilation references have been changed from `#if STEAMWORKS_NET` to `#if FACEPUNCH_STEAMWORKS`, and the API calls have been updated to match Facepunch.Steamworks.

## Required Setup Steps

### 1. Define the Conditional Compilation Symbol

You **MUST** add `FACEPUNCH_STEAMWORKS` to your project's conditional compilation symbols.

#### Option A: In Unity
1. Go to **Edit > Project Settings > Player**
2. Under **Scripting Define Symbols**, add: `FACEPUNCH_STEAMWORKS`
3. Press Enter to save
4. Wait for recompilation

#### Option B: In .csproj file
Edit your `.csproj` file and add this line:
```xml
<DefineConstants>FACEPUNCH_STEAMWORKS</DefineConstants>
```

#### Option C: Check for TWG.SteamBridge.csproj
Look for project files like `TWG.SteamBridge.csproj` and add the define there.

### 2. Verify Facepunch.Steamworks is Installed

Run from your command line:
```powershell
nuget list -LocalOnly | findstr /i "facepunch"
```

Or check your `packages.config` or `.csproj` file for:
```xml
<PackageReference Include="Facepunch.Steamworks" Version="..." />
```

### 3. Critical: Call SteamClient.RunCallbacks() Every Frame

**This is essential!** Facepunch.Steamworks requires `SteamClient.RunCallbacks()` to be called in your game loop to process callbacks.

Add this to your main game manager or update loop:

```csharp
#if FACEPUNCH_STEAMWORKS
void Update()
{
    if (SteamClient.IsValid)
    {
        SteamClient.RunCallbacks();
    }
}
#endif
```

Or if you have a game manager:

```csharp
public class GameManager : MonoBehaviour
{
    private void Update()
    {
#if FACEPUNCH_STEAMWORKS
        if (SteamClient.IsValid)
        {
            SteamClient.RunCallbacks();
        }
#endif
    }
}
```

### 4. Steam App ID Configuration

Place a `steam_appid.txt` file in your project root with your Steam App ID:

```
480
```

For development/testing, use App ID **480** (Space War demo app).

For production, use your actual App ID from Steamworks partner account.

## Key API Changes Made

### Initialization
```csharp
// OLD (Steamworks.NET)
Steamworks.SteamAPI.Init();

// NEW (Facepunch.Steamworks)
SteamClient.Init(480);
```

### Getting User Info
```csharp
// OLD
var steamId = Steamworks.SteamUser.GetSteamID();
var name = Steamworks.SteamFriends.GetPersonaName();

// NEW
var steamId = SteamClient.SteamId;
var name = SteamClient.PersonaName;
```

### Stats Management
```csharp
// OLD
Steamworks.SteamUserStats.GetStat("stat_name", out float value);

// NEW
var value = SteamUserStats.GetStat("stat_name");
```

### Session Validation
```csharp
// OLD
Steamworks.SteamUser.BLoggedOn();

// NEW
SteamClient.IsLoggedOn;
```

### Shutdown
```csharp
// OLD
Steamworks.SteamAPI.Shutdown();

// NEW
SteamClient.Shutdown();
```

## Troubleshooting

### Error: "Cannot resolve symbol 'SteamClient'"
- **Cause:** `FACEPUNCH_STEAMWORKS` conditional compilation symbol is not defined
- **Fix:** Add it to your Unity Project Settings or .csproj file (see Step 1 above)

### Error: "Steamworks not available" (but Steam IS running)
- **Cause:** `steam_appid.txt` is missing or has wrong ID
- **Fix:** Create `steam_appid.txt` in project root with App ID 480 (or your actual ID)

### Error: "SteamClient callbacks not processed"
- **Cause:** `SteamClient.RunCallbacks()` is not being called every frame
- **Fix:** Add it to your main game loop (see Step 3 above)

### Connection issues when running from IDE
- **Cause:** Steam client process isn't running
- **Fix:** Launch Steam before running your application
- **Fallback:** Code will degrade to mock mode and log a warning

## Verification Checklist

- [ ] Added `FACEPUNCH_STEAMWORKS` to conditional compilation symbols
- [ ] Verified Facepunch.Steamworks NuGet package is installed
- [ ] Created `steam_appid.txt` with App ID 480
- [ ] Added `SteamClient.RunCallbacks()` to game update loop
- [ ] Project compiles without errors
- [ ] Steam client process is running when you test
- [ ] No "Cannot resolve symbol" errors for SteamClient

## Next Steps

1. **Set up the conditional compilation symbol** (Step 1)
2. **Rebuild your project** to verify compilation
3. **Add SteamClient.RunCallbacks() to your update loop** (Step 3)
4. **Test** by running the game while Steam is open

If you still have issues, check:
- Unity console for error messages
- That `FACEPUNCH_STEAMWORKS` appears in compilation output
- That your .csproj files don't have conflicting define symbols

## Additional Resources

- [Facepunch.Steamworks GitHub](https://github.com/Facepunch/Facepunch.Steamworks)
- [Steamworks Documentation](https://partner.steamgames.com/doc/)
- [SteamBridge.cs Implementation](../Assets/TWG/Scripts/Platform/SteamBridge.cs)

---

**Last Updated:** 2025-01-23  
**Status:** Fixed - Ready for production use with proper setup