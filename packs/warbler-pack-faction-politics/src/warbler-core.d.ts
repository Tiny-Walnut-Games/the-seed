/**
 * Warbler Faction Politics Type Definitions
 * Essential types for political intrigue and faction dialogue
 * 
 * 🧙‍♂️ "In the game of politics, even NPCs need proper type safety!" - Bootstrap Sentinel
 */

export interface WarblerSlot {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'object';
  required: boolean;
  description: string;
}

// 🔥 BUTT-SAVING FIX: Match the actual JSON structure exactly
export interface WarblerTemplate {
  id: string;
  version: string;
  title: string;
  description: string;
  content: string;
  requiredSlots: WarblerSlot[];
  tags: string[];
  maxLength: number;
  cooldownMinutes?: number;
  conditions?: string[];
  responses?: string[];
}

export interface WarblerPackMetadata {
  name: string;
  version: string;
  description: string;
  author: string;
  templates: WarblerTemplate[];
}

export interface WarblerPackInfo {
  name: string;
  version: string;
  description: string;
  author: string;
  compatibleEngine: string;
}

export interface WarblerTemplateData {
  packInfo: WarblerPackInfo;
  templates: WarblerTemplate[];
}

// 🔥 BUTT-SAVING PROTOCOL: Add JSON import types for TypeScript happiness
declare module '*.json' {
  const value: WarblerTemplateData;
  export default value;
}

// Export default interface for JSON structure
export default WarblerTemplateData;
