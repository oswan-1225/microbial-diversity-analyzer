import pytest
from visualize import p_value_to_asterisks
from stats_tests import compare_groups, compare_multiple_groups
import pandas as pd

# Basic Tests for p_value_to_asterisks function

def test_low_p_value():
    # Test with a low p-value
    p_value = 0.0001
    assert p_value_to_asterisks(p_value) == '***'

def test_high_p_value():
    # Test with a high p-value
    p_value = 0.6
    assert p_value_to_asterisks(p_value) == 'ns'

def test_middle_p_value():
    # Test with a middle p-value
    p_value = 0.03
    assert p_value_to_asterisks(p_value) == '*'

def test_middle_low_p_value():
    # Test with a middle-low p-value
    p_value = 0.005
    assert p_value_to_asterisks(p_value) == '**'

def test_p_value_boundary():
    # Test with a p-value exactly at the boundary
    p_value = 0.05
    assert p_value_to_asterisks(p_value) == 'ns'

# Basic Tests for compare_groups function

def test_compare_groups_raises_on_wrong_group_count():
    df = pd.DataFrame({
        "group": ["a", "a", "b", "b", "c", "c"],
        "shannon_diversity": [1.0, 1.1, 2.0, 2.1, 3.0, 3.1]
    })
    with pytest.raises(ValueError):
        compare_groups(df, metric="shannon_diversity")

def test_compare_groups_detects_clear_difference():
    df = pd.DataFrame({
        "group": ["control"]*5 + ["treated"]*5,
        "shannon_diversity": [1.0, 1.1, 1.2, 1.05, 1.15,      # control 
                              5.0, 5.1, 5.2, 5.05, 5.15]        # treated 
    })
    result = compare_groups(df, metric="shannon_diversity")
    assert result["p_value"] < 0.05

def test_compare_groups_no_difference():
    df = pd.DataFrame({
        "group": ["control"]*5 + ["treated"]*5,
        "shannon_diversity": [2.0, 2.1, 2.2, 2.05, 2.15,
                              2.0, 2.1, 2.2, 2.05, 2.15]  # identical values
    })
    result = compare_groups(df, metric="shannon_diversity")
    assert result["p_value"] > 0.05

# Basic tests for compare_multiple_groups function

def test_compare_multiple_groups_returns_all_treatments():
    df = pd.DataFrame({
        "group": ["control"]*5 + ["drug_a"]*5 + ["drug_b"]*5,
        "shannon_diversity": [2.0]*5 + [1.0]*5 + [3.0]*5
    })
    result = compare_multiple_groups(df, metric="shannon_diversity", control_label="control")
    
    assert set(result["treatment"]) == {"drug_a", "drug_b"}
    assert "control" not in result["treatment"].values

def test_compare_multiple_groups_bonferroni_correction():
    df = pd.DataFrame({
        "group": ["control"]*5 + ["drug_a"]*5 + ["drug_b"]*5 + ["drug_c"]*5,
        "shannon_diversity": [2.0, 2.1, 2.2, 2.05, 2.15,
                              1.0, 1.1, 1.2, 1.05, 1.15,
                              3.0, 3.1, 3.2, 3.05, 3.15,
                              2.0, 2.2, 2.1, 2.15, 2.05]  # drug_c basically the control
    })
    result = compare_multiple_groups(df, metric="shannon_diversity", control_label="control")
    
    n_comparisons = 3  # drug_a, drug_b, drug_c
    for _, row in result.iterrows():
        expected = min(row["p_value"] * n_comparisons, 1.0)
        assert row["corrected_p_value"] == pytest.approx(expected)