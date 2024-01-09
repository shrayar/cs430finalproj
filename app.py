# Import necessary libraries
from datetime import datetime
import logging
import os

from flask import Flask, redirect, render_template, request

from google.cloud import datastore
from google.cloud import storage
from google.cloud import vision

# Define your Cloud Storage bucket environment variable
CLOUD_STORAGE_BUCKET = os.environ.get("CLOUD_STORAGE_BUCKET")

# Initialize Flask app
app = Flask(__name__)

# Route for deleting existing entities
@app.route("/delete_entities", methods=["GET"])
def delete_entities():
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Fetch existing entities of the specified kind (e.g., "Animals").
    query = datastore_client.query(kind="Animals")
    existing_entities = list(query.fetch())

    # Delete existing entities before adding new ones.
    with datastore_client.transaction():
        for existing_entity in existing_entities:
            datastore_client.delete(existing_entity.key)

    # Log the deleted entities
    deleted_entity_keys = [existing_entity.key for existing_entity in existing_entities]
    logging.info(f"Deleted entities: {deleted_entity_keys}")

    return "Entities deleted successfully!"

# Homepage route
@app.route("/")
def homepage():
    datastore_client = datastore.Client()

    # Fetch information from Datastore about each photo.
    query = datastore_client.query(kind="Animals")  # Adjust kind to match your Datastore entity for animals.
    image_entities = list(query.fetch())

    # Return HTML template and pass in image_entities as a parameter.
    return render_template("homepage.html", image_entities=image_entities)

# Route for uploading photos and detecting animals
@app.route("/upload_photo", methods=["GET", "POST"])
def upload_photo():
    photo = request.files["file"]

    # Create a Cloud Storage client.
    storage_client = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(photo.filename)
    blob.upload_from_string(photo.read(), content_type=photo.content_type)

    # Make the blob publicly viewable.
    blob.make_public()

    # Create a Cloud Vision client.
    vision_client = vision.ImageAnnotatorClient()

    # Use the Cloud Vision client to detect objects in the image.
    source_uri = "gs://{}/{}".format(CLOUD_STORAGE_BUCKET, blob.name)
    image = vision.Image(source=vision.ImageSource(gcs_image_uri=source_uri))
    objects = vision_client.object_localization(image=image).localized_object_annotations

    # If objects are detected, save information about the detected animals to Datastore.
    if len(objects) > 0:
        detected_animals = [obj.name.lower() for obj in objects]
        # Extract other relevant information about the detected animals as needed.

        # Create a Cloud Datastore client.
        datastore_client = datastore.Client()

        # Fetch the current date/time.
        current_datetime = datetime.now()

        # The kind for the new entity.
        kind = "Animals"  # Adjust kind to match your Datastore entity for animals.

        # The name/ID for the new entity.
        name = blob.name

        # Create the Cloud Datastore key for the new entity.
        key = datastore_client.key(kind, name)

        # Construct the new entity using the key. Set dictionary values for entity keys.
        entity = datastore.Entity(key)
        entity["blob_name"] = blob.name
        entity["image_public_url"] = blob.public_url
        entity["timestamp"] = current_datetime
        entity["detected_animals"] = detected_animals

        # Save the new entity to Datastore.
        datastore_client.put(entity)

    # Redirect to the home page.
    return redirect("/")

# Error handling for server errors
@app.errorhandler(500)
def server_error(e):
    logging.exception("An error occurred during a request.")
    return (
        """
    An internal error occurred: <pre>{}</pre>
    See logs for a full stacktrace.
    """.format(
            e
        ),
        500,
    )

# Run the app
if __name__ == "__main__":
    # Trigger the deletion route before starting the app
    with app.app_context():
        delete_entities()

    # Run the app
    app.run(host="0.0.0.0", port=5000, debug=True)
