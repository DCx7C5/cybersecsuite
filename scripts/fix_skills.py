import os
import yaml
import re
from pathlib import Path

# Canonical action verbs (22 total)
CANONICAL_VERBS = {
    'blue': ['detect', 'analyze', 'audit', 'monitor', 'hunt', 'forensic', 'harden', 'recover', 'respond', 'verify', 'parse', 'collect'],
    'red': ['exploit', 'bypass', 'extract', 'enum', 'inject', 'persist', 'escalate', 'pivot', 'intercept', 'simulate'],
    'neutral': ['configure', 'deploy']
}
ALL_VERBS = [v for sublist in CANONICAL_VERBS.values() for v in sublist]

# Mapping for non-canonical verbs to canonical ones
VERB_MAPPING = {
    'pentest': 'audit',
    'assess': 'analyze',
    'execute': 'deploy',
    'overview': 'monitor',
    'implement': 'configure',
    'create': 'deploy',
    # Add more as needed based on errors
}

def derive_name_from_path(domain, subsystem, tool, action):
    # Name: subsystem-tool-action or subsystem-tool or domain-subsystem
    if action:
        return f"{subsystem}-{tool}-{action}"
    elif tool:
        return f"{subsystem}-{tool}"
    else:
        return f"{domain}-{subsystem}"

def map_action_to_canonical(action):
    return VERB_MAPPING.get(action, action) if action in VERB_MAPPING else action

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Split YAML frontmatter and body
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_str, body = parts[1], parts[2]
        else:
            yaml_str, body = ''
    else:
        yaml_str, body = '', content

    # Parse YAML
    try:
        data = yaml.safe_load(yaml_str) or {}
    except yaml.YAMLError:
        data = {}

    # Get path parts
    path = Path(filepath)
    path_parts = path.parts
    # Assuming .claude/skills.disabled/domain/subsystem/tool/action/SKILL.md
    # So domain = path_parts[3], subsystem = path_parts[4], tool = path_parts[5], action = path_parts[6] if len > 6
    domain = path_parts[3] if len(path_parts) > 3 else ''
    subsystem = path_parts[4] if len(path_parts) > 4 else ''
    tool = path_parts[5] if len(path_parts) > 5 else ''
    action = path_parts[6] if len(path_parts) > 6 else ''

    # Fix name
    correct_name = derive_name_from_path(domain, subsystem, tool, action)
    if data.get('name') != correct_name:
        data['name'] = correct_name
        print(f"Fixed name in {filepath}: {correct_name}")

    # Fix action
    canonical_action = map_action_to_canonical(action)
    if action != canonical_action:
        # Rename directory if needed (simulate mv)
        new_dir = path.parent.parent / canonical_action
        new_filepath = new_dir / 'SKILL.md'
        os.makedirs(new_dir, exist_ok=True)
        os.rename(filepath, new_filepath)
        filepath = new_filepath
        print(f"Renamed action dir in {filepath}: {action} -> {canonical_action}")

    # Fix description format (already done previously, but ensure)
    if 'description' in data:
        desc = data['description']
        if isinstance(desc, str) and not desc.startswith('\n'):
            data['description'] = '>\n  ' + desc.replace('>', '').strip()

    # Fill content-less body
    if not body.strip():
        desc = data.get('description', '').replace('>\n  ', '').strip()
        body = f"# {data.get('name', 'Skill')}\n\n## Description\n{desc}\n\n## Usage\n[Placeholder: Add detailed steps here based on taxonomy.]\n\n## Examples\n[Placeholder: Provide code/command examples.]\n\n## References\n[Placeholder: Link to docs/tools.]\n"
        print(f"Added content to {filepath}")

    # Verify location (basic check: domain in path matches description keywords)
    desc_lower = data.get('description', '').lower()
    if domain not in desc_lower and domain:
        print(f"Warning: Location mismatch in {filepath} (domain '{domain}' not in description)")

    # Write back
    new_yaml = yaml.dump(data, default_flow_style=False)
    new_content = f"---\n{new_yaml}---\n{body}"
    with open(filepath, 'w') as f:
        f.write(new_content)

# Scan and fix all SKILL.md files
skills_dir = Path('.claude/skills.disabled')
for md_file in skills_dir.rglob('SKILL.md'):
    fix_file(md_file)

print("All skill fixes applied. Check logs for details.")
