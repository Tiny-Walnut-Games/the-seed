/**
 * Core type definitions for the Warbler conversation system
 */

export interface WarblerSlot {
  readonly name: string;
  readonly type: 'string' | 'number' | 'boolean' | 'object';
  readonly required: boolean;
  readonly description?: string;
}

export interface WarblerTemplate {
  readonly id: string;
  readonly version: string;
  readonly title: string;
  readonly description: string;
  readonly content: string;
  readonly requiredSlots: WarblerSlot[];
  readonly tags: string[];
  readonly maxLength?: number;
}

export interface WarblerIntent {
  readonly type: string;
  readonly confidence: number;
  readonly slots: Record<string, unknown>;
}

export interface WarblerContext {
  readonly npcId: string;
  readonly sceneId: string;
  readonly previousUtterances: string[];
  readonly worldState: Record<string, unknown>;
  readonly conversationHistory: WarblerUtterance[];
}

export interface WarblerUtterance {
  readonly id: string;
  readonly timestamp: number;
  readonly npcId: string;
  readonly content: string;
  readonly templateId: string;
  readonly intent: WarblerIntent;
  readonly metadata: Record<string, unknown>;
}

export interface WarblerScore {
  readonly templateId: string;
  readonly relevance: number;
  readonly contextFit: number;
  readonly novelty: number;
  readonly total: number;
}

export interface WarblerRealizationResult {
  readonly success: boolean;
  readonly utterance?: WarblerUtterance;
  readonly error?: string;
  readonly alternatives?: WarblerUtterance[];
}

export interface WarblerPackMetadata {
  readonly name: string;
  readonly version: string;
  readonly description: string;
  readonly author: string;
  readonly templates: WarblerTemplate[];
}