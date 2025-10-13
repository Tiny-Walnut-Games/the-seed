/**
 * Template management and processing for Warbler conversations
 */

import { WarblerTemplate, WarblerSlot } from './types.js';

export class TemplateManager {
  private templates: Map<string, WarblerTemplate> = new Map();
  
  /**
   * Register a template for use in conversations
   */
  registerTemplate(template: WarblerTemplate): void {
    this.validateTemplate(template);
    this.templates.set(template.id, template);
  }
  
  /**
   * Register multiple templates from a pack
   */
  registerTemplates(templates: WarblerTemplate[]): void {
    templates.forEach(template => this.registerTemplate(template));
  }
  
  /**
   * Get a template by ID
   */
  getTemplate(id: string): WarblerTemplate | undefined {
    return this.templates.get(id);
  }
  
  /**
   * Get all templates matching specified tags
   */
  getTemplatesByTags(tags: string[]): WarblerTemplate[] {
    return Array.from(this.templates.values())
      .filter(template => 
        tags.some(tag => template.tags.includes(tag))
      );
  }
  
  /**
   * Get all templates for a specific intent type
   */
  getTemplatesByIntent(intentType: string): WarblerTemplate[] {
    return this.getTemplatesByTags([intentType]);
  }
  
  /**
   * Get all registered templates
   */
  getAllTemplates(): WarblerTemplate[] {
    return Array.from(this.templates.values());
  }
  
  /**
   * Validate template structure and constraints
   */
  private validateTemplate(template: WarblerTemplate): void {
    if (!template.id || template.id.trim().length === 0) {
      throw new Error('Template ID is required');
    }
    
    if (!template.version || !this.isValidVersion(template.version)) {
      throw new Error('Template version must be a valid semver string');
    }
    
    if (!template.content || template.content.trim().length === 0) {
      throw new Error('Template content is required');
    }
    
    if (template.maxLength && template.content.length > template.maxLength) {
      throw new Error(`Template content exceeds maximum length of ${template.maxLength}`);
    }
    
    // Validate required slots
    template.requiredSlots.forEach(slot => this.validateSlot(slot));
    
    // Check for duplicate slot names
    const slotNames = template.requiredSlots.map(slot => slot.name);
    const uniqueSlotNames = new Set(slotNames);
    if (slotNames.length !== uniqueSlotNames.size) {
      throw new Error('Template contains duplicate slot names');
    }
  }
  
  private validateSlot(slot: WarblerSlot): void {
    if (!slot.name || slot.name.trim().length === 0) {
      throw new Error('Slot name is required');
    }
    
    const validTypes = ['string', 'number', 'boolean', 'object'];
    if (!validTypes.includes(slot.type)) {
      throw new Error(`Slot type must be one of: ${validTypes.join(', ')}`);
    }
  }
  
  private isValidVersion(version: string): boolean {
    // Basic semver validation
    const semverRegex = /^\d+\.\d+\.\d+$/;
    return semverRegex.test(version);
  }
  
  /**
   * Check if slots are satisfied by provided values
   */
  validateSlotValues(template: WarblerTemplate, slots: Record<string, unknown>): boolean {
    for (const requiredSlot of template.requiredSlots) {
      if (requiredSlot.required && !(requiredSlot.name in slots)) {
        return false;
      }
      
      const value = slots[requiredSlot.name];
      if (value !== undefined && !this.isValidSlotType(value, requiredSlot.type)) {
        return false;
      }
    }
    
    return true;
  }
  
  private isValidSlotType(value: unknown, expectedType: string): boolean {
    switch (expectedType) {
      case 'string':
        return typeof value === 'string';
      case 'number':
        return typeof value === 'number';
      case 'boolean':
        return typeof value === 'boolean';
      case 'object':
        return typeof value === 'object' && value !== null;
      default:
        return false;
    }
  }
}