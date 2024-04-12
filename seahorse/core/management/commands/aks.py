from seahorse.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_argument(self, parser):
        parser.add_argument(
            "--subscription",
            action="append",
            help="subscription is required to use AKS service",
        )
        parser.add_argument(
            "--public IP",
            action="append",
            default=[],
            help="AKS has public IP",
        )
        parser.add_argument(
            "--private IP",
            action="append",
            default=[],
            help="AKS has private network",
        )
    
    def handle(self, *app_labels, **options):
        rsm = options.get("ResourceManager", None)
        print("use resource manager deploying resources")