import pytest

from diversity_analyzer import species_richness
from diversity_analyzer import shannon_diversity

def test_species_richness_default_threshold_counts_any_nonzero():
    # default threshold=0.0 preserves original behavior
    sample_counts = [1e-11, 0, 5, 0, 2]
    assert species_richness(sample_counts) == 3

def test_species_richness_with_noise_threshold():
    # tiny values below threshold should NOT count as present
    sample_counts = [1e-11, 0, 5, 0, 2]
    assert species_richness(sample_counts, threshold=0.0001) == 2

def test_species_richness_threshold_boundary():
    # value exactly at threshold should NOT count (strict inequality)
    sample_counts = [0.0001, 5, 2]
    assert species_richness(sample_counts, threshold=0.0001) == 2

def test_shannon_diversity():
    # Test with a sample that has some taxa present
    sample_counts = [0, 5, 3, 0, 2]
    diversity = shannon_diversity(sample_counts)
    assert isinstance(diversity, float)
    assert diversity > 0

    # Test with a sample that has all taxa absent
    sample_counts = [0, 0, 0, 0]
    assert shannon_diversity(sample_counts) == 0.0

    # Test with a sample that has all taxa present equally
    sample_counts = [1, 1, 1, 1]
    diversity = shannon_diversity(sample_counts)
    assert isinstance(diversity, float)
    assert diversity > 0

    # Tests with a single taxon present
    sample_counts = [10, 0, 0, 0]
    assert shannon_diversity(sample_counts) == pytest.approx(0.0)