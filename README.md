# ulauncher-google-cloud-console

This is a [Ulauncher](https://ulauncher.io/) extension to open [Google Cloud Console](https://console.cloud.google.com) to a specific area and project.

![Filtered by project and area](screenshots/areas-filtered-project.png "Filtered by project and area")

![Preferences](screenshots/preferences.png "Preferences")

## Usage

Usage is as simple as typing the configured keyword (default is `gcloud`)
followed by space or enter. This will present you with the top list of areas.
Choosing any result will take you to it in your default web browser. As you
type additional letters after the keyword, the list of results will be filtered
to those that contain what you've typed.

### Projects

Project support is what differentiates this extension from the others described
below. By entering a comma-separated list of projects in the extension's
preferences, you web browser can be opened to the desired area within your
choice of project.

For example, let's say you have added `xyz-dev,xyz-prod1,xyz-prod2` into the
projects preference. When you type `gcloud prod logs` you will be presented
with the following two options.

- Logs for xyz-prod1
- Logs for xyz-prod2

## Supported Services

The list of supported Google Cloud services and areas within those services is
maintained within this project, and will probably never be complete. It's easy
to add new services and areas by adding to the `AREAS` dictionary in `main.py`,
and I encourage pull requests that do so.

Currently the supported services and areas are the following.

- Artifact Registry Repositories
- Bigtable Instances
- Billing
- Compute Instances
- Dataflow Jobs
- Datastore Databases
- DNS Zones
- Firestore Databases
- IAM
- IAM Service Accounts
- Kubernetes Clusters
- Load Balancers
- Logs
- Metrics Explorer
- Pub/Sub Subscriptions
- Pub/Sub Topics
- Pub/Sub Lite Reservations
- Pub/Sub Lite Subscriptions
- Pub/Sub Lite Topics
- SQL Instances
- Storage Buckets

## Similar Projects

As of now (2025-01-25) there are two other extensions that do a similar thing
to this one.

- [Google Cloud Extension](https://ext.ulauncher.io/-/github-dhollinger-ulauncher-gcp)
- [GCP Launcher](https://ext.ulauncher.io/-/github-zeue-ulauncher-gcp)

As far as I can tell, their features are the same. However, the GitHub
repository associated with _GCP Launcher_ is no longer available.

The reason I created yet another plugin for opening Google Cloud Console is
because in my daily work I work with many different Google Cloud services, and
in many different Google Cloud projects. The aforementioned extensions don't
offer a way to open a page for the correct project, and that's always what I
want to do.
