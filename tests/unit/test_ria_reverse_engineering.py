from atlas.innovation.ria_reverse import RIAReverseEngineering, default_reverse_engineering_candidates


def test_default_ria_candidates_are_routable():
    engine = RIAReverseEngineering()
    results = [engine.evaluate(c) for c in default_reverse_engineering_candidates()]
    assert results
    assert all(result.required_reviews for result in results)


def test_semantic_codec_goes_to_creation_and_math():
    engine = RIAReverseEngineering()
    candidate = next(c for c in default_reverse_engineering_candidates() if c.candidate_id == "semantic-image-codec")
    result = engine.evaluate(candidate)
    ministries = {x.ministry_id for x in result.ministry_assessments}
    assert "math_coherence" in ministries
    assert "creation_design" in ministries


def test_health_related_candidates_require_review():
    engine = RIAReverseEngineering()
    candidate = next(c for c in default_reverse_engineering_candidates() if c.candidate_id == "tesla-resonance-coupling")
    result = engine.evaluate(candidate)
    assert "health_wellbeing" in result.required_reviews
