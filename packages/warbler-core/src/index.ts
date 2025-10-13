/**
 * Warbler Core - NPC Conversation and Narration Engine
 * 
 * Main entry point for the Warbler conversation system
 */

export * from './types.js';
export * from './intents.js';
export * from './templates.js';
export * from './slotResolvers.js';
export * from './scoring.js';
export * from './realize.js';

import { RealizationEngine } from './realize.js';
import { IntentProcessor } from './intents.js';
import { WarblerTemplate, WarblerContext, WarblerIntent, WarblerRealizationResult } from './types.js';

/**
 * High-level Warbler conversation manager
 */
export class Warbler {
  private realizationEngine: RealizationEngine;
  private intentProcessor: IntentProcessor;
  
  constructor() {
    this.realizationEngine = new RealizationEngine();
    this.intentProcessor = new IntentProcessor();
  }
  
  /**
   * Register templates for conversation use
   */
  registerTemplate(template: WarblerTemplate): void {
    this.realizationEngine.registerTemplate(template);
  }
  
  registerTemplates(templates: WarblerTemplate[]): void {
    this.realizationEngine.registerTemplates(templates);
  }
  
  /**
   * Process user input and generate NPC response
   */
  processConversation(
    userInput: string,
    context: WarblerContext,
    additionalSlots: Record<string, unknown> = {}
  ): WarblerRealizationResult {
    // Process user intent
    const intent = this.intentProcessor.processInput(userInput, context.worldState);
    
    // Extract additional slots from input
    const extractedSlots = this.intentProcessor.extractSlots(userInput, intent.type);
    const combinedSlots = { ...extractedSlots, ...additionalSlots };
    
    // Generate response
    return this.realizationEngine.realize(intent, context, combinedSlots);
  }
  
  /**
   * Generate response from explicit intent (for scripted scenarios)
   */
  processIntent(
    intent: WarblerIntent,
    context: WarblerContext,
    slots: Record<string, unknown> = {}
  ): WarblerRealizationResult {
    return this.realizationEngine.realize(intent, context, slots);
  }
  
  /**
   * Get all registered templates
   */
  getTemplates(): WarblerTemplate[] {
    return this.realizationEngine.getRegisteredTemplates();
  }
  
  /**
   * Check system health and configuration
   */
  getSystemInfo(): {
    templateCount: number;
    version: string;
    status: 'ready' | 'no-templates';
  } {
    const templateCount = this.realizationEngine.getRegisteredTemplates().length;
    
    return {
      templateCount,
      version: '1.0.0',
      status: templateCount > 0 ? 'ready' : 'no-templates'
    };
  }
}