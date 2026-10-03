from dataclasses import dataclass
from typing import Optional


@dataclass
class SocialPost:
    platform: str
    post_id: str

    impressions: int = 0
    views: int = 0

    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0


@dataclass
class PerformanceMetrics:
    impressions: int
    views: int

    likes: int
    comments: int
    shares: int
    saves: int

    engagements: int
    engagement_rate: float


@dataclass
class EMVResult:
    platform: str
    post_id: str

    cpm: float
    emv: float

    performance: PerformanceMetrics


def calculate_emv(impressions: int, cpm: float) -> float:
    """
    Calculate media-value-based EMV.

    EMV = (Impressions / 1,000) × CPM
    """

    if impressions <= 0:
        return 0.0

    return (impressions / 1000) * cpm


def calculate_performance(
    impressions: int,
    views: int,
    likes: int,
    comments: int,
    shares: int,
    saves: int,
) -> PerformanceMetrics:

    engagements = (
        likes
        + comments
        + shares
        + saves
    )

    if impressions > 0:
        engagement_rate = engagements / impressions
    elif views > 0:
        engagement_rate = engagements / views
    else:
        engagement_rate = 0.0

    return PerformanceMetrics(
        impressions=impressions,
        views=views,
        likes=likes,
        comments=comments,
        shares=shares,
        saves=saves,
        engagements=engagements,
        engagement_rate=engagement_rate,
    )


def calculate_post(
    post: SocialPost,
    cpm: float,
) -> EMVResult:

    emv = calculate_emv(
        impressions=post.impressions,
        cpm=cpm,
    )

    performance = calculate_performance(
        impressions=post.impressions,
        views=post.views,
        likes=post.likes,
        comments=post.comments,
        shares=post.shares,
        saves=post.saves,
    )

    return EMVResult(
        platform=post.platform,
        post_id=post.post_id,
        cpm=cpm,
        emv=emv,
        performance=performance,
    )
