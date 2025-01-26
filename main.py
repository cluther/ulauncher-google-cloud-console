# Copyright (c) 2025 Chet Luther <chet.luther@gmail.com>
#
# This code is licensed under the MIT License.
#
# See the LICENSE file for details.

import logging

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import (
    KeywordQueryEvent,
    PreferencesEvent,
    PreferencesUpdateEvent,
)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem


AREAS = {
    "artifact registry repositories": {
        "name": "Artifact Registry Repositories",
        "icon": "container_registry",
        "url": "https://console.cloud.google.com/artifacts",
    },
    "bigtable instances": {
        "name": "Bigtable Instances",
        "icon": "bigtable",
        "url": "https://console.cloud.google.com/bigtable/instances",
    },
    "billing": {
        "name": "Billing",
        "icon": "billing",
        "url": "https://console.cloud.google.com/billing",
    },
    "compute instances": {
        "name": "Compute Instances",
        "icon": "compute_engine",
        "url": "https://console.cloud.google.com/compute/instances",
    },
    "dataflow jobs": {
        "name": "Dataflow Jobs",
        "icon": "dataflow",
        "url": "https://console.cloud.google.com/dataflow/jobs",
    },
    "datastore databases": {
        "name": "Datastore Databases",
        "icon": "datastore",
        "url": "https://console.cloud.google.com/datastore/databases",
    },
    "dns zones": {
        "name": "DNS Zones",
        "icon": "cloud_dns",
        "url": "https://console.cloud.google.com/net-services/dns/zones",
    },
    "firestore databases": {
        "name": "Firestore Databases",
        "icon": "firestore",
        "url": "https://console.cloud.google.com/firestore/databases",
    },
    "iam": {
        "name": "IAM",
        "icon": "identity_and_access_management",
        "url": "https://console.cloud.google.com/iam-admin/iam",
    },
    "iam service accounts": {
        "name": "IAM Service Accounts",
        "icon": "identity_and_access_management",
        "url": "https://console.cloud.google.com/iam-admin/serviceaccounts",
    },
    "kubernetes clusters": {
        "name": "Kubernetes Clusters",
        "icon": "google_kubernetes_engine",
        "url": "https://console.cloud.google.com/kubernetes/list",
    },
    "load balancers": {
        "name": "Load Balancers",
        "icon": "cloud_load_balancing",
        "url": "https://console.cloud.google.com/net-services/loadbalancing/list/loadBalancers",
    },
    "logs": {
        "name": "Logs",
        "icon": "cloud_logging",
        "url": "https://console.cloud.google.com/logs/query",
    },
    "metrics explorer": {
        "name": "Metrics Explorer",
        "icon": "cloud_monitoring",
        "url": "https://console.cloud.google.com/monitoring/metrics-explorer",
    },
    "pubsub subscriptions": {
        "name": "Pub/Sub Subscriptions",
        "icon": "pubsub",
        "url": "https://console.cloud.google.com/cloudpubsub/subscription",
    },
    "pubsub topics": {
        "name": "Pub/Sub Topics",
        "icon": "pubsub",
        "url": "https://console.cloud.google.com/cloudpubsub/topic",
    },
    "pubsublite reservations": {
        "name": "Pub/Sub Lite Reservations",
        "icon": "pubsub",
        "url": "https://console.cloud.google.com/cloudpubsub/liteReservation",
    },
    "pubsublite subscriptions": {
        "name": "Pub/Sub Lite Subscriptions",
        "icon": "pubsub",
        "url": "https://console.cloud.google.com/cloudpubsub/liteSubscription",
    },
    "pubsublite topics": {
        "name": "Pub/Sub Lite Topics",
        "icon": "pubsub",
        "url": "https://console.cloud.google.com/cloudpubsub/liteTopic",
    },
    "sql instances": {
        "name": "SQL Instances",
        "icon": "cloud_sql",
        "url": "https://console.cloud.google.com/sql/instances",
    },
    "storage buckets": {
        "name": "Storage Buckets",
        "icon": "cloud_storage",
        "url": "https://console.cloud.google.com/storage/browser",
    },
}

logger = logging.getLogger(__name__)


class GCloudExtension(Extension):
    projects = None

    def __init__(self):
        super().__init__()
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def set_projects(self, line: str) -> None:
        self.projects = [
            x.strip()
            for x in (line or "").split(",")
            if x.strip()
        ]


class PreferencesEventListener(EventListener):
    def on_event(self, event: PreferencesEvent, extension: GCloudExtension) -> None:
        extension.set_projects(event.preferences.get("projects"))


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event: PreferencesUpdateEvent, extension: GCloudExtension) -> None:
        if event.id == "projects":
            extension.set_projects(event.new_value)


class KeywordQueryEventListener(EventListener):
    def on_event(self, event: KeywordQueryEvent, extension: GCloudExtension) -> RenderResultListAction:
        if extension.projects:
            return self.with_projects(event, extension.projects)

        return self.without_projects(event)

    def with_projects(self, event: KeywordQueryEvent, projects: list[str]) -> RenderResultListAction:
        """Called when the user has specified at least one project.

        The text supplied by the user will be split into two parts by the first
        space. Both parts will be considered as potentially matching either one
        of the projects, or one of the predefined areas. For example, typing
        either "gcloud myproject logs" or "gcloud logs myproject" will both
        match the logs area for the myproject project.

        """
        arg = event.get_argument()
        arg1 = None
        arg2 = None
        if arg:
            args = arg.split(" ", 1) if arg else []
            if len(args) == 1:
                arg1 = args[0]
            else:
                arg1, arg2 = args

        items = []
        for project in projects:
            for area_name, area in AREAS.items():
                if arg1 and arg1 not in project and arg1 not in area_name:
                    continue

                if arg2 and arg2 not in project and arg2 not in area_name:
                    continue

                url = f"{area['url']}?project={project}"

                items.append(
                    ExtensionResultItem(
                        icon=f"images/{area["icon"]}.png",
                        name=f"{area["name"]} for {project}",
                        description=url,
                        on_enter=OpenUrlAction(url)))

        return RenderResultListAction(items)

    def without_projects(self, event: KeywordQueryEvent) -> RenderResultListAction:
        """Called when the user has not specified any projects.

        The text supplied will simply be matched by area, and the opened URL
        will not be project-specific.
        """
        arg = event.get_argument()

        items = []
        for area_name, area in AREAS.items():
            if arg and arg not in area_name:
                continue

            url = area["url"]

            items.append(
                ExtensionResultItem(
                    icon=f"images/{area["icon"]}.png",
                    name=f"{area["name"]}",
                    description=url,
                    on_enter=OpenUrlAction(url)))

        return RenderResultListAction(items)


if __name__ == "__main__":
    GCloudExtension().run()

