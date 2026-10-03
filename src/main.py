from emv import SocialPost, calculate_post

from database import (
    initialize_database,
    save_post,
    get_total_emv,
    get_total_engagements,
)


CPM = {
    "instagram": 10.0,
    "tiktok": 8.0,
    "x": 6.0,
}


def main():

    # Create database
    initialize_database()

    # Example post
    post = SocialPost(
        platform="tiktok",
        post_id="example_001",

        impressions=500_000,
        views=500_000,

        likes=25_000,
        comments=1_000,
        shares=2_000,
        saves=0,
    )

    cpm = CPM[post.platform]

    result = calculate_post(
        post=post,
        cpm=cpm,
    )

    # Save to database
    save_post(
        result=result,
        author="example_user",
        post_url="https://example.com/post/001",
        text="Example TikTok post",
    )

    print()
    print("==============================")
    print("       SOCIAL EMV TRACKER")
    print("==============================")

    print()
    print("POST")
    print("------------------------------")
    print(f"Platform:        {result.platform}")
    print(f"Post ID:         {result.post_id}")

    print()
    print("PERFORMANCE")
    print("------------------------------")
    print(f"Views:           {result.performance.views:,}")
    print(f"Likes:           {result.performance.likes:,}")
    print(f"Comments:        {result.performance.comments:,}")
    print(f"Shares:          {result.performance.shares:,}")
    print(f"Saves:           {result.performance.saves:,}")
    print(f"Engagements:     {result.performance.engagements:,}")
    print(
        f"Engagement Rate: "
        f"{result.performance.engagement_rate:.2%}"
    )

    print()
    print("EMV")
    print("------------------------------")
    print(f"CPM:             ${result.cpm:.2f}")
    print(f"EMV:             ${result.emv:,.2f}")

    print()
    print("TOTAL DATABASE")
    print("------------------------------")
    print(f"Total EMV:       ${get_total_emv():,.2f}")
    print(f"Total Engagements: {get_total_engagements():,}")

    print()
    print("==============================")


if __name__ == "__main__":
    main()
