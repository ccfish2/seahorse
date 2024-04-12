
from seahorse.core.management.base import BaseCommand

class Command(BaseCommand):
    def add_arguments(self, parser):
        
        parser.add_argument(
            "--vpcid",
            action="append",
            help="VPC is required to provision EKS cluster",
        )
        parser.add_argument(
            "--CIDR",
            action="append",
            help="CIDR is required to provision EKS cluster",
        )
    
    def handle(self, *app_labels, **options):
        vpcid = options.get("vpcid", None)
        cidr = options.get("CIDR", None)
        print("EKS vpcid ", vpcid, " cidr ", cidr)