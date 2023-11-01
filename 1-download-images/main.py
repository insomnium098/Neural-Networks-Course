import pandas as pd
from dotenv import load_dotenv
import datetime as dt
from google.cloud.storage import Client, transfer_manager

load_dotenv()

# function from google storage quickstart
def download_many_blobs_with_transfer_manager(
    bucket_name, blob_names, destination_directory="", workers=8
):
    """Download blobs in a list by name, concurrently in a process pool.

    The filename of each blob once downloaded is derived from the blob name and
    the `destination_directory `parameter. For complete control of the filename
    of each blob, use transfer_manager.download_many() instead.

    Directories will be created automatically as needed to accommodate blob
    names that include slashes.
    """

    storage_client = Client()
    bucket = storage_client.bucket(bucket_name)

    results = transfer_manager.download_many_to_path(
        bucket, blob_names, destination_directory=destination_directory, max_workers=workers
    )

    failed_downloads = []
    for name, result in zip(blob_names, results):
        # The results list is either `None` or an exception for each blob in
        # the input list, in order.

        if isinstance(result, Exception):
            print("Failed to download {} due to exception: {}".format(name, result))
            failed_downloads.append(name)
        else:
            print("Downloaded {} to {}.".format(name, destination_directory + name))

    return failed_downloads


if __name__ == '__main__':
    WD = "1-download-images/"
    IMAGES_INFO = WD+"file_list.csv"
    IMAGES_FOLDER = WD+"raw_images/"
    SAMPLE_SIZE = 1

    df = pd.read_csv(IMAGES_INFO)

    df = df.sample(n=SAMPLE_SIZE)
    df["bucket"] = df.apply(lambda row: str(row["GCS Location"]).split("/")[2], axis=1)
    df["blob_name"] = df.apply(lambda row: "/".join(str(row["GCS Location"]).split("/")[3:5]), axis=1)

    timestamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")

    df["download_status"] = "success"
    for bucket in df["bucket"].unique():
        blobs = df[df["bucket"] == bucket]["blob_name"].tolist()
        destination_directory = IMAGES_FOLDER + bucket

        # download blobs and get failed downloads
        failed_downloads = download_many_blobs_with_transfer_manager(bucket, blobs, destination_directory, workers=8)

        # tag downloads as ok or failed in df
        mask = (df["bucket"] == bucket) & (df["blob_name"].isin(failed_downloads))
        df.loc[mask, "download_status"] = "failure"

    # add a column to filepath in local storage
    df = df.assign(filepath=IMAGES_FOLDER+df["bucket"]+df["blob_name"])
    # keep only image info from success downloads
    df = df[df["download_status"] == "success"]
    n = len(df)
    # save info dataframe
    filepath = ".".join(IMAGES_INFO.split(".")[:-1])+"_success_n"+str(n)+"_"+timestamp+".csv"
    df.to_csv(filepath, index=False)
    print(f"Info dataframe saved to {filepath}")
