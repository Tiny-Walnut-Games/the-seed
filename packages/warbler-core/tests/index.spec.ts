/**
 * Unit tests for Warbler Core functionality
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { 
  Warbler,
  WarblerTemplate,
  WarblerContext,
  WarblerIntent,
  RealizationEngine,
  ScoringEngine,
  TemplateManager
} from '../src/index.js';

describe('Warbler Core', () => {
  let warbler: Warbler;
  let mockTemplate: WarblerTemplate;
  let mockContext: WarblerContext;

  beforeEach(() => {
    warbler = new Warbler();
    
    mockTemplate = {
      id: 'test_greeting',
      version: '1.0.0',
      title: 'Test Greeting',
      description: 'A test greeting template',
      content: 'Hello {{user_name}}, welcome to {{location}}!',
      requiredSlots: [
        { name: 'user_name', type: 'string', required: true },
        { name: 'location', type: 'string', required: false }
      ],
      tags: ['greeting', 'test'],
      maxLength: 200
    };

    mockContext = {
      npcId: 'test_npc',
      sceneId: 'town_square',
      previousUtterances: [],
      worldState: { time_of_day: 'morning' },
      conversationHistory: []
    };
  });

  describe('Template Registration', () => {
    it('should register a template successfully', () => {
      warbler.registerTemplate(mockTemplate);
      const templates = warbler.getTemplates();
      
      expect(templates).toHaveLength(1);
      expect(templates[0].id).toBe('test_greeting');
    });

    it('should register multiple templates', () => {
      const template2 = { ...mockTemplate, id: 'test_farewell' };
      warbler.registerTemplates([mockTemplate, template2]);
      
      const templates = warbler.getTemplates();
      expect(templates).toHaveLength(2);
    });
  });

  describe('Conversation Processing', () => {
    beforeEach(() => {
      warbler.registerTemplate(mockTemplate);
    });

    it('should process user input and generate response', () => {
      const result = warbler.processConversation(
        'Hello there!',
        mockContext,
        { user_name: 'Adventurer' }
      );

      expect(result.success).toBe(true);
      expect(result.utterance).toBeDefined();
      expect(result.utterance?.content).toContain('Hello Adventurer');
      expect(result.utterance?.templateId).toBe('test_greeting');
    });

    it('should handle missing required slots', () => {
      const result = warbler.processConversation('Hello there!', mockContext);
      
      // Should fail or fallback gracefully when required slots can't be resolved
      expect(result.success).toBe(false);
      expect(result.error).toContain('candidate templates');
    });
  });

  describe('Intent Processing', () => {
    beforeEach(() => {
      warbler.registerTemplate(mockTemplate);
    });

    it('should process explicit intent', () => {
      const intent: WarblerIntent = {
        type: 'greeting',
        confidence: 0.9,
        slots: { greeting_type: 'formal' }
      };

      const result = warbler.processIntent(intent, mockContext, { user_name: 'Traveler' });
      
      expect(result.success).toBe(true);
      expect(result.utterance?.content).toContain('Hello Traveler');
    });
  });

  describe('System Info', () => {
    it('should report no templates when empty', () => {
      const info = warbler.getSystemInfo();
      
      expect(info.templateCount).toBe(0);
      expect(info.status).toBe('no-templates');
      expect(info.version).toBe('1.0.0');
    });

    it('should report ready status with templates', () => {
      warbler.registerTemplate(mockTemplate);
      const info = warbler.getSystemInfo();
      
      expect(info.templateCount).toBe(1);
      expect(info.status).toBe('ready');
    });
  });
});

describe('RealizationEngine', () => {
  let engine: RealizationEngine;
  let mockTemplate: WarblerTemplate;

  beforeEach(() => {
    engine = new RealizationEngine();
    
    mockTemplate = {
      id: 'combat_taunt',
      version: '1.0.0',
      title: 'Combat Taunt',
      description: 'A taunting response during combat',
      content: 'You dare challenge {{npc_name}}? Prepare yourself!',
      requiredSlots: [
        { name: 'npc_name', type: 'string', required: true }
      ],
      tags: ['combat', 'taunt'],
      maxLength: 100
    };
  });

  it('should realize utterance with proper slots', () => {
    engine.registerTemplate(mockTemplate);
    
    const intent: WarblerIntent = {
      type: 'combat',
      confidence: 0.8,
      slots: {}
    };

    const context: WarblerContext = {
      npcId: 'guard_001',
      sceneId: 'castle_gates',
      previousUtterances: [],
      worldState: {},
      conversationHistory: []
    };

    const result = engine.realize(intent, context);
    
    expect(result.success).toBe(true);
    expect(result.utterance?.content).toContain('Captain Marcus'); // From slot resolver
  });
});

describe('ScoringEngine', () => {
  let scorer: ScoringEngine;
  let templates: WarblerTemplate[];

  beforeEach(() => {
    scorer = new ScoringEngine();
    
    templates = [
      {
        id: 'greeting_formal',
        version: '1.0.0',
        title: 'Formal Greeting',
        description: 'A formal greeting',
        content: 'Good day to you.',
        requiredSlots: [],
        tags: ['greeting', 'formal']
      },
      {
        id: 'greeting_casual',
        version: '1.0.0', 
        title: 'Casual Greeting',
        description: 'A casual greeting',
        content: 'Hey there!',
        requiredSlots: [],
        tags: ['greeting', 'casual']
      }
    ];
  });

  it('should score templates based on intent relevance', () => {
    const intent: WarblerIntent = {
      type: 'greeting',
      confidence: 0.9,
      slots: {}
    };

    const context: WarblerContext = {
      npcId: 'test_npc',
      sceneId: 'test_scene',
      previousUtterances: [],
      worldState: {},
      conversationHistory: []
    };

    const scores = scorer.scoreTemplates(templates, intent, context);
    
    expect(scores).toHaveLength(2);
    expect(scores[0].relevance).toBeGreaterThan(0);
    expect(scores[0].total).toBeGreaterThan(0);
  });

  it('should get best scoring template', () => {
    const scores = [
      { templateId: 'template1', relevance: 0.5, contextFit: 0.3, novelty: 0.8, total: 0.53 },
      { templateId: 'template2', relevance: 0.8, contextFit: 0.7, novelty: 0.5, total: 0.68 }
    ];

    const best = scorer.getBestTemplate(scores);
    
    expect(best?.templateId).toBe('template2');
    expect(best?.total).toBe(0.68);
  });
});

describe('TemplateManager', () => {
  let manager: TemplateManager;

  beforeEach(() => {
    manager = new TemplateManager();
  });

  it('should validate template structure', () => {
    const invalidTemplate = {
      id: '',
      version: 'invalid',
      title: 'Test',
      description: 'Test',
      content: '',
      requiredSlots: [],
      tags: []
    };

    expect(() => manager.registerTemplate(invalidTemplate as WarblerTemplate)).toThrow();
  });

  it('should get templates by tags', () => {
    const template1 = {
      id: 'test1',
      version: '1.0.0',
      title: 'Test 1',
      description: 'Test',
      content: 'Content 1',
      requiredSlots: [],
      tags: ['greeting', 'formal']
    };

    const template2 = {
      id: 'test2',
      version: '1.0.0',
      title: 'Test 2', 
      description: 'Test',
      content: 'Content 2',
      requiredSlots: [],
      tags: ['farewell', 'casual']
    };

    manager.registerTemplate(template1);
    manager.registerTemplate(template2);

    const greetingTemplates = manager.getTemplatesByTags(['greeting']);
    expect(greetingTemplates).toHaveLength(1);
    expect(greetingTemplates[0].id).toBe('test1');
  });
});