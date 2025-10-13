/**
 * Conversation realization engine - generates final utterances
 */

import { 
  WarblerTemplate, 
  WarblerIntent, 
  WarblerContext, 
  WarblerUtterance, 
  WarblerRealizationResult 
} from './types.js';
import { TemplateManager } from './templates.js';
import { SlotResolver } from './slotResolvers.js';
import { ScoringEngine } from './scoring.js';

export class RealizationEngine {
  private templateManager: TemplateManager;
  private slotResolver: SlotResolver;
  private scoringEngine: ScoringEngine;
  
  constructor() {
    this.templateManager = new TemplateManager();
    this.slotResolver = new SlotResolver();
    this.scoringEngine = new ScoringEngine();
  }
  
  /**
   * Register templates for use in conversations
   */
  registerTemplate(template: WarblerTemplate): void {
    this.templateManager.registerTemplate(template);
  }
  
  registerTemplates(templates: WarblerTemplate[]): void {
    this.templateManager.registerTemplates(templates);
  }
  
  /**
   * Realize an utterance from intent and context
   */
  realize(
    intent: WarblerIntent,
    context: WarblerContext,
    providedSlots: Record<string, unknown> = {}
  ): WarblerRealizationResult {
    try {
      // Get candidate templates for this intent
      const candidateTemplates = this.getCandidateTemplates(intent);
      
      if (candidateTemplates.length === 0) {
        return {
          success: false,
          error: `No templates found for intent type: ${intent.type}`
        };
      }
      
      // Score templates against intent and context
      const scores = this.scoringEngine.scoreTemplates(candidateTemplates, intent, context);
      const topScores = this.scoringEngine.getTopTemplates(scores, 3);
      
      // Try to realize with the best scoring templates
      for (const score of topScores) {
        const template = this.templateManager.getTemplate(score.templateId);
        if (!template) continue;
        
        const result = this.realizeWithTemplate(template, intent, context, providedSlots);
        if (result.success) {
          // Generate alternatives from remaining templates
          const alternatives = this.generateAlternatives(
            topScores.slice(1), 
            intent, 
            context, 
            providedSlots
          );
          
          return {
            ...result,
            alternatives
          };
        }
      }
      
      return {
        success: false,
        error: 'Failed to realize any candidate templates'
      };
      
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error during realization'
      };
    }
  }
  
  /**
   * Attempt to realize an utterance with a specific template
   */
  private realizeWithTemplate(
    template: WarblerTemplate,
    intent: WarblerIntent,
    context: WarblerContext,
    providedSlots: Record<string, unknown>
  ): WarblerRealizationResult {
    try {
      // Check if we can resolve all required slots
      if (!this.slotResolver.canResolveSlots(template.requiredSlots, providedSlots, context)) {
        return {
          success: false,
          error: `Cannot resolve required slots for template: ${template.id}`
        };
      }
      
      // Resolve slots
      const resolvedSlots = this.slotResolver.resolveSlots(
        template.requiredSlots,
        providedSlots,
        context
      );
      
      // Apply slots to template content
      const content = this.slotResolver.applySlots(template.content, resolvedSlots);
      
      // Create utterance
      const utterance: WarblerUtterance = {
        id: this.generateUtteranceId(),
        timestamp: Date.now(),
        npcId: context.npcId,
        content,
        templateId: template.id,
        intent,
        metadata: {
          templateVersion: template.version,
          resolvedSlots,
          contextSceneId: context.sceneId
        }
      };
      
      return {
        success: true,
        utterance
      };
      
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Template realization failed'
      };
    }
  }
  
  private getCandidateTemplates(intent: WarblerIntent): WarblerTemplate[] {
    // Get templates by intent type
    let candidates = this.templateManager.getTemplatesByIntent(intent.type);
    
    // If no direct matches, try broader categories
    if (candidates.length === 0) {
      const intentCategory = intent.type.split('_')[0];
      candidates = this.templateManager.getTemplatesByTags([intentCategory]);
    }
    
    // Last resort - get general/fallback templates
    if (candidates.length === 0) {
      candidates = this.templateManager.getTemplatesByTags(['general', 'fallback']);
    }
    
    return candidates;
  }
  
  private generateAlternatives(
    scores: Array<{ templateId: string }>,
    intent: WarblerIntent,
    context: WarblerContext,
    providedSlots: Record<string, unknown>
  ): WarblerUtterance[] {
    const alternatives: WarblerUtterance[] = [];
    
    for (const score of scores.slice(0, 2)) { // Max 2 alternatives
      const template = this.templateManager.getTemplate(score.templateId);
      if (!template) continue;
      
      const result = this.realizeWithTemplate(template, intent, context, providedSlots);
      if (result.success && result.utterance) {
        alternatives.push(result.utterance);
      }
    }
    
    return alternatives;
  }
  
  private generateUtteranceId(): string {
    return `utterance_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Get all registered templates
   */
  getRegisteredTemplates(): WarblerTemplate[] {
    return this.templateManager.getAllTemplates();
  }
  
  /**
   * Get template manager for direct access
   */
  getTemplateManager(): TemplateManager {
    return this.templateManager;
  }
}