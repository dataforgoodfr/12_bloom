import os
import time
import requests
from tqdm.auto import tqdm
from typing import Optional
from azure.storage.blob import BlobServiceClient

def download_and_cache_file(url: str, cache_dir: str = '.cache', verbose: Optional[bool] = True) -> str:
    # Create the cache directory if it doesn't exist
    os.makedirs(cache_dir, exist_ok=True)

    # Get the filename from the URL
    file_name = os.path.basename(url)

    # Check if the file is in the cache
    file_path = os.path.join(cache_dir, file_name)
    if os.path.exists(file_path):
        if verbose:
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB
            print(f"File {file_name} already exists in cache ({file_size:.2f} MB)")
    else:
        if verbose:
            print(f"Downloading file {file_name}...")

        session = requests.Session()
        response = session.get(url, stream=True, allow_redirects=True)
        total_size = int(response.headers.get('content-length', 0))
        total_chunks = (total_size + 1024*1024 - 1) // (1024*1024)  # Calculate total number of chunks

        with open(file_path, 'wb') as f:
            for chunk in tqdm(response.iter_content(chunk_size=1024*1024), total=total_chunks, unit='chunks'):
                f.write(chunk)

        if verbose:
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB
            print(f"Downloaded {file_name} ({file_size:.2f} MB)")

    return file_path




