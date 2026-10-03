from src.emv import (
    calculate_emv,
    calculate_performance,
)


def test_emv():
    emv = calculate_emv(
        impressions=500_000,
        cpm=8.0,
    )

    assert emv == 4000.0


def test_engagement():
    result = calculate_performance(
        impressions=500_000,
        views=500_000,
        likes=25_000,
        comments=1_000,
        shares=2_000,
        saves=0,
    )

    assert result.engagements == 28_000
    assert result.engagement_rate == 0.056
