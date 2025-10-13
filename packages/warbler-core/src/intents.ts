/**
 * Intent recognition and processing for Warbler conversations
 */

import { WarblerIntent } from './types.js';

export class IntentProcessor {
  /**
   * Process user input and extract intent with confidence scoring
   */
  processInput(input: string, context?: Record<string, unknown>): WarblerIntent {
    const normalizedInput = input.toLowerCase().trim();
    
    // Simple keyword-based intent recognition for MVP
    if (this.matchesKeywords(normalizedInput, ['hello', 'hi', 'greetings', 'hey'])) {
      return {
        type: 'greeting',
        confidence: 0.9,
        slots: { greeting_type: 'casual' }
      };
    }
    
    if (this.matchesKeywords(normalizedInput, ['bye', 'goodbye', 'farewell', 'see you'])) {
      return {
        type: 'farewell',
        confidence: 0.9,
        slots: { farewell_type: 'polite' }
      };
    }
    
    if (this.matchesKeywords(normalizedInput, ['help', 'assist', 'support'])) {
      return {
        type: 'help_request',
        confidence: 0.8,
        slots: { urgency: 'normal' }
      };
    }
    
    if (this.matchesKeywords(normalizedInput, ['attack', 'fight', 'battle', 'combat'])) {
      return {
        type: 'combat_initiation',
        confidence: 0.85,
        slots: { aggression_level: 'high' }
      };
    }
    
    if (this.matchesKeywords(normalizedInput, ['trade', 'buy', 'sell', 'merchant'])) {
      return {
        type: 'trade_inquiry',
        confidence: 0.8,
        slots: { transaction_type: 'general' }
      };
    }
    
    // Default fallback intent
    return {
      type: 'general_conversation',
      confidence: 0.5,
      slots: { input_length: input.length }
    };
  }
  
  private matchesKeywords(input: string, keywords: string[]): boolean {
    return keywords.some(keyword => input.includes(keyword));
  }
  
  /**
   * Extract slots from input based on intent type
   */
  extractSlots(input: string, intentType: string): Record<string, unknown> {
    const slots: Record<string, unknown> = {};
    
    // Basic slot extraction - can be enhanced with NLP libraries
    switch (intentType) {
      case 'greeting':
        slots.time_of_day = this.extractTimeOfDay(input);
        break;
      case 'trade_inquiry':
        slots.item_mentions = this.extractItemMentions(input);
        break;
      case 'combat_initiation':
        slots.weapon_type = this.extractWeaponType(input);
        break;
    }
    
    return slots;
  }
  
  private extractTimeOfDay(input: string): string {
    if (input.includes('morning')) return 'morning';
    if (input.includes('afternoon')) return 'afternoon';
    if (input.includes('evening')) return 'evening';
    if (input.includes('night')) return 'night';
    return 'unknown';
  }
  
  private extractItemMentions(input: string): string[] {
    const commonItems = ['sword', 'shield', 'potion', 'armor', 'bow', 'arrow'];
    return commonItems.filter(item => input.includes(item));
  }
  
  private extractWeaponType(input: string): string {
    const weapons = ['sword', 'bow', 'staff', 'dagger', 'axe'];
    const found = weapons.find(weapon => input.includes(weapon));
    return found || 'unarmed';
  }
}