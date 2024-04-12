from seahorse.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_argument(self, parser):
        parser.add_argument(
            "--hostproject",
            action="append",
            help="host project share subnet that other project could use",
        )
        parser.add_argument(
            "--internal_load_balancer",
            action="append",
            help="internal load balancer distribute data into GKE cluster",
        )
        parser.add_argument(
            "--external_load_balancer",
            action="append",
            help="external load balancer distribute data from outside of the cluster",
        )
    
    def handle(self, **options):
        projectID = options.get("projectID", None)
        print("GKE ", projectID, " ", options.get("internal_load_balancer", None),
              options.get("external_load_balancer", None))