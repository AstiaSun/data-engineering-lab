from .loaders import CampaignsUploader, UserUploader, AdEventUploader
from .constants import DATASET_PATH


def main():
    CampaignsUploader().upload(DATASET_PATH / "campaigns.csv")
    UserUploader().upload(DATASET_PATH / "users.csv")
    AdEventUploader(batch_size=10_000).upload(source_path=DATASET_PATH / "ad_events.csv")


if __name__ == "__main__":
    main()
