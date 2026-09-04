import pytest

from backend.agent_core.tools.profile_tools import (
    FORGET_USER_FACT_CONTRACT,
    REMEMBER_USER_FACT_CONTRACT,
    make_profile_tools,
)
from backend.memory.profile import Profile
from backend.memory.profile_errors import ProfileFactNotFoundError


def _tools(profile: Profile):
    pairs = make_profile_tools(profile)
    return {contract.name: fn for contract, fn in pairs}


def test_make_profile_tools_returns_both_contracts_bound_to_the_profile():
    profile = Profile.new()

    tools = _tools(profile)

    assert set(tools.keys()) == {"remember_user_fact", "forget_user_fact"}


def test_remember_user_fact_closure_mutates_the_bound_profile():
    profile = Profile.new()
    tools = _tools(profile)

    result = tools["remember_user_fact"](fact="Likes cats.", category="preference")

    assert result == {"id": "fact_0001", "status": "active"}
    assert profile.active_facts()[0].text == "Likes cats."
    assert profile.dirty is True


def test_remember_user_fact_closure_supports_supersedes():
    profile = Profile.new()
    tools = _tools(profile)
    first = tools["remember_user_fact"](fact="Lives in Bandung.", category="location")

    result = tools["remember_user_fact"](
        fact="Lives in Jakarta.", category="location", supersedes=first["id"]
    )

    assert result["status"] == "active"
    ids_by_status = {f.id: f.status for f in profile.facts}
    assert ids_by_status[first["id"]] == "superseded"


def test_forget_user_fact_closure_marks_deleted():
    profile = Profile.new()
    tools = _tools(profile)
    fact = tools["remember_user_fact"](fact="Allergic to peanuts.", category="health")

    result = tools["forget_user_fact"](fact_id=fact["id"])

    assert result == {"id": fact["id"], "status": "deleted"}
    assert profile.active_facts() == []


def test_forget_user_fact_closure_raises_uncaught_for_unknown_id():
    profile = Profile.new()
    tools = _tools(profile)

    # Not wrapped in try/except here — backend/agent_core/loop.py's
    # _execute_tool_call is what's responsible for catching this and
    # turning it into a verbal tool_result observation, not the closure.
    with pytest.raises(ProfileFactNotFoundError):
        tools["forget_user_fact"](fact_id="fact_9999")


def test_contracts_declare_standard_permission_tier():
    assert REMEMBER_USER_FACT_CONTRACT.permission_tier.value == "standard"
    assert FORGET_USER_FACT_CONTRACT.permission_tier.value == "standard"
