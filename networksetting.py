import boto3
import pandas as pd
import os

client = boto3.client("ec2")


class NetworkSetting:
    def get_securitygroup(self):
        nexttoken = ""
        result = []
        while True:
            if nexttoken == "":
                sg = client.describe_security_groups()
            else:
                sg = client.describe_security_groups(NextToken=nexttoken)
            if not len(sg["SecurityGroups"]) == 0:
                result.extend(sg["SecurityGroups"])
            if "NextToken" in sg:
                nexttoken = sg["NextToken"]
            else:
                break
        df = pd.json_normalize(result)
        df.to_csv(
            "./csv/security_group.csv",
            index=False,
            # columns=[
            #     "GroupName",
            #     "GroupId",
            #     "VpcId",
            #     "Description",
            #     "IpPermissions",
            #     "IpPermissionsEgress",
            #     "Tags",
            #     "OwnerId",
            # ],
        )

    def get_securitygrouprules(self):
        nexttoken = ""
        result = []
        while True:
            if nexttoken == "":
                sgrules = client.describe_security_group_rules()
            else:
                sgrules = client.describe_security_group_rules(NextToken=nexttoken)
            if not len(sgrules["SecurityGroupRules"]) == 0:
                result.extend(sgrules["SecurityGroupRules"])
            if "NextToken" in sgrules:
                nexttoken = sgrules["NextToken"]
            else:
                break
        df = pd.json_normalize(result)
        df.to_csv(
            "./csv/security_group_rules.csv",
            index=False,
            # columns=[
            #     "SecurityGroupRuleId",
            #     "GroupId",
            #     "GroupOwnerId",
            #     "IsEgress",
            #     "IpProtocol",
            #     "FromPort",
            #     "ToPort",
            #     "Tags",
            #     "ReferencedGroupInfo.GroupId",
            #     "ReferencedGroupInfo.UserId",
            #     "CidrIpv4",
            #     "CidrIpv6",
            #     "PrefixListId",
            #     "Description",
            # ],
        )

    def get_managedprefixlists(self):
        result = self.__get_managedprefixlists()
        df = pd.json_normalize(result)
        df.to_csv(
            "./csv/managed_prefix_lists.csv",
            index=False,
            # columns=[
            #     "PrefixListId",
            #     "PrefixListName",
            #     "MaxEntries",
            #     "AddressFamily",
            #     "State",
            #     "Version",
            #     "PrefixListArn",
            #     "Tags",
            #     "OwnerId",
            # ],
        )

    def __get_managedprefixlists(self):
        nexttoken = ""
        result = []
        while True:
            if nexttoken == "":
                prefix = client.describe_managed_prefix_lists()
            else:
                prefix = client.describe_managed_prefix_lists(NextToken=nexttoken)
            if not len(prefix["PrefixLists"]) == 0:
                result.extend(prefix["PrefixLists"])
            if "NextToken" in prefix:
                nexttoken = prefix["NextToken"]
            else:
                break
        return result

    def get_managed_prefix_list_entries(self):
        prefixlist = self.__get_managedprefixlists()
        result = []
        for prefix in prefixlist:
            nexttoken = ""
            while True:
                if nexttoken == "":
                    ls = client.get_managed_prefix_list_entries(PrefixListId=prefix["PrefixListId"])
                else:
                    ls = client.get_managed_prefix_list_entries(PrefixListId=prefix["PrefixListId"], NextToken=nexttoken)
                if not len(ls["Entries"]) == 0:
                    for cidr in ls["Entries"]:
                        cidr["PrefixListId"] = prefix["PrefixListId"]  # type: ignore
                        result.append(cidr)
                if "NextToken" in ls:
                    nexttoken = ls["NextToken"]
                else:
                    break

        df = pd.json_normalize(result)
        df.to_csv(
            "./csv/managed_prefix_entries.csv",
            index=False,
            # columns=[
            #     "PrefixListId",
            #     "Cidr",
            #     "Description",
            # ],
        )

    def get_routetables(self):
        nexttoken = ""
        result = []
        while True:
            if nexttoken == "":
                routetables = client.describe_route_tables()
            else:
                routetables = client.describe_route_tables(NextToken=nexttoken)
            if not len(routetables["RouteTables"]) == 0:
                result.extend(routetables["RouteTables"])
            if "NextToken" in routetables:
                nexttoken = routetables["NextToken"]
            else:
                break
        # route tables
        df = pd.json_normalize(result)
        df.to_csv(
            "./csv/route_tables.csv",
            index=False,
            # columns=[
            #     "RouteTableId",
            #     "Tags",
            #     "VpcId",
            #     "Associations",
            #     "PropagatingVgws",
            #     "Routes",
            #     "OwnerId",
            # ],
        )

        routescsv = []
        associationscsv = []
        propagatingvgwscsv = []
        for routetable in result:
            id = routetable["RouteTableId"]

            routes = routetable["Routes"]
            for route in routes:
                route["RouteTableId"] = id
                routescsv.append(route)

            associations = routetable["Associations"]
            for association in associations:
                association["RouteTableId"] = id
                associationscsv.append(association)

            propagatingvgws = routetable["PropagatingVgws"]
            for propagatingvgw in propagatingvgws:
                propagatingvgw["RouteTableId"] = id
                propagatingvgwscsv.append(propagatingvgw)

        df = pd.json_normalize(routescsv)
        df.to_csv(
            "./csv/route_tables_routes.csv",
            index=False,
        )

        df = pd.json_normalize(associationscsv)
        df.to_csv(
            "./csv/route_tables_associations.csv",
            index=False,
        )

        df = pd.json_normalize(propagatingvgwscsv)
        df.to_csv(
            "./csv/route_tables_propagatingvgws.csv",
            index=False,
        )


if __name__ == "__main__":
    os.makedirs("./csv/", exist_ok=True)
    ns = NetworkSetting()
    ns.get_securitygroup()
    ns.get_securitygrouprules()
    ns.get_managedprefixlists()
    ns.get_managed_prefix_list_entries()
    ns.get_routetables()
