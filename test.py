from config import *
from telethon import *
from asyncio import CancelledError
import logging
import threading
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Column, PickleType, UnicodeText, distinct, func
BASE = declarative_base()
SESSION = start()
engine = create_engine("sed.db")
BASE.metadata.bind = engine
BASE.metadata.create_all(engine)


class lucithon_GlobalCollection(BASE):
    __tablename__ = "lucithon_globalcollection"
    keywoard = Column(UnicodeText, primary_key=True)
    contents = Column(PickleType, primary_key=True, nullable=False)

    def __init__(self, keywoard, contents):
        self.keywoard = keywoard
        self.contents = tuple(contents)

    def __repr__(self):
        return "<lucithon Global Collection lists '%s' for %s>" % (
            self.contents,
            self.keywoard,
        )

    def __eq__(self, other):
        return bool(
            isinstance(other, lucithon_GlobalCollection)
            and self.keywoard == other.keywoard
            and self.contents == other.contents
        )


lucithon_GlobalCollection.__table__.create(checkfirst=True)

lucithon_GLOBALCOLLECTION = threading.RLock()


class COLLECTION_SQL:
    def __init__(self):
        self.CONTENTS_LIST = {}


COLLECTION_SQL_ = COLLECTION_SQL()


def add_to_collectionlist(keywoard, contents):
    with lucithon_GLOBALCOLLECTION:
        keyword_items = lucithon_GlobalCollection(keywoard, tuple(contents))

        SESSION.merge(keyword_items)
        SESSION.commit()
        COLLECTION_SQL_.CONTENTS_LIST.setdefault(
            keywoard, set()).add(tuple(contents))


def del_keyword_collectionlist(keywoard):
    with lucithon_GLOBALCOLLECTION:
        keyword_items = (
            SESSION.query(lucithon_GlobalCollection.keywoard)
            .filter(lucithon_GlobalCollection.keywoard == keywoard)
            .delete()
        )
        COLLECTION_SQL_.CONTENTS_LIST.pop(keywoard)
        SESSION.commit()


def get_collectionlist_items():
    try:
        chats = SESSION.query(
            lucithon_GlobalCollection.keywoard).distinct().all()
        return [i[0] for i in chats]
    finally:
        SESSION.close()


logging.basicConfig(
    format="[%(levelname)s- %(asctime)s]- %(name)s- %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)

LOGS = logging.getLogger(__name__)


@fifthon.on(events.NewMessage(outgoing=True, pattern=r"\.تحديث"))
async def _(event):

    sandy = await event.edit(
        event,
        "**JUST WAIT FOR 5 MINS AND JOIN HEHR @LUCITHON**",
    )
    try:
        ulist = get_collectionlist_items()
        for i in ulist:
            if i == "restart_update":
                del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
    try:
        add_to_collectionlist("restart_update", [sandy.chat_id, sandy.id])
    except Exception as e:
        LOGS.error(e)
    try:
        await fifthon.disconnect()
    except CancelledError:
        pass
    except Exception as e:
        LOGS.error(e)
