from backend.agent_core.llm_client import LLMResponse
from backend.memory.session import Session


def test_needs_compaction_below_threshold_is_false():
    session = Session.new("s1")
    session.last_input_tokens = 100

    assert session.needs_compaction(threshold_tokens=6000) is False


def test_needs_compaction_at_threshold_is_true():
    session = Session.new("s1")
    session.last_input_tokens = 6000

    assert session.needs_compaction(threshold_tokens=6000) is True


def test_needs_compaction_above_threshold_is_true():
    session = Session.new("s1")
    session.last_input_tokens = 9000

    assert session.needs_compaction(threshold_tokens=6000) is True


def test_needs_compaction_defaults_to_no_safety_margin():
    session = Session.new("s1")
    session.last_input_tokens = 5900

    assert session.needs_compaction(threshold_tokens=6000) is False


def test_needs_compaction_safety_margin_triggers_earlier():
    session = Session.new("s1")
    session.last_input_tokens = 5900  # below threshold on its own

    assert (
        session.needs_compaction(threshold_tokens=6000, safety_margin_tokens=200)
        is True  # 5900 + 200 >= 6000
    )


def test_needs_compaction_safety_margin_not_enough_is_still_false():
    session = Session.new("s1")
    session.last_input_tokens = 5000

    assert session.needs_compaction(threshold_tokens=6000, safety_margin_tokens=200) is False


def test_needs_compaction_with_no_usage_recorded_yet_is_false():
    session = Session.new("s1")

    assert session.needs_compaction(threshold_tokens=6000) is False


def test_record_usage_sets_token_fields():
    session = Session.new("s1")

    session.record_usage(LLMResponse(text="ok", input_tokens=123, output_tokens=45))

    assert session.last_input_tokens == 123
    assert session.last_output_tokens == 45


def test_append_user_message_appends_plain_string_turn():
    session = Session.new("s1")

    session.append_user_message("hello")

    assert session.messages == [{"role": "user", "content": "hello"}]


def test_to_llm_messages_without_summary_returns_messages_unchanged():
    session = Session.new("s1")
    session.messages = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "yo"}]

    assert session.to_llm_messages() == session.messages


def test_to_llm_messages_with_summary_places_it_first_then_ack_then_recent_verbatim():
    session = Session.new("s1")
    session.summary = "Earlier the user asked about the weather."
    session.messages = [{"role": "user", "content": "and now?"}, {"role": "assistant", "content": "sunny"}]

    result = session.to_llm_messages()

    assert result[0]["role"] == "user"
    assert "Earlier the user asked about the weather." in result[0]["content"]
    assert result[1]["role"] == "assistant"
    assert result[2:] == session.messages
