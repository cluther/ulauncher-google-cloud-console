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
    "artifact registry": {
        "name": "Artifact Registry",
        "description": "Repositories – Artifact Registry",
        "icon": "section-artifact-registry",
        "url": "artifacts",
    },
    "bigtable instances": {
        "name": "Bigtable",
        "description": "Instances – Bigtable",
        "icon": "section-bigtable",
        "url": "bigtable/instances",
    },
    "billing": {
        "name": "Billing",
        "description": "Billing",
        "icon": "section-billing",
        "url": "billing",
    },
    "compute overview": {
        "name": "Compute",
        "description": "Overview – Compute",
        "icon": "section-compute",
        "url": "compute/overview",
    },
    "compute instances": {
        "name": "VM instances",
        "description": "VM instances – Compute",
        "icon": "instance",
        "url": "compute/instances",
    },
    "dataflow jobs": {
        "name": "Jobs",
        "description": "Jobs – Dataflow",
        "icon": "section-dataflow",
        "url": "dataflow/jobs",
    },
    "datastore databases": {
        "name": "Datastore",
        "description": "Databases – Datastore",
        "icon": "section-datastore",
        "url": "datastore/databases",
    },
    "filestore instances": {
        "name": "Filestore",
        "description": "Instances – Filestore",
        "icon": "section-filestore",
        "url": "filestore/instances",
    },
    "firestore databases": {
        "name": "Firestore",
        "description": "Databases – Firestore",
        "icon": "section-firestore",
        "url": "firestore/databases",
    },
    "iam": {
        "name": "IAM",
        "description": "IAM – IAM & Admin",
        "icon": "section-iam-admin",
        "url": "iam-admin/iam",
    },
    "iam service accounts": {
        "name": "Service Accounts",
        "description": "Service accounts – IAM & Admin",
        "icon": "service-accounts",
        "url": "iam-admin/serviceaccounts",
    },
    "kubernetes clusters": {
        "name": "Clusters",
        "description": "Kubernetes clusters – Kubernetes Engine",
        "icon": "section-kubernetes",
        "url": "kubernetes/list/overview",
    },
    "monitoring overview": {
        "name": "Monitoring",
        "description": "Overview – Monitoring",
        "icon": "section-monitoring",
        "url": "monitoring",
    },
    "monitoring dashboards": {
        "name": "Dashboards",
        "description": "Dashboards – Monitoring",
        "icon": "dashboards",
        "url": "monitoring/dashboards",
    },
    "monitoring metrics explorer": {
        "name": "Metrics explorer",
        "description": "Metrics explorer – Monitoring",
        "icon": "metrics",
        "url": "monitoring/metrics-explorer",
    },
    "monitoring logs explorer": {
        "name": "Logs explorer",
        "description": "Logs explorer – Monitoring",
        "icon": "section-logs",
        "url": "logs/query",
    },
    "monitoring alerting": {
        "name": "Alerting",
        "description": "Alerting – Monitoring",
        "icon": "alert",
        "url": "logs/query",
    },
    "monitoring alerting incidents": {
        "name": "Incidents",
        "description": "Incidents – Monitoring",
        "icon": "alert",
        "url": "logs/query",
    },
    "network dns zones": {
        "name": "DNS Zones",
        "description": "DNS Zones – Network Services",
        "icon": "dns",
        "url": "net-services/dns/zones",
    },
    "network load balancing": {
        "name": "Load Balancing",
        "description": "Load Balancing – Network Services",
        "icon": "section-load-balancing",
        "url": "net-services/loadbalancing",
    },
    "pubsub": {
        "name": "Pub/Sub",
        "description": "Cloud Pub/Sub",
        "icon": "section-cloudpubsub",
        "url": "cloudpubsub",
    },
    "pubsub topics": {
        "name": "Topics",
        "description": "Topics – Pub/Sub",
        "icon": "topic",
        "url": "cloudpubsub/topic",
    },
    "pubsub subscriptions": {
        "name": "Subscriptions",
        "description": "Subscriptions – Pub/Sub",
        "icon": "activity",
        "url": "cloudpubsub/subscription",
    },
    "pubsub lite reservations": {
        "name": "Lite Reservations",
        "description": "Lite Reservations – Pub/Sub",
        "icon": "service-directory",
        "url": "cloudpubsub/liteReservation",
    },
    "pubsub lite topics": {
        "name": "Lite Topics",
        "description": "Lite Topics – Pub/Sub",
        "icon": "topic",
        "url": "cloudpubsub/liteTopic",
    },
    "pubsub lite subscriptions": {
        "name": "Lite Subscriptions",
        "description": "Lite Subscriptions – Pub/Sub",
        "icon": "activity",
        "url": "cloudpubsub/liteSubscription",
    },
    "sql instances": {
        "name": "Instances",
        "description": "Instances – SQL",
        "icon": "section-sql",
        "url": "sql/instances",
    },
    "storage overview": {
        "name": "Storage",
        "description": "Overview – Storage",
        "icon": "section-storage",
        "url": "storage",
    },
    "storage buckets": {
        "name": "Storage Buckets",
        "description": "Buckets – Storage",
        "icon": "bucket",
        "url": "storage/browser",
    },
}

BASE_URL = "https://console.cloud.google.com"

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

                url = f"{BASE_URL}/{area["url"]}?project={project}"

                items.append(
                    ExtensionResultItem(
                        icon=f"images/{area["icon"]}.png",
                        name=self.get_name(area, project),
                        description=self.get_description(area, project),
                        on_enter=OpenUrlAction(url)))

        return RenderResultListAction(items[:9])

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

            url = f"{BASE_URL}/{area["url"]}"

            items.append(
                ExtensionResultItem(
                    icon=f"images/{area["icon"]}.png",
                    name=self.get_name(area),
                    description=self.get_description(area),
                    on_enter=OpenUrlAction(url)))

        return RenderResultListAction(items[:9])

    def get_name(self, area: dict, project=None) -> str:
        if project:
            return f"{area["name"]} – {project}"
        return area["name"]

    def get_description(self, area: dict, project=None) -> str:
        description = area.get("description", area["name"])
        if project:
            return f"{description} – {project}"
        return description


if __name__ == "__main__":
    GCloudExtension().run()

