# Animal Detection Flask App

## Overview

This Python Flask application uses the Google Cloud Vision API for animal detection in photos. It allows users to upload an image, detects animals in the photo using the Vision API, and displays the detected animals on the web page.

## Features

- **Animal Detection:** Utilizes the Google Cloud Vision API to detect animals in uploaded images.
- **Web Interface:** Provides a simple web interface for users to upload photos and view the results.

## Prerequisites

- Google Cloud Platform (GCP) Account
- Google Cloud Storage Bucket
- Google Cloud Vision API enabled
- Python 3.x and pip installed

## Setup

1. Clone the repository:

    cd <cloud-Ramamoorthy-shraya/final>


2. Install dependencies:

    pip install -r requirements.txt
3. 
    gcloud services enable vision.googleapis.com
    gcloud services enable storage-component.googleapis.com
    gcloud services enable datastore.googleapis.com

4.  gcloud iam service-accounts create finalproject
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member serviceAccount:finalproject@${PROJECT_ID}.iam.gserviceaccount.com \
    --role roles/owner

5.  gcloud iam service-accounts keys create ~/key.json --iam-account \
    finalproject@${PROJECT_ID}.iam.gserviceaccount.com

    export GOOGLE_APPLICATION_CREDENTIALS="/home/shraya/key.json"

6.  gsutil mb gs://finalprojshraya
    export CLOUD_STORAGE_BUCKET=finalprojshraya

7.  gcloud builds submit --timeout=900 --tag gcr.io/disco-station-400818/finalproj

8.  gcloud run deploy finalproject \
    --image gcr.io/disco-station-400818/finalproj \
    --service-account finalproject@disco-station-400818.iam.gserviceaccount.com \
    --set-env-vars CLOUD_STORAGE_BUCKET=finalprojshraya





