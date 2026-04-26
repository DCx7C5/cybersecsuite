/**
 * Command Execution Engine
 * Parses and executes commands with argument validation
 */

export interface Command {
  name: string;
  execute: (args: string[]) => Promise<string>;
  validate?: (args: string[]) => boolean;
  description: string;
  argsCount?: number;
}

export interface CommandRegistry {
  [key: string]: Command;
}

export interface ExecutionResult {
  success: boolean;
  output: string;
  error?: string;
  command: string;
  args: string[];
}

/**
 * Parse command input string into command name and arguments
 */
export function parseCommand(input: string): { command: string; args: string[] } {
  const trimmed = input.trim();
  if (!trimmed) {
    return { command: '', args: [] };
  }

  const parts = trimmed.split(/\s+/);
  const command = parts[0].toLowerCase();
  const args = parts.slice(1);

  return { command, args };
}

/**
 * Validate command against registry
 */
export function validateCommand(
  command: string,
  args: string[],
  registry: CommandRegistry
): { valid: boolean; error?: string } {
  const cmd = registry[command];

  if (!cmd) {
    return { valid: false, error: `Unknown command: ${command}` };
  }

  if (cmd.argsCount !== undefined && args.length !== cmd.argsCount) {
    return {
      valid: false,
      error: `${command} expects ${cmd.argsCount} arguments, got ${args.length}`,
    };
  }

  if (cmd.validate && !cmd.validate(args)) {
    return { valid: false, error: `Invalid arguments for command: ${command}` };
  }

  return { valid: true };
}

/**
 * Execute a command
 */
export async function executeCommand(
  input: string,
  registry: CommandRegistry
): Promise<ExecutionResult> {
  try {
    const { command, args } = parseCommand(input);

    if (!command) {
      return {
        success: false,
        output: '',
        error: 'Empty command',
        command: '',
        args: [],
      };
    }

    const validation = validateCommand(command, args, registry);
    if (!validation.valid) {
      return {
        success: false,
        output: '',
        error: validation.error,
        command,
        args,
      };
    }

    const cmd = registry[command];
    const output = await cmd.execute(args);

    return {
      success: true,
      output,
      command,
      args,
    };
  } catch (e) {
    const error = e instanceof Error ? e.message : String(e);
    return {
      success: false,
      output: '',
      error,
      command: '',
      args: [],
    };
  }
}

/**
 * Create a command registry builder
 */
export class CommandRegistryBuilder {
  private registry: CommandRegistry = {};

  register(command: Command): this {
    this.registry[command.name.toLowerCase()] = command;
    return this;
  }

  registerMultiple(commands: Command[]): this {
    commands.forEach((cmd) => this.register(cmd));
    return this;
  }

  build(): CommandRegistry {
    return { ...this.registry };
  }

  getCommand(name: string): Command | undefined {
    return this.registry[name.toLowerCase()];
  }

  listCommands(): string[] {
    return Object.keys(this.registry);
  }
}

/**
 * Helper to create a command
 */
export function createCommand(
  name: string,
  description: string,
  execute: (args: string[]) => Promise<string>,
  options?: {
    validate?: (args: string[]) => boolean;
    argsCount?: number;
  }
): Command {
  return {
    name: name.toLowerCase(),
    description,
    execute,
    validate: options?.validate,
    argsCount: options?.argsCount,
  };
}
