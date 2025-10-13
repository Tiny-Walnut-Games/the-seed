// Quick compilation test for Warbler Pack
// This verifies our types and imports work correctly

import { WarblerTemplate, WarblerPackMetadata } from './warbler-core';

// Test: Can we import and use our local types?
const testTemplate: WarblerTemplate = {
  id: 'test',
  version: '1.0.0',
  title: 'Test Template',
  description: 'Test',
  content: 'Hello {{name}}!',
  requiredSlots: [],
  tags: [],
  maxLength: 100
};

const testMetadata: WarblerPackMetadata = {
  name: 'Test Pack',
  version: '1.0.0',
  description: 'Test',
  author: 'Test Author',
  templates: [testTemplate]
};

export { testTemplate, testMetadata };
