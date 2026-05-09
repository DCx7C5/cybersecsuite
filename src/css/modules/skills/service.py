"""Service-layer operations for skills."""

from css.modules.skills.models import SkillDefinition, SkillDefinitionModel
from css.modules.skills.registry import SkillRegistry


async def create_skill(skill: SkillDefinition, *, is_builtin: bool = False) -> SkillDefinition:
    """Persist and register a new skill definition."""
    record = SkillDefinitionModel.from_domain(skill, is_builtin=is_builtin)
    await record.save()
    registry = SkillRegistry()
    if registry.get(skill.skill_id) is None:
        registry.register(skill)
    else:
        registry.update_skill(
            skill.skill_id,
            status=skill.status,
            description=skill.description,
            custom_metadata=skill.custom_metadata,
        )
    return skill


async def update_skill(skill: SkillDefinition) -> SkillDefinition:
    """Persist and register an updated skill definition."""
    record = await SkillDefinitionModel.get_or_none(skill_id=skill.skill_id)
    if record is None:
        return await create_skill(skill)

    updated = SkillDefinitionModel.from_domain(skill, is_builtin=record.is_builtin)
    updated.id = record.id
    await updated.save()
    registry = SkillRegistry()
    if registry.get(skill.skill_id) is None:
        registry.register(skill)
    else:
        registry.update_skill(
            skill.skill_id,
            status=skill.status,
            description=skill.description,
            custom_metadata=skill.custom_metadata,
        )
    return skill


async def delete_skill(skill_id: str) -> bool:
    """Delete a skill definition from DB and runtime registry."""
    deleted_count = await SkillDefinitionModel.filter(skill_id=skill_id).delete()
    SkillRegistry().deregister(skill_id)
    return deleted_count > 0
