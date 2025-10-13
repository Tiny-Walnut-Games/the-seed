/**
 * Slot resolution for dynamic template content generation
 */

import { WarblerSlot, WarblerContext } from './types.js';

export class SlotResolver {
  /**
   * Resolve slot values from context and provided slots
   */
  resolveSlots(
    requiredSlots: WarblerSlot[],
    providedSlots: Record<string, unknown>,
    context: WarblerContext
  ): Record<string, unknown> {
    const resolved: Record<string, unknown> = { ...providedSlots };
    
    for (const slot of requiredSlots) {
      if (!(slot.name in resolved)) {
        const contextValue = this.resolveFromContext(slot, context);
        if (contextValue !== undefined) {
          resolved[slot.name] = contextValue;
        } else if (slot.required) {
          throw new Error(`Required slot '${slot.name}' could not be resolved`);
        }
      }
    }
    
    return resolved;
  }
  
  /**
   * Resolve a slot value from conversation context
   */
  private resolveFromContext(slot: WarblerSlot, context: WarblerContext): unknown {
    switch (slot.name) {
      case 'npc_name':
        return this.resolveNpcName(context.npcId);
      case 'location':
        return this.resolveLocation(context.sceneId);
      case 'time_of_day':
        return this.resolveTimeOfDay(context);
      case 'conversation_length':
        return context.conversationHistory.length;
      case 'last_speaker':
        return this.getLastSpeaker(context);
      case 'world_state':
        return context.worldState;
      default:
        return this.resolveFromWorldState(slot.name, context.worldState);
    }
  }
  
  private resolveNpcName(npcId: string): string {
    // In a real implementation, this would look up NPC data
    const nameMap: Record<string, string> = {
      'guard_001': 'Captain Marcus',
      'merchant_002': 'Trader Elara',
      'villager_003': 'Old Willem',
      'priest_004': 'Brother Theodore'
    };
    
    return nameMap[npcId] || `NPC-${npcId}`;
  }
  
  private resolveLocation(sceneId: string): string {
    // In a real implementation, this would look up scene data
    const locationMap: Record<string, string> = {
      'town_square': 'the bustling town square',
      'tavern_interior': 'the dimly lit tavern',
      'castle_gates': 'the imposing castle gates',
      'forest_path': 'the winding forest path'
    };
    
    return locationMap[sceneId] || `location ${sceneId}`;
  }
  
  private resolveTimeOfDay(context: WarblerContext): string {
    // Simple time resolution - could be enhanced with game time system
    const hour = new Date().getHours();
    
    if (hour >= 6 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 18) return 'afternoon';
    if (hour >= 18 && hour < 22) return 'evening';
    return 'night';
  }
  
  private getLastSpeaker(context: WarblerContext): string {
    if (context.conversationHistory.length === 0) return 'none';
    
    const lastUtterance = context.conversationHistory[context.conversationHistory.length - 1];
    return lastUtterance.npcId;
  }
  
  private resolveFromWorldState(slotName: string, worldState: Record<string, unknown>): unknown {
    return worldState[slotName];
  }
  
  /**
   * Apply resolved slots to template content
   */
  applySlots(templateContent: string, resolvedSlots: Record<string, unknown>): string {
    let result = templateContent;
    
    // Replace slot placeholders in the format {{slot_name}}
    for (const [slotName, slotValue] of Object.entries(resolvedSlots)) {
      const placeholder = `{{${slotName}}}`;
      const valueString = this.formatSlotValue(slotValue);
      result = result.replace(new RegExp(placeholder, 'g'), valueString);
    }
    
    return result;
  }
  
  private formatSlotValue(value: unknown): string {
    if (value === null || value === undefined) {
      return '';
    }
    
    if (typeof value === 'string') {
      return value;
    }
    
    if (typeof value === 'number' || typeof value === 'boolean') {
      return String(value);
    }
    
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    
    return String(value);
  }
  
  /**
   * Check if all required slots can be resolved
   */
  canResolveSlots(
    requiredSlots: WarblerSlot[],
    providedSlots: Record<string, unknown>,
    context: WarblerContext
  ): boolean {
    try {
      this.resolveSlots(requiredSlots, providedSlots, context);
      return true;
    } catch {
      return false;
    }
  }
}