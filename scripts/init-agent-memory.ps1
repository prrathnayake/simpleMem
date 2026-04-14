$dir = ".agent_memories"
New-Item -ItemType Directory -Force -Path "$dir"

Set-Content -Path "AGENTS.md" -Value "AGENTS: Your memory system is a graph. Go specifically to .agent_memories/_agent_rules.md now.`n"

# Core files
New-Item -Path "$dir/_agent_rules.md" -ItemType File -Force
New-Item -Path "$dir/project_state.md" -ItemType File -Force
New-Item -Path "$dir/folder_map.md" -ItemType File -Force
