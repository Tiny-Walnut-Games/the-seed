using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace TWG.TLDA.SpriteForge
{
    /// <summary>
    /// TLDA integration bridge for NFT minting
    /// KeeperNote: Connects TLDA ritual validation to sprite generation and minting
    /// </summary>
    public static class TLDANFTBridge
    {
        private static readonly Dictionary<string, RitualTokenMapping> RitualMappings = new()
        {
            ["nitpick_hunt"] = new RitualTokenMapping
            {
                TokenCategory = TokenCategory.GenreCreature,
                Genre = GenreStyle.Fantasy,
                Archetype = CreatureArchetype.Familiar,
                RarityRange = new[] { RarityTier.Common, RarityTier.Uncommon, RarityTier.Rare }
            },
            ["scroll_integrity"] = new RitualTokenMapping
            {
                TokenCategory = TokenCategory.GenreCreature,
                Genre = GenreStyle.SciFi,
                Archetype = CreatureArchetype.Sentinel,
                RarityRange = new[] { RarityTier.Uncommon, RarityTier.Rare, RarityTier.Epic }
            },
            ["warbler_song"] = new RitualTokenMapping
            {
                TokenCategory = TokenCategory.FacultyUltraRare,
                Faculty = FacultyRole.Warbler,
                RarityRange = new[] { RarityTier.OneOfOne }
            },
            ["giant_in_well"] = new RitualTokenMapping
            {
                TokenCategory = TokenCategory.Location,
                LocationName = "The Well",
                RarityRange = new[] { RarityTier.Rare, RarityTier.Epic }
            },
            ["castle_rite"] = new RitualTokenMapping
            {
                TokenCategory = TokenCategory.Location,
                LocationName = "Mind Castle",
                RarityRange = new[] { RarityTier.Epic, RarityTier.Legendary }
            }
        };

        /// <summary>
        /// Process validated TLDA ritual and trigger NFT generation
        /// KeeperNote: Main entry point from TLDA validation system
        /// </summary>
        public static NFTMintResult ProcessRitual(TLDARitualEvent ritualEvent)
        {
            try
            {
                Debug.Log($"[TLDANFTBridge] Processing ritual: {ritualEvent.RitualType}");
                
                // Generate seed from TLDA event
                var seed = GenerateTLDASeed(ritualEvent);
                
                // Get ritual mapping
                if (!RitualMappings.TryGetValue(ritualEvent.RitualType, out var mapping))
                {
                    Debug.LogWarning($"[TLDANFTBridge] No mapping found for ritual: {ritualEvent.RitualType}");
                    return NFTMintResult.Failed($"Unknown ritual type: {ritualEvent.RitualType}");
                }
                
                // Generate sprite specification
                var spec = GenerateSpecFromRitual(ritualEvent, mapping, seed);
                
                // Generate sprite
                var spriteResult = SpriteGenerator.GenerateSprite(seed, spec);
                if (spriteResult == null || !spriteResult.IsValid)
                {
                    return NFTMintResult.Failed("Sprite generation failed");
                }
                
                // Save generated assets
                var assetPaths = SaveGeneratedAssets(spriteResult);
                
                // Prepare mint transaction (local devchain)
                var mintData = PrepareMintTransaction(spriteResult, assetPaths);
                
                // Record in TLDA ledger
                var ledgerEntry = CreateTLDALedgerEntry(ritualEvent, spriteResult, mintData);
                AppendToTLDALedger(ledgerEntry);
                
                Debug.Log($"[TLDANFTBridge] Successfully processed ritual {ritualEvent.RitualType} → Token {spec.TokenId}");
                
                return NFTMintResult.CreateSuccess(spriteResult, mintData, ledgerEntry);
            }
            catch (Exception ex)
            {
                Debug.LogError($"[TLDANFTBridge] Failed to process ritual: {ex.Message}");
                return NFTMintResult.Failed(ex.Message);
            }
        }
        
        /// <summary>
        /// Generate deterministic seed from TLDA ritual event
        /// KeeperNote: Uses TLDA provenance hash methodology
        /// </summary>
        private static string GenerateTLDASeed(TLDARitualEvent ritualEvent)
        {
            var combined = $"{ritualEvent.Source}{ritualEvent.Text}{ritualEvent.UnixMillis}{ritualEvent.RitualType}";
            using var sha256 = System.Security.Cryptography.SHA256.Create();
            var hashBytes = sha256.ComputeHash(System.Text.Encoding.UTF8.GetBytes(combined));
            return BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();
        }
        
        /// <summary>
        /// Generate sprite specification from ritual and mapping
        /// </summary>
        private static SpriteSpec GenerateSpecFromRitual(TLDARitualEvent ritualEvent, RitualTokenMapping mapping, string seed)
        {
            var random = new System.Random(seed.GetHashCode());
            var tokenId = GenerateTokenId(ritualEvent, mapping);
            
            var spec = new SpriteSpec
            {
                TokenId = tokenId,
                Faculty = mapping.Faculty,
                Genre = mapping.Genre,
                Archetype = mapping.Archetype,
                Rarity = SelectRarity(mapping.RarityRange, random),
                Description = GenerateDescription(ritualEvent, mapping)
            };
            
            // Faculty ultra-rares get special treatment
            if (mapping.TokenCategory == TokenCategory.FacultyUltraRare)
            {
                spec = SpriteSpec.CreateFacultySpec(mapping.Faculty, tokenId);
            }
            // Genre creatures
            else if (mapping.TokenCategory == TokenCategory.GenreCreature)
            {
                spec = SpriteSpec.CreateGenreSpec(mapping.Genre, mapping.Archetype, spec.Rarity);
                spec.TokenId = tokenId;
            }
            
            // Add ritual-specific traits
            AddRitualTraits(spec, ritualEvent);
            
            return spec;
        }
        
        /// <summary>
        /// Add ritual-specific traits to token metadata
        /// </summary>
        private static void AddRitualTraits(SpriteSpec spec, TLDARitualEvent ritualEvent)
        {
            spec.CustomTraits["Ritual Type"] = ritualEvent.RitualType;
            spec.CustomTraits["Ritual Timestamp"] = DateTimeOffset.FromUnixTimeMilliseconds(ritualEvent.UnixMillis).ToString("yyyy-MM-dd HH:mm:ss UTC");
            spec.CustomTraits["TLDA Source"] = ritualEvent.Source;
            spec.CustomTraits["Emotional Weight"] = ritualEvent.EmotionalWeight;
            
            // Add ritual mark based on type
            var ritualMark = ritualEvent.RitualType switch
            {
                "nitpick_hunt" => "Nitpick Hunt",
                "scroll_integrity" => "Scroll Integrity",
                "warbler_song" => "Warbler Song",
                "giant_in_well" => "Giant-in-the-Well",
                "castle_rite" => "Castle Rite",
                _ => "Unknown Ritual"
            };
            
            spec.CustomTraits["Ritual Mark"] = ritualMark;
            
            // Add tags as traits
            if (ritualEvent.Tags != null && ritualEvent.Tags.Length > 0)
            {
                spec.CustomTraits["Tags"] = string.Join(", ", ritualEvent.Tags);
            }
        }
        
        /// <summary>
        /// Generate unique token ID
        /// </summary>
        private static string GenerateTokenId(TLDARitualEvent ritualEvent, RitualTokenMapping mapping)
        {
            var timestamp = DateTimeOffset.FromUnixTimeMilliseconds(ritualEvent.UnixMillis);
            var dateStr = timestamp.ToString("yyyyMMdd");
            var typePrefix = mapping.TokenCategory switch
            {
                TokenCategory.FacultyUltraRare => "FAC",
                TokenCategory.GenreCreature => "CRE",
                TokenCategory.Location => "LOC",
                _ => "UNK"
            };
            
            var random = new System.Random(ritualEvent.UnixMillis.GetHashCode());
            var suffix = random.Next(1000, 9999);
            
            return $"{typePrefix}-{dateStr}-{suffix}";
        }
        
        /// <summary>
        /// Select rarity tier from range
        /// </summary>
        private static RarityTier SelectRarity(RarityTier[] rarityRange, System.Random random)
        {
            if (rarityRange == null || rarityRange.Length == 0)
                return RarityTier.Common;
                
            return rarityRange[random.Next(0, rarityRange.Length)];
        }
        
        /// <summary>
        /// Generate token description
        /// </summary>
        private static string GenerateDescription(TLDARitualEvent ritualEvent, RitualTokenMapping mapping)
        {
            return mapping.TokenCategory switch
            {
                TokenCategory.FacultyUltraRare => $"Faculty ultra-rare 1/1. Born from the {ritualEvent.RitualType} ritual on {DateTimeOffset.FromUnixTimeMilliseconds(ritualEvent.UnixMillis):yyyy-MM-dd}.",
                TokenCategory.GenreCreature => $"{mapping.Genre} creature forged from TLDA ritual validation. Emotional weight: {ritualEvent.EmotionalWeight:F2}.",
                TokenCategory.Location => $"Sacred location from the TLDA mythos: {mapping.LocationName}. Witnessed during {ritualEvent.RitualType} ritual.",
                _ => "Unknown token type from TLDA ritual system."
            };
        }
        
        /// <summary>
        /// Save generated sprite assets to disk
        /// </summary>
        private static GeneratedAssetPaths SaveGeneratedAssets(SpriteGenerationResult result)
        {
            var baseDir = Path.Combine(Application.dataPath, "TWG/TLDA/Tools/SpriteForge/Generated");
            var tokenDir = Path.Combine(baseDir, "Creatures", result.TokenMetadata.name.Replace(" ", "_"));
            
            Directory.CreateDirectory(tokenDir);
            
            var paths = new GeneratedAssetPaths();
            
            // Save sprite sheet
            var spriteBytes = result.SpriteSheet.EncodeToPNG();
            paths.SpriteSheetPath = Path.Combine(tokenDir, "sheet.png");
            File.WriteAllBytes(paths.SpriteSheetPath, spriteBytes);
            
            // Save metadata JSON
            var metadataJson = JsonUtility.ToJson(result.TokenMetadata, true);
            paths.MetadataPath = Path.Combine(tokenDir, "metadata.json");
            File.WriteAllText(paths.MetadataPath, metadataJson);
            
            // Save animation data
            var animationJson = JsonUtility.ToJson(result.AnimationData, true);
            paths.AnimationDataPath = Path.Combine(tokenDir, "animation.json");
            File.WriteAllText(paths.AnimationDataPath, animationJson);
            
            // Save Unity sprite meta file
            var unityMeta = GenerateUnitySpriteMetaFile(result);
            paths.UnityMetaPath = Path.Combine(tokenDir, "sheet.png.meta");
            File.WriteAllText(paths.UnityMetaPath, unityMeta);
            
            Debug.Log($"[TLDANFTBridge] Saved assets to: {tokenDir}");
            
            return paths;
        }
        
        /// <summary>
        /// Generate Unity sprite import settings
        /// </summary>
        private static string GenerateUnitySpriteMetaFile(SpriteGenerationResult result)
        {
            // This would generate proper Unity .meta file content
            // For now, return a placeholder that indicates sprite slicing data
            var frameCount = result.AnimationData.FrameRects.Length;
            var _ = result.AnimationData.FrameRects[0]; // Frame size is calculated but not used in this basic implementation
            
            return $@"fileFormatVersion: 2
guid: {System.Guid.NewGuid():N}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 12
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
  bumpmap:
    convertToNormalMap: 0
  isReadable: 0
  streamingMipmaps: 0
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: {frameCount}
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePNGGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteMode: 2
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {{x: 0.5, y: 0}}
  spritePixelsPerUnit: 100
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePNGGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  platformSettings: []
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: 
    internalID: 0
    vertices: []
    indices: 
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  mipmapLimitGroupName: 
  pSDRemoveMatte: 0
  userData: 
  assetBundleName: 
  assetBundleVariant: ";
        }
        
        /// <summary>
        /// Prepare local devchain mint transaction
        /// </summary>
        private static MintTransactionData PrepareMintTransaction(SpriteGenerationResult result, GeneratedAssetPaths paths)
        {
            var isERC721 = result.TokenMetadata.attributes.Any(a => 
                a.trait_type == "Uniqueness" && a.value.ToString() == "1/1");
            
            return new MintTransactionData
            {
                TokenId = result.TokenMetadata.name.GetHashCode().ToString(),
                ContractType = isERC721 ? "ERC721" : "ERC1155",
                TokenURI = $"file://{paths.MetadataPath}",
                Recipient = "0x742d35Cc6634C0532925a3b8D5c5B1E0A4A6E4Be", // Placeholder address
                Supply = isERC721 ? 1 : GetSupplyFromRarity(result),
                TransactionHash = System.Guid.NewGuid().ToString("N"),
                BlockNumber = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
                GasUsed = 150000 + result.AnimationData.FrameRects.Length * 1000 // Simulated gas
            };
        }
        
        /// <summary>
        /// Get supply amount based on rarity
        /// </summary>
        private static int GetSupplyFromRarity(SpriteGenerationResult result)
        {
            var rarityAttr = result.TokenMetadata.attributes.FirstOrDefault(a => a.trait_type == "Rarity");
            if (rarityAttr == null) return 512; // Default to common
            
            return rarityAttr.value.ToString() switch
            {
                "OneOfOne" => 1,
                "Legendary" => 4,
                "Epic" => 16,
                "Rare" => 64,
                "Uncommon" => 256,
                "Common" => 512,
                _ => 512
            };
        }
        
        /// <summary>
        /// Create TLDA ledger entry
        /// </summary>
        private static TLDALedgerEntry CreateTLDALedgerEntry(TLDARitualEvent ritualEvent, SpriteGenerationResult result, MintTransactionData mintData)
        {
            return new TLDALedgerEntry
            {
                Id = $"TLDA-NFT-{DateTimeOffset.UtcNow:yyyyMMdd-HHmmss}-{result.TokenMetadata.name.GetHashCode():X8}",
                Timestamp = DateTimeOffset.UtcNow,
                EventType = "NFT_MINTED",
                Source = "TLDANFTBridge",
                RitualReference = ritualEvent.Id,
                TokenId = mintData.TokenId,
                ProvenanceHash = result.ProvenanceHash,
                Metadata = new Dictionary<string, object>
                {
                    ["ritual_type"] = ritualEvent.RitualType,
                    ["token_name"] = result.TokenMetadata.name,
                    ["contract_type"] = mintData.ContractType,
                    ["supply"] = mintData.Supply,
                    ["sprite_seed"] = result.Seed,
                    ["generation_timestamp"] = result.GeneratedAt,
                    ["mint_transaction"] = mintData.TransactionHash
                }
            };
        }
        
        /// <summary>
        /// Append entry to TLDA ledger
        /// </summary>
        private static void AppendToTLDALedger(TLDALedgerEntry entry)
        {
            var ledgerPath = Path.Combine(Application.dataPath, "TWG/TLDA/Tools/SpriteForge/Generated/tlda_nft_ledger.json");
            
            List<TLDALedgerEntry> ledger;
            
            if (File.Exists(ledgerPath))
            {
                var existingJson = File.ReadAllText(ledgerPath);
                ledger = JsonUtility.FromJson<TLDALedgerWrapper>(existingJson)?.entries ?? new List<TLDALedgerEntry>();
            }
            else
            {
                ledger = new List<TLDALedgerEntry>();
            }
            
            ledger.Add(entry);
            
            var wrapper = new TLDALedgerWrapper { entries = ledger };
            var json = JsonUtility.ToJson(wrapper, true);
            
            Directory.CreateDirectory(Path.GetDirectoryName(ledgerPath));
            File.WriteAllText(ledgerPath, json);
            
            Debug.Log($"[TLDANFTBridge] Appended to TLDA ledger: {entry.Id}");
        }
    }
    
    // Supporting data structures
    
    [Serializable]
    public class TLDARitualEvent
    {
        public string Id;
        public string Source;
        public string Text;
        public string RitualType;
        public float EmotionalWeight;
        public string[] Tags;
        public long UnixMillis;
        public string ProvenanceHash;
    }
    
    [Serializable]
    public class RitualTokenMapping
    {
        public TokenCategory TokenCategory;
        public GenreStyle Genre;
        public CreatureArchetype Archetype;
        public FacultyRole Faculty;
        public string LocationName;
        public RarityTier[] RarityRange;
    }
    
    public enum TokenCategory
    {
        FacultyUltraRare,
        GenreCreature,
        Location
    }
    
    [Serializable]
    public class GeneratedAssetPaths
    {
        public string SpriteSheetPath;
        public string MetadataPath;
        public string AnimationDataPath;
        public string UnityMetaPath;
    }
    
    [Serializable]
    public class MintTransactionData
    {
        public string TokenId;
        public string ContractType;
        public string TokenURI;
        public string Recipient;
        public int Supply;
        public string TransactionHash;
        public long BlockNumber;
        public long GasUsed;
    }
    
    [Serializable]
    public class TLDALedgerEntry
    {
        public string Id;
        public DateTimeOffset Timestamp;
        public string EventType;
        public string Source;
        public string RitualReference;
        public string TokenId;
        public string ProvenanceHash;
        public Dictionary<string, object> Metadata;
    }
    
    [Serializable]
    public class TLDALedgerWrapper
    {
        public List<TLDALedgerEntry> entries;
    }
    
    [Serializable]
    public class NFTMintResult
    {
        public bool Success;
        public string ErrorMessage;
        public SpriteGenerationResult SpriteResult;
        public MintTransactionData MintData;
        public TLDALedgerEntry LedgerEntry;
        
        public static NFTMintResult CreateSuccess(SpriteGenerationResult spriteResult, MintTransactionData mintData, TLDALedgerEntry ledgerEntry)
        {
            return new NFTMintResult
            {
                Success = true,
                SpriteResult = spriteResult,
                MintData = mintData,
                LedgerEntry = ledgerEntry
            };
        }
        
        public static NFTMintResult Failed(string error)
        {
            return new NFTMintResult
            {
                Success = false,
                ErrorMessage = error
            };
        }
    }
}
