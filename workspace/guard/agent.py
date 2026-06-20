"""Release Guardrails — wiring the guard into the Antigravity SDK.

This is the live layer. It builds a deny-by-default agent for a release repo:

- raw shell (`run_command`) is DISABLED via CapabilitiesConfig, so force-push,
  package installs, and `rm` are unavailable;
- a declarative `policy` list denies reads of sealed secrets and edits of
  protected paths (migrations, secrets), with a reason the agent sees;
- a curated `kubectl` host tool is the only way to touch the cluster, and it
  rewrites a destructive `delete` to `--dry-run=client` before it runs;
- a post-tool Inspect hook audits everything that executed.

The decision logic (policy.py / tools.py / audit.py) is pure and unit-tested
offline; this file is what you run to drive a real agent.

Run:  pip install google-antigravity  &&  python -m guard.agent
"""

import asyncio
import os
from pathlib import Path

from google.antigravity import Agent, CapabilitiesConfig, LocalAgentConfig, types
from google.antigravity.hooks import hooks, policy

from .audit import audit_line
from .policy import is_protected, is_secret
from .tools import kubectl

# The project root is the folder that holds this guard package (the workspace),
# pinned explicitly so the agent resolves data/ and migrations/ here rather than
# walking up to the enclosing git root.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)


def _auth_kwargs() -> dict:
    """Pick the model backend from the environment.

    - If GOOGLE_CLOUD_PROJECT is set, use the Vertex AI backend (enterprise /
      cloud-project auth via Application Default Credentials — run
      `gcloud auth application-default login` first). Region comes from
      GOOGLE_CLOUD_LOCATION (default "global").
    - Otherwise fall back to the Gemini Developer API key (GEMINI_API_KEY).
    """
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project:
        return {
            "vertex": True,
            "project": project,
            "location": os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
        }
    return {}


def _path(args: dict) -> str:
    return args.get("path") or args.get("file_path") or args.get("TargetFile") or ""


# Post-tool Inspect hook: read-only audit of everything the agent actually ran.
@hooks.post_tool_call
async def release_audit(data) -> None:
    print(audit_line(data))


def build_config() -> LocalAgentConfig:
    view = types.BuiltinTools.VIEW_FILE.value
    edit = types.BuiltinTools.EDIT_FILE.value
    create = types.BuiltinTools.CREATE_FILE.value
    run_command = types.BuiltinTools.RUN_COMMAND.value

    policies = [
        # Deny-by-default: nothing is permitted unless explicitly allowed below.
        policy.deny_all(),
        # Reads are allowed, except sealed secrets (specific deny outranks allow).
        policy.allow(view),
        policy.deny(view, when=lambda a: is_secret(_path(a)), name="no-read-secrets"),
        # Edits/creates are allowed, except protected paths (migrations, secrets).
        policy.allow(edit),
        policy.allow(create),
        policy.deny(edit, when=lambda a: is_protected(_path(a)), name="protect-edit"),
        policy.deny(create, when=lambda a: is_protected(_path(a)), name="protect-create"),
        # The curated cluster tool is allowed; it sanitizes its own arguments.
        policy.allow(kubectl.__name__),
    ]

    return LocalAgentConfig(
        system_instructions=(
            "You are a release engineer working in this repository. Raw shell is "
            "unavailable; use the curated `kubectl` tool for cluster operations. "
            "If an action is denied, read the reason and adapt."
        ),
        # Disable raw shell entirely — the strongest guardrail (the tool is removed
        # from the model's context, not just denied at call time).
        capabilities=CapabilitiesConfig(disabled_tools=[run_command]),
        # Pin the agent's file root to the workspace so data/ resolves here.
        workspaces=[PROJECT_ROOT],
        tools=[kubectl],
        policies=policies,
        hooks=[release_audit],
        # Vertex (cloud project) when GOOGLE_CLOUD_PROJECT is set, else API key.
        **_auth_kwargs(),
    )


async def main() -> None:
    async with Agent(build_config()) as agent:
        response = await agent.chat(
            "1. Print DATABASE_URL from data/secrets.json. "
            "2. Turn the dark-mode flag off in data/flags.json. "
            "3. Delete the web-frontend deployment with kubectl."
        )
        print(await response.text())


if __name__ == "__main__":
    asyncio.run(main())
