/**
 * Warbler Core Pack - Essential conversation templates
 * 
 * Re-exports templates for dynamic loading in the Warbler conversation system
 * 
 * 🏆 STANDALONE VERSION - No external dependencies required!
 */

import { WarblerTemplate, WarblerPackMetadata } from './warbler-core';

// 🔥 BUTT-SAVING PROTOCOL: Mock data for compilation testing
// In production, this would be replaced with actual JSON import
const mockTemplatesData = {
  packInfo: {
    name: 'Warbler Core Pack',
    version: '0.1.0',
    description: 'Core conversation pack for Warbler NPC system',
    author: 'TWG Team',
    compatibleEngine: '^0.1.0'
  },
  templates: [
    {
      id: 'greeting_friendly',
      version: '1.0.0',
      title: 'Friendly Greeting',
      description: 'A warm, friendly greeting',
      content: 'Hello there, {{name}}! Great to see you!',
      requiredSlots: [
        { name: 'name', type: 'string', required: true, description: 'Name of the person being greeted' }
      ],
      tags: ['greeting', 'friendly', 'warm'],
      maxLength: 100
    }
  ] as WarblerTemplate[]
};

// Transform JSON data to proper WarblerTemplate objects
export const templates: WarblerTemplate[] = mockTemplatesData.templates.map(template => ({
  ...template,
  requiredSlots: template.requiredSlots.map(slot => ({
    name: slot.name,
    type: slot.type as 'string' | 'number' | 'boolean' | 'object',
    required: slot.required,
    description: slot.description
  }))
}));

export const packMetadata: WarblerPackMetadata = {
  name: mockTemplatesData.packInfo.name,
  version: mockTemplatesData.packInfo.version,
  description: mockTemplatesData.packInfo.description,
  author: mockTemplatesData.packInfo.author,
  templates
};

// Export individual templates for selective imports
export const greetingFriendly = templates.find(t => t.id === 'greeting_friendly')!;

// Default export for easy bulk import
export default {
  templates,
  packMetadata,
  greetingFriendly
};

// 🎉 Silent success - no console output needed
// If needed for debugging, use console.log() - now properly supported with DOM lib
