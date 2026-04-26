/**
 * Tests for Command Execution Engine
 */

import {
  parseCommand,
  validateCommand,
  executeCommand,
  CommandRegistryBuilder,
  createCommand,
} from '../../src/dashboard/static/ts/utils/commandEngine';

describe('parseCommand', () => {
  it('should parse simple command', () => {
    const result = parseCommand('help');
    expect(result.command).toBe('help');
    expect(result.args).toEqual([]);
  });

  it('should parse command with arguments', () => {
    const result = parseCommand('echo hello world');
    expect(result.command).toBe('echo');
    expect(result.args).toEqual(['hello', 'world']);
  });

  it('should handle multiple spaces', () => {
    const result = parseCommand('echo   hello    world');
    expect(result.command).toBe('echo');
    expect(result.args).toEqual(['hello', 'world']);
  });

  it('should be case-insensitive', () => {
    const result = parseCommand('ECHO hello');
    expect(result.command).toBe('echo');
  });

  it('should handle empty input', () => {
    const result = parseCommand('   ');
    expect(result.command).toBe('');
    expect(result.args).toEqual([]);
  });
});

describe('validateCommand', () => {
  const registry = {
    help: createCommand('help', 'Show help', async () => 'Help text'),
    echo: createCommand('echo', 'Echo text', async (args) => args.join(' '), {
      argsCount: 1,
    }),
  };

  it('should validate known command', () => {
    const result = validateCommand('help', [], registry);
    expect(result.valid).toBe(true);
  });

  it('should reject unknown command', () => {
    const result = validateCommand('unknown', [], registry);
    expect(result.valid).toBe(false);
    expect(result.error).toMatch(/Unknown command/);
  });

  it('should check argument count', () => {
    const result = validateCommand('echo', [], registry);
    expect(result.valid).toBe(false);
    expect(result.error).toMatch(/expects 1 arguments/);
  });

  it('should validate with custom validator', () => {
    const customRegistry = {
      validate: createCommand('validate', 'Test', async (args) => args[0], {
        validate: (args) => args[0] === 'valid',
      }),
    };

    const result1 = validateCommand('validate', ['valid'], customRegistry);
    expect(result1.valid).toBe(true);

    const result2 = validateCommand('validate', ['invalid'], customRegistry);
    expect(result2.valid).toBe(false);
  });
});

describe('executeCommand', () => {
  const registry = {
    echo: createCommand('echo', 'Echo text', async (args) => args.join(' ')),
    greet: createCommand('greet', 'Greet', async (args) => `Hello ${args[0]}!`),
  };

  it('should execute command successfully', async () => {
    const result = await executeCommand('echo hello world', registry);
    expect(result.success).toBe(true);
    expect(result.output).toBe('hello world');
    expect(result.command).toBe('echo');
  });

  it('should handle unknown command', async () => {
    const result = await executeCommand('unknown', registry);
    expect(result.success).toBe(false);
    expect(result.error).toMatch(/Unknown command/);
  });

  it('should handle empty input', async () => {
    const result = await executeCommand('', registry);
    expect(result.success).toBe(false);
    expect(result.error).toBe('Empty command');
  });

  it('should handle command execution errors', async () => {
    const errorRegistry = {
      error: createCommand('error', 'Error', async () => {
        throw new Error('Test error');
      }),
    };

    const result = await executeCommand('error', errorRegistry);
    expect(result.success).toBe(false);
    expect(result.error).toBe('Test error');
  });
});

describe('CommandRegistryBuilder', () => {
  it('should build registry', () => {
    const builder = new CommandRegistryBuilder();
    builder.register(createCommand('help', 'Help', async () => 'Help'));
    const registry = builder.build();

    expect(registry['help']).toBeDefined();
  });

  it('should register multiple commands', () => {
    const builder = new CommandRegistryBuilder();
    builder.registerMultiple([
      createCommand('help', 'Help', async () => 'Help'),
      createCommand('echo', 'Echo', async (args) => args.join(' ')),
    ]);

    const registry = builder.build();
    expect(Object.keys(registry)).toHaveLength(2);
  });

  it('should get command', () => {
    const builder = new CommandRegistryBuilder();
    const cmd = createCommand('test', 'Test', async () => 'Test');
    builder.register(cmd);

    expect(builder.getCommand('test')).toBeDefined();
  });

  it('should list commands', () => {
    const builder = new CommandRegistryBuilder();
    builder.registerMultiple([
      createCommand('help', 'Help', async () => 'Help'),
      createCommand('echo', 'Echo', async (args) => args.join(' ')),
    ]);

    const commands = builder.listCommands();
    expect(commands).toContain('help');
    expect(commands).toContain('echo');
  });

  it('should handle case-insensitive lookup', () => {
    const builder = new CommandRegistryBuilder();
    builder.register(createCommand('HELP', 'Help', async () => 'Help'));

    expect(builder.getCommand('help')).toBeDefined();
    expect(builder.getCommand('HELP')).toBeDefined();
  });
});
