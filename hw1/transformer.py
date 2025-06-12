from .db import DBSession


def link_campaigns_to_ad_events(db: DBSession):
    pass

def transform():
    with DBSession() as db:
        link_campaigns_to_ad_events(db)