# Warbler Core

Core runtime engine for the Warbler NPC conversation and narration system.

## Overview

Warbler Core provides the foundational conversation engine for NPCs in interactive applications, games, and narrative experiences. It features template-based content generation, intent recognition, context-aware scoring, and dynamic slot resolution.

## Features

- **Template-Based Conversations**: Define reusable conversation templates with dynamic slot filling
- **Intent Recognition**: Process user input and classify conversational intents  
- **Context-Aware Scoring**: Score and rank templates based on conversation context and history
- **Dynamic Slot Resolution**: Automatically resolve template variables from context and world state
- **Conversation Memory**: Track conversation history to avoid repetitive responses
- **Extensible Architecture**: Plugin-friendly design for custom templates and behavior

## Installation

```bash
npm install warbler-core
```

## Quick Start

```typescript
import { Warbler, WarblerTemplate, WarblerContext } from 'warbler-core';

// Create warbler instance
const warbler = new Warbler();

// Define a conversation template
const greetingTemplate: WarblerTemplate = {
  id: 'friendly_greeting',
  version: '1.0.0',
  title: 'Friendly Greeting',
  description: 'A warm greeting for friendly NPCs',
  content: 'Hello {{user_name}}! Welcome to {{location}}. How can I help you today?',
  requiredSlots: [
    { name: 'user_name', type: 'string', required: true },
    { name: 'location', type: 'string', required: false }
  ],
  tags: ['greeting', 'friendly', 'help'],
  maxLength: 200
};

// Register template
warbler.registerTemplate(greetingTemplate);

// Set up conversation context
const context: WarblerContext = {
  npcId: 'merchant_001',
  sceneId: 'marketplace',
  previousUtterances: [],
  worldState: { time_of_day: 'afternoon' },
  conversationHistory: []
};

// Process user input
const result = warbler.processConversation(
  'Hello there!',
  context,
  { user_name: 'Adventurer' }
);

if (result.success) {
  console.log('NPC Response:', result.utterance?.content);
  // Output: "Hello Adventurer! Welcome to the bustling marketplace. How can I help you today?"
}
```

## Core Concepts

### Templates

Templates define the structure and content of NPC responses. Each template includes:

- **Content**: The response text with slot placeholders (`{{slot_name}}`)
- **Required Slots**: Variables that must be provided or resolved from context
- **Tags**: Keywords for template categorization and selection
- **Version**: Semantic version for template evolution

### Intents

Intents represent the user's conversational goal:

- `greeting` - Casual hellos and conversation starters
- `farewell` - Goodbyes and conversation endings  
- `help_request` - Requests for assistance
- `trade_inquiry` - Commerce and trading conversations
- `combat_initiation` - Hostile or combat interactions

### Context

Context provides the situational awareness for conversation generation:

- **NPC ID**: Identity of the speaking character
- **Scene ID**: Current location or scenario
- **World State**: Global game/application state
- **Conversation History**: Previous utterances in the conversation

### Scoring

Templates are scored and ranked based on:

- **Relevance** (50%): How well the template matches the detected intent
- **Context Fit** (30%): How appropriate the template is for the current situation  
- **Novelty** (20%): How recently the template has been used (to avoid repetition)

## API Reference

### Warbler Class

Main conversation manager class.

#### Methods

- `registerTemplate(template: WarblerTemplate)`: Register a single template
- `registerTemplates(templates: WarblerTemplate[])`: Register multiple templates
- `processConversation(input: string, context: WarblerContext, slots?: Record<string, unknown>)`: Process user input and generate response
- `processIntent(intent: WarblerIntent, context: WarblerContext, slots?: Record<string, unknown>)`: Generate response from explicit intent
- `getTemplates()`: Get all registered templates
- `getSystemInfo()`: Get system status and configuration

### Core Components

- **RealizationEngine**: Orchestrates template selection and content generation
- **TemplateManager**: Manages template registration and retrieval
- **ScoringEngine**: Scores and ranks templates for selection
- **SlotResolver**: Resolves dynamic variables in template content
- **IntentProcessor**: Processes user input and extracts conversational intent

## Versioning Policy

Warbler Core follows semantic versioning with specific conventions for conversation systems:

- **Major versions** introduce breaking changes to template contracts or core APIs
- **Minor versions** add new features, intent types, or slot resolvers while maintaining backward compatibility
- **Patch versions** contain bug fixes and safe improvements to existing functionality

Template content packs should specify compatible engine versions in their dependencies.

## Advanced Usage

### Custom Slot Resolvers

```typescript
import { SlotResolver } from 'warbler-core';

class CustomSlotResolver extends SlotResolver {
  resolveFromContext(slot: WarblerSlot, context: WarblerContext): unknown {
    // Custom slot resolution logic
    if (slot.name === 'player_level') {
      return context.worldState.playerLevel || 1;
    }
    return super.resolveFromContext(slot, context);
  }
}
```

### Template Validation

Templates are automatically validated on registration:

- Required fields presence
- Semantic version format
- Slot type consistency  
- Content length limits
- Unique slot names

### Error Handling

The conversation system gracefully handles various error conditions:

- Missing templates for intent types
- Unresolvable required slots
- Invalid template syntax
- Context inconsistencies

Failed realizations return descriptive error messages without crashing the conversation flow.

## Contributing

Warbler Core is part of the broader Warbler conversation system. Contributions are welcome!

### Development Setup

```bash
git clone <repository>
cd packages/warbler-core
npm install
npm run build
npm test
```

### Testing

```bash
npm run test          # Run all tests
npm run test:watch    # Watch mode for development
npm run test:coverage # Generate coverage report
```

## License

MIT License - see LICENSE file for details.

## Related Packages

- `warbler-pack-core` - Core conversation templates
- `warbler-pack-faction-politics` - Political intrigue templates
- Additional content packs available in the Warbler ecosystem