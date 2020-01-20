from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam
)


class VpcPeeringStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        workspaces_vpc = props['workspaces_vpc']
        analytics_vpc = props['analytics_vpc']
        sap_vpc = props['sap_vpc']

        # WorkSpaces用VPCから分析用VPCへのピアリング
        workspaces_to_analytics_vpc_peering = ec2.CfnVPCPeeringConnection(
            self, 'WorkSpacesToAnalyticsVPCPeering',
            vpc_id=workspaces_vpc.vpc_id,
            peer_vpc_id=analytics_vpc.vpc_id,
            tags=[core.CfnTag(key='Name', value='{}/WorkSpacesToAnalyticsVPCPeering'.format(self.stack_name))]
        )

        # WorkSpaces用VPCからSAP用VCPへのピアリング
        workspaces_to_sap_vpc_peering = ec2.CfnVPCPeeringConnection(
            self, 'WorkSpacesToSapVPCPeering',
            vpc_id=workspaces_vpc.vpc_id,
            peer_vpc_id=sap_vpc.vpc_id,
            tags=[core.CfnTag(key='Name', value='{}/WorkSpacesToSapVPCPeering'.format(self.stack_name))]
        )

        # WorkSpaces用VPCのIsolated Subnetから分析用VPCとSAP用VPCへのルート
        for subnet in workspaces_vpc.select_subnets(subnet_type=ec2.SubnetType.ISOLATED).subnets:
            analytics_route = ec2.CfnRoute(
                self, 'AnalyticsPeerRoute{}'.format(subnet.to_string()),
                route_table_id=subnet.route_table.route_table_id,
                destination_cidr_block=analytics_vpc.vpc_cidr_block,
                vpc_peering_connection_id=workspaces_to_analytics_vpc_peering.ref
            )
            sap_route = ec2.CfnRoute(
                self, 'SapPeerRoute{}'.format(subnet.to_string()),
                route_table_id=subnet.route_table.route_table_id,
                destination_cidr_block=sap_vpc.vpc_cidr_block,
                vpc_peering_connection_id=workspaces_to_sap_vpc_peering.ref
            )

        # 分析用VPCのIsolated SubnetからWorkSpaces用VPCへのルート
        for subnet in analytics_vpc.select_subnets(subnet_type=ec2.SubnetType.ISOLATED).subnets:
            route = ec2.CfnRoute(
                self, 'PeerRoute{}'.format(subnet.to_string()),
                route_table_id=subnet.route_table.route_table_id,
                destination_cidr_block=workspaces_vpc.vpc_cidr_block,
                vpc_peering_connection_id=workspaces_to_analytics_vpc_peering.ref
            )

        # SAP用VPCのPrivate SubnetからWorkSpaces用VPCへのルート
        for subnet in sap_vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnets:
            route = ec2.CfnRoute(
                self, 'PeerRoute{}'.format(subnet.to_string()),
                route_table_id=subnet.route_table.route_table_id,
                destination_cidr_block=workspaces_vpc.vpc_cidr_block,
                vpc_peering_connection_id=workspaces_to_sap_vpc_peering.ref
            )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
