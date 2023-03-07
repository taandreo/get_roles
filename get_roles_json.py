from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.subscription import SubscriptionClient
import json
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", default=False)
    parser.add_argument("--role", default=False)
    parser.add_argument("-d", default=".")
    args = parser.parse_args()

    credential = DefaultAzureCredential()
    subs_id = list_subs_id(credential)
    for sub_id in subs_id:
        gen_json_sub(sub_id, credential, "CustomRole", args.d)

def list_subs_id(cred):
    sub_ids = []
    sub_client = SubscriptionClient(cred)
    sub_list = sub_client.subscriptions.list()
    for sub in sub_list:
        if sub.state == "Enabled":
            sub_ids.append(sub.id)
    return sub_ids

def write_file(data, dir):
    file_name = dir + "/" + data["Name"] + ".json"
    file = open(file_name, "w")
    json.dump(data, file, indent=2)
    file.close()

def gen_data(definition):
    data = {
        "Name": definition.role_name,
        "Description": definition.description,
        "IsCustom":  definition.role_type,
        "type": definition.type,
        "AssignableScope": definition.assignable_scopes,
        "Actions": definition.permissions[0].actions,
        "DataActions": definition.permissions[0].data_actions,
        "NotActions": definition.permissions[0].not_actions,
        "NotDataActions": definition.permissions[0].not_data_actions
    }
    return data
    

def gen_json_sub(subscription_id, cred, role_type, dir):
    auth_client = AuthorizationManagementClient(cred, subscription_id)
    definitions = auth_client.role_definitions.list(subscription_id)
    for definition in definitions:
        if definition.role_type == role_type:
            data = gen_data(definition)
            write_file(data, dir)

main()
