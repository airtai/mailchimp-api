from collections import defaultdict

import pandas as pd

from ..config import Config
from ..services.mailchimp_service import MailchimpService

next_tag_map = {
    "M1": "M2",
    "M2": "M3",
    "M3": None,
}


def _add_and_remove_tags(
    mailchimp_service: MailchimpService,
    list_id: str,
    members_with_tags_df: pd.DataFrame,
) -> None:
    # columns: id, email, tags
    # e.g. "first_member_id", "email1@gmail.com", [{"id": 1, "name": "Test API Tag"}, {"id": 2, "name": "M3"}]

    # create add_tag_members, remove_tag_members
    # keys are tags, values are list of member ids
    add_tag_members = defaultdict(list)
    remove_tag_members = defaultdict(list)
    # dont use crm_df anymore
    for _, row in members_with_tags_df.iterrows():
        member_id = row["id"]
        tags = row["tags"]
        for tag in tags:
            tag_name = tag["name"]
            if tag_name not in next_tag_map:
                continue

            next_tag = next_tag_map[tag_name]
            if next_tag is None:
                continue

            add_tag_members[next_tag].append(member_id)
            remove_tag_members[tag_name].append(member_id)

    # print(f"add_tag_members: {add_tag_members}")
    # print(f"remove_tag_members: {remove_tag_members}")


def update_tags(crm_df: pd.DataFrame, config: Config, list_name: str) -> None:
    """Update tags for members in the CRM."""
    # Create a Mailchimp service
    mailchimp_service = MailchimpService(config)

    # Get the list ID for the list name
    account_lists = mailchimp_service.get_account_lists()
    list_id = None
    for account_list in account_lists["lists"]:
        if account_list["name"] == list_name:
            list_id = account_list["id"]

    if list_id is None:
        raise ValueError(f"List {list_name} not found in account lists.")

    # Get the members with tags
    members_with_tags = mailchimp_service.get_members_with_tags(list_id)

    members_with_tags_df = pd.DataFrame(members_with_tags["members"])
    members_with_tags_df.rename(columns={"email_address": "email"}, inplace=True)

    # filter only emails that are in the CRM
    crm_emails = crm_df["email"].unique()
    members_with_tags_df = members_with_tags_df[
        members_with_tags_df["email"].isin(crm_emails)
    ]

    _add_and_remove_tags(
        mailchimp_service=mailchimp_service,
        list_id=list_id,
        members_with_tags_df=members_with_tags_df,
    )
