/**
 * Scoring system for template selection and ranking
 */

import { WarblerTemplate, WarblerIntent, WarblerContext, WarblerScore } from './types.js';

export class ScoringEngine {
  /**
   * Score templates against intent and context
   */
  scoreTemplates(
    templates: WarblerTemplate[],
    intent: WarblerIntent,
    context: WarblerContext
  ): WarblerScore[] {
    return templates.map(template => this.scoreTemplate(template, intent, context));
  }
  
  /**
   * Score a single template against intent and context
   */
  scoreTemplate(
    template: WarblerTemplate,
    intent: WarblerIntent,
    context: WarblerContext
  ): WarblerScore {
    const relevance = this.calculateRelevance(template, intent);
    const contextFit = this.calculateContextFit(template, context);
    const novelty = this.calculateNovelty(template, context);
    
    // Weighted scoring - relevance is most important
    const total = (relevance * 0.5) + (contextFit * 0.3) + (novelty * 0.2);
    
    return {
      templateId: template.id,
      relevance,
      contextFit,
      novelty,
      total
    };
  }
  
  /**
   * Calculate how relevant the template is to the detected intent
   */
  private calculateRelevance(template: WarblerTemplate, intent: WarblerIntent): number {
    let score = 0;
    
    // Direct intent type match
    if (template.tags.includes(intent.type)) {
      score += 0.8;
    }
    
    // Partial intent type match (e.g., combat_* intents)
    const intentPrefix = intent.type.split('_')[0];
    if (template.tags.some(tag => tag.startsWith(intentPrefix))) {
      score += 0.4;
    }
    
    // Generic fallback templates
    if (template.tags.includes('general') || template.tags.includes('fallback')) {
      score += 0.2;
    }
    
    // Boost score by intent confidence
    score *= intent.confidence;
    
    return Math.min(score, 1.0);
  }
  
  /**
   * Calculate how well the template fits the current context
   */
  private calculateContextFit(template: WarblerTemplate, context: WarblerContext): number {
    let score = 0;
    
    // Check if template has been used recently (novelty factor)
    const recentUsage = this.getRecentTemplateUsage(template.id, context);
    if (recentUsage === 0) {
      score += 0.4; // Bonus for unused templates
    } else {
      score += Math.max(0, 0.4 - (recentUsage * 0.1));
    }
    
    // Context-specific scoring
    score += this.scoreContextSpecifics(template, context);
    
    // Conversation length consideration
    score += this.scoreConversationLength(template, context);
    
    return Math.min(score, 1.0);
  }
  
  private scoreContextSpecifics(template: WarblerTemplate, context: WarblerContext): number {
    let score = 0;
    
    // Scene-specific templates
    if (template.tags.includes(`scene_${context.sceneId}`)) {
      score += 0.3;
    }
    
    // NPC-specific templates
    if (template.tags.includes(`npc_${context.npcId}`)) {
      score += 0.2;
    }
    
    // World state considerations
    for (const [key, value] of Object.entries(context.worldState)) {
      if (template.tags.includes(`${key}_${value}`)) {
        score += 0.1;
      }
    }
    
    return score;
  }
  
  private scoreConversationLength(template: WarblerTemplate, context: WarblerContext): number {
    const conversationLength = context.conversationHistory.length;
    
    // Prefer shorter responses early in conversation
    if (conversationLength < 3 && template.tags.includes('brief')) {
      return 0.2;
    }
    
    // Allow longer responses in established conversations
    if (conversationLength >= 5 && template.tags.includes('detailed')) {
      return 0.2;
    }
    
    return 0;
  }
  
  /**
   * Calculate novelty score to avoid repetitive responses
   */
  private calculateNovelty(template: WarblerTemplate, context: WarblerContext): number {
    const recentUsage = this.getRecentTemplateUsage(template.id, context);
    
    // High novelty for unused templates
    if (recentUsage === 0) {
      return 1.0;
    }
    
    // Decreasing novelty based on recent usage
    const maxLookback = 10;
    const noveltyScore = Math.max(0, 1.0 - (recentUsage / maxLookback));
    
    return noveltyScore;
  }
  
  private getRecentTemplateUsage(templateId: string, context: WarblerContext): number {
    const lookbackLimit = 10;
    const recentHistory = context.conversationHistory.slice(-lookbackLimit);
    
    return recentHistory.filter(utterance => utterance.templateId === templateId).length;
  }
  
  /**
   * Get the best scoring template from a list
   */
  getBestTemplate(scores: WarblerScore[]): WarblerScore | undefined {
    if (scores.length === 0) return undefined;
    
    return scores.reduce((best, current) => 
      current.total > best.total ? current : best
    );
  }
  
  /**
   * Get top N templates by score
   */
  getTopTemplates(scores: WarblerScore[], n: number): WarblerScore[] {
    return scores
      .sort((a, b) => b.total - a.total)
      .slice(0, n);
  }
}