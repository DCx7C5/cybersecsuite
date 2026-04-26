/**
 * Mention Insertion Validation
 * Parsing and validation logic for @mentions and special syntax
 */

export interface MentionMatch {
  type: 'user' | 'role' | 'team' | 'entity' | 'skill';
  value: string;
  displayName: string;
  startIndex: number;
  endIndex: number;
}

export interface ValidationResult {
  valid: boolean;
  mentions: MentionMatch[];
  errors: string[];
  warnings: string[];
}

/**
 * Parse mentions from text
 * Supports @user, @role:rolename, @team:teamname, @entity:type:id
 */
export function parseMentions(text: string): MentionMatch[] {
  const mentions: MentionMatch[] = [];

  // @username pattern
  const userPattern = /@([a-zA-Z0-9_-]+)(?!\w)/g;
  let match;

  while ((match = userPattern.exec(text)) !== null) {
    mentions.push({
      type: 'user',
      value: match[1],
      displayName: `@${match[1]}`,
      startIndex: match.index,
      endIndex: match.index + match[0].length,
    });
  }

  // @role:rolename pattern
  const rolePattern = /@role:([a-zA-Z0-9_-]+)(?!\w)/g;
  while ((match = rolePattern.exec(text)) !== null) {
    mentions.push({
      type: 'role',
      value: match[1],
      displayName: `@role:${match[1]}`,
      startIndex: match.index,
      endIndex: match.index + match[0].length,
    });
  }

  // @team:teamname pattern
  const teamPattern = /@team:([a-zA-Z0-9_-]+)(?!\w)/g;
  while ((match = teamPattern.exec(text)) !== null) {
    mentions.push({
      type: 'team',
      value: match[1],
      displayName: `@team:${match[1]}`,
      startIndex: match.index,
      endIndex: match.index + match[0].length,
    });
  }

  // @entity:type:id pattern
  const entityPattern = /@entity:([a-zA-Z0-9_-]+):([a-zA-Z0-9_-]+)(?!\w)/g;
  while ((match = entityPattern.exec(text)) !== null) {
    mentions.push({
      type: 'entity',
      value: `${match[1]}:${match[2]}`,
      displayName: `@entity:${match[1]}:${match[2]}`,
      startIndex: match.index,
      endIndex: match.index + match[0].length,
    });
  }

  // #skill pattern
  const skillPattern = /#([a-zA-Z0-9_-]+)(?!\w)/g;
  while ((match = skillPattern.exec(text)) !== null) {
    mentions.push({
      type: 'skill',
      value: match[1],
      displayName: `#${match[1]}`,
      startIndex: match.index,
      endIndex: match.index + match[0].length,
    });
  }

  // Sort by start index
  mentions.sort((a, b) => a.startIndex - b.startIndex);

  return mentions;
}

/**
 * Check for overlapping mentions
 */
export function checkOverlappingMentions(mentions: MentionMatch[]): boolean {
  for (let i = 0; i < mentions.length - 1; i++) {
    const current = mentions[i];
    const next = mentions[i + 1];

    if (current.endIndex > next.startIndex) {
      return true; // Overlapping
    }
  }

  return false;
}

/**
 * Validate mention references against available entities
 */
export function validateMentionReferences(
  mentions: MentionMatch[],
  availableUsers: string[] = [],
  availableRoles: string[] = [],
  availableTeams: string[] = [],
  availableSkills: string[] = [],
  availableEntityTypes: string[] = []
): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  const validMentions: MentionMatch[] = [];

  mentions.forEach((mention) => {
    switch (mention.type) {
      case 'user':
        if (availableUsers.length > 0 && !availableUsers.includes(mention.value)) {
          warnings.push(`Unknown user: @${mention.value}`);
        } else {
          validMentions.push(mention);
        }
        break;

      case 'role':
        if (availableRoles.length > 0 && !availableRoles.includes(mention.value)) {
          errors.push(`Unknown role: @role:${mention.value}`);
        } else {
          validMentions.push(mention);
        }
        break;

      case 'team':
        if (availableTeams.length > 0 && !availableTeams.includes(mention.value)) {
          errors.push(`Unknown team: @team:${mention.value}`);
        } else {
          validMentions.push(mention);
        }
        break;

      case 'entity': {
        const [type, id] = mention.value.split(':');
        if (availableEntityTypes.length > 0 && !availableEntityTypes.includes(type)) {
          errors.push(`Unknown entity type: ${type}`);
        } else {
          validMentions.push(mention);
        }
        break;
      }

      case 'skill':
        if (availableSkills.length > 0 && !availableSkills.includes(mention.value)) {
          warnings.push(`Unknown skill: #${mention.value}`);
        } else {
          validMentions.push(mention);
        }
        break;
    }
  });

  const overlapping = checkOverlappingMentions(mentions);
  if (overlapping) {
    errors.push('Overlapping mentions detected');
  }

  return {
    valid: errors.length === 0,
    mentions: validMentions,
    errors,
    warnings,
  };
}

/**
 * Replace mentions in text with tokens or formatted strings
 */
export function replaceMentions(
  text: string,
  replacer: (mention: MentionMatch) => string
): string {
  const mentions = parseMentions(text);

  if (mentions.length === 0) {
    return text;
  }

  let result = '';
  let lastIndex = 0;

  mentions.forEach((mention) => {
    result += text.slice(lastIndex, mention.startIndex);
    result += replacer(mention);
    lastIndex = mention.endIndex;
  });

  result += text.slice(lastIndex);
  return result;
}

/**
 * Extract unique mention values by type
 */
export function extractMentionsByType(
  mentions: MentionMatch[],
  type: MentionMatch['type']
): string[] {
  return [...new Set(mentions.filter((m) => m.type === type).map((m) => m.value))];
}
