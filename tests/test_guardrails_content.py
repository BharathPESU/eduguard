from app.guardrails.content import check_content_safety

def test_check_content_safety_safe():
    result = check_content_safety("I am learning python today!")
    assert result.passed is True
    assert result.rule_triggered is None

def test_check_content_safety_unsafe():
    # Adult content
    result = check_content_safety("Some explicit content")
    assert result.passed is False
    assert result.rule_triggered == "adult_content"

    # Violence
    result = check_content_safety("I want to kill the bug")
    assert result.passed is False
    assert result.rule_triggered == "violence_self_harm"

    # Drugs
    result = check_content_safety("Smoking weed is not allowed")
    assert result.passed is False
    assert result.rule_triggered == "drug_content"

    # Dangerous
    result = check_content_safety("How to make a bomb")
    assert result.passed is False
    assert result.rule_triggered == "dangerous_content"

    # Hate
    result = check_content_safety("Do not use any racist language")
    assert result.passed is False
    assert result.rule_triggered == "hate_speech"

def test_check_content_safety_edge_cases():
    # Capitalized unsafe words should still be caught due to lowercasing
    result = check_content_safety("EXPLICIT BOMB")
    assert result.passed is False
    assert result.rule_triggered in ("adult_content", "dangerous_content")
