import csv

from pathlib import Path

from emv import SocialPost, calculate_post
from database import initialize_database, save_post


CPM = {
    "instagram": 10.0,
    "tiktok": 8.0,
    "x": 6.0,
}


CSV_FILE = Path("data/posts.csv")


def import_csv():

    initialize_database()

    if not CSV_FILE.exists():
        print(f"CSV file not found: {CSV_FILE}")
        return

    imported = 0
    skipped = 0

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            platform = row["platform"].lower().strip()

            if platform not in CPM:
                print(
                    f"Skipping unsupported platform: {platform}"
                )
                skipped += 1
                continue

            post = SocialPost(
                platform=platform,
                post_id=row["post_id"],

                impressions=int(
                    row["impressions"] or 0
                ),

                views=int(
                    row["views"] or 0
                ),

                likes=int(
                    row["likes"] or 0
                ),

                comments=int(
                    row["comments"] or 0
                ),

                shares=int(
                    row["shares"] or 0
                ),

                saves=int(
                    row["saves"] or 0
                ),
            )

            result = calculate_post(
                post=post,
                cpm=CPM[platform],
            )

            save_post(
                result=result,

                author=row.get("author"),

                post_url=row.get("post_url"),

                text=row.get("text"),
            )

            imported += 1

            print(
                f"Imported: "
                f"{platform} / "
                f"{post.post_id} / "
                f"EMV=${result.emv:,.2f}"
            )

    print()
    print("==============================")
    print("CSV IMPORT COMPLETE")
    print("==============================")
    print(f"Imported: {imported}")
    print(f"Skipped:  {skipped}")


if __name__ == "__main__":
    import_csv()
