/**
 * Tests for Mention Validation
 */

import {
  parseMentions,
  checkOverlappingMentions,
  validateMentionReferences,
  replaceMentions,
  extractMentionsByType,
} from '../../src/dashboard/static/ts/utils/mentionValidation';

describe('parseMentions', () => {
  it('should parse user mentions', () => {
    const text = '@alice and @bob';
    const mentions = parseMentions(text);

    expect(mentions).toHaveLength(2);
    expect(mentions[0].type).toBe('user');
    expect(mentions[0].value).toBe('alice');
    expect(mentions[1].value).toBe('bob');
  });

  it('should parse role mentions', () => {
    const text = '@role:admin and @role:moderator';
    const mentions = parseMentions(text);

    expect(mentions).toHaveLength(2);
    expect(mentions[0].type).toBe('role');
    expect(mentions[0].value).toBe('admin');
  });

  it('should parse team mentions', () => {
    const text = '@team:frontend @team:backend';
    const mentions = parseMentions(text);

    expect(mentions).toHaveLength(2);
    expect(mentions[0].type).toBe('team');
    expect(mentions[0].value).toBe('frontend');
  });

  it('should parse entity mentions', () => {
    const text = '@entity:ioc:192.168.1.1';
    const mentions = parseMentions(text);

    expect(mentions).toHaveLength(1);
    expect(mentions[0].type).toBe('entity');
    expect(mentions[0].value).toBe('ioc:192.168.1.1');
  });

  it('should parse skills mentions', () => {
    const text = '#python #javascript';
    const mentions = parseMentions(text);

    expect(mentions).toHaveLength(2);
    expect(mentions[0].type).toBe('skills');
    expect(mentions[0].value).toBe('python');
  });

  it('should handle mixed mentions', () => {
    const text = '@alice @role:admin #python @entity:ioc:123';
    const mentions = parseMentions(text);

    expect(mentions).toHaveLength(4);
  });

  it('should return empty array for no mentions', () => {
    const text = 'No mentions here';
    const mentions = parseMentions(text);

    expect(mentions).toHaveLength(0);
  });

  it('should not match partial words', () => {
    const text = 'email@example.com is not @user';
    const mentions = parseMentions(text);

    expect(mentions).toHaveLength(1);
    expect(mentions[0].value).toBe('user');
  });
});

describe('checkOverlappingMentions', () => {
  it('should detect no overlap in non-overlapping mentions', () => {
    const mentions = [
      { type: 'user', value: 'alice', displayName: '@alice', startIndex: 0, endIndex: 6 },
      { type: 'user', value: 'bob', displayName: '@bob', startIndex: 11, endIndex: 15 },
    ];

    expect(checkOverlappingMentions(mentions)).toBe(false);
  });

  it('should detect overlapping mentions', () => {
    const mentions = [
      { type: 'user', value: 'alice', displayName: '@alice', startIndex: 0, endIndex: 6 },
      { type: 'role', value: 'admin', displayName: '@role:admin', startIndex: 3, endIndex: 14 },
    ];

    expect(checkOverlappingMentions(mentions)).toBe(true);
  });

  it('should handle single mention', () => {
    const mentions = [
      { type: 'user', value: 'alice', displayName: '@alice', startIndex: 0, endIndex: 6 },
    ];

    expect(checkOverlappingMentions(mentions)).toBe(false);
  });

  it('should handle empty list', () => {
    expect(checkOverlappingMentions([])).toBe(false);
  });
});

describe('validateMentionReferences', () => {
  it('should validate known references', () => {
    const mentions = [
      { type: 'user', value: 'alice', displayName: '@alice', startIndex: 0, endIndex: 6 },
    ];

    const result = validateMentionReferences(mentions, ['alice', 'bob']);

    expect(result.valid).toBe(true);
    expect(result.mentions).toHaveLength(1);
  });

  it('should warn on unknown user', () => {
    const mentions = [
      { type: 'user', value: 'charlie', displayName: '@charlie', startIndex: 0, endIndex: 8 },
    ];

    const result = validateMentionReferences(mentions, ['alice', 'bob']);

    expect(result.warnings).toContain(expect.stringMatching(/Unknown user/));
  });

  it('should error on unknown role', () => {
    const mentions = [
      { type: 'role', value: 'superadmin', displayName: '@role:superadmin', startIndex: 0, endIndex: 16 },
    ];

    const result = validateMentionReferences(mentions, undefined, ['admin', 'user']);

    expect(result.valid).toBe(false);
    expect(result.errors).toContain(expect.stringMatching(/Unknown role/));
  });

  it('should validate teams', () => {
    const mentions = [
      { type: 'team', value: 'frontend', displayName: '@team:frontend', startIndex: 0, endIndex: 14 },
    ];

    const result = validateMentionReferences(mentions, undefined, undefined, ['frontend', 'backend']);

    expect(result.valid).toBe(true);
  });

  it('should validate skills', () => {
    const mentions = [
      { type: 'skills', value: 'python', displayName: '#python', startIndex: 0, endIndex: 7 },
    ];

    const result = validateMentionReferences(mentions, undefined, undefined, undefined, ['python', 'javascript']);

    expect(result.valid).toBe(true);
  });
});

describe('replaceMentions', () => {
  it('should replace mentions', () => {
    const text = '@alice and @bob';
    const result = replaceMentions(text, (mention) => `[${mention.value}]`);

    expect(result).toBe('[alice] and [bob]');
  });

  it('should handle no replacements', () => {
    const text = 'No mentions';
    const result = replaceMentions(text, (mention) => `[${mention.value}]`);

    expect(result).toBe('No mentions');
  });

  it('should replace with custom format', () => {
    const text = '@alice';
    const result = replaceMentions(text, (mention) => `<@${mention.value}>`);

    expect(result).toBe('<@alice>');
  });
});

describe('extractMentionsByType', () => {
  it('should extract mentions by type', () => {
    const mentions = [
      { type: 'user', value: 'alice', displayName: '@alice', startIndex: 0, endIndex: 6 },
      { type: 'user', value: 'bob', displayName: '@bob', startIndex: 11, endIndex: 15 },
      { type: 'role', value: 'admin', displayName: '@role:admin', startIndex: 20, endIndex: 31 },
    ];

    const users = extractMentionsByType(mentions, 'user');
    expect(users).toEqual(['alice', 'bob']);
  });

  it('should return unique values', () => {
    const mentions = [
      { type: 'user', value: 'alice', displayName: '@alice', startIndex: 0, endIndex: 6 },
      { type: 'user', value: 'alice', displayName: '@alice', startIndex: 20, endIndex: 26 },
    ];

    const users = extractMentionsByType(mentions, 'user');
    expect(users).toEqual(['alice']);
  });
});
