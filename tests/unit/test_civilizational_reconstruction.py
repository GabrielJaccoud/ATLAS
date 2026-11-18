from atlas.civilizations import CivilizationalPattern, CivilizationalReconstructionEngine


def test_saba_water_system_yields_resilience_capabilities():
    pattern = CivilizationalPattern(
        pattern_id="saba-marib",
        civilization="Saba",
        problem="Sustain agriculture in a semi-arid environment.",
        solution="Dam, sluices, canals and distributed maintenance obligations.",
        evidence_refs=("unesco:saba-marib",),
        domains=("water", "infrastructure", "governance"),
        maintenance_model="shared obligations tied to water access",
    )
    capabilities = CivilizationalReconstructionEngine().transferable_capabilities(pattern)
    assert "resilience_planning" in capabilities
    assert "distributed_maintenance_governance" in capabilities
