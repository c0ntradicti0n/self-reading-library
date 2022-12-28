import inspect
import json
import logging
import traceback
from logging import StreamHandler

from core.database import login, BASE
from helpers.hash_tools import hashval


class GraphHandler(StreamHandler):
    def __init__(self):
        StreamHandler.__init__(self)

        # Kafka Broker Configuration
        self.conn = login("ant_log")
        self.Log = self.conn.createURI(f"{BASE}log")
        self.Level = self.conn.createURI(f"{BASE}level")
        self.Msg = self.conn.createURI(f"{BASE}msg")
        self.Date = self.conn.createURI(f"{BASE}date")
        self.Msg = self.conn.createURI(f"{BASE}type")

    def emit(self, record):
        msg = self.format(record)
        frame = inspect.currentframe()
        stack_trace = traceback.format_stack(frame)
        logging.debug(stack_trace[:-1])
        hash = hashval(msg)
        msg = json.dumps(msg)
        msg = msg.replace("{", "")
        msg = msg.replace("}", "")
        msg = msg.replace("]", "")
        msg = msg.replace("[{]", "")
        msg = msg.replace("'{'", "")
        msg = msg.replace("'{'", "")
        msg = msg.replace('"', "")
        msg = msg.replace("'", "")
        msg = msg.replace("\\", "")

        try:
            q = f"""
              insert data {{{{
                 "{{threadName}}" {self.Log} "{hash}".
                 "{hash}" {self.Msg} "{msg}".
                 "{hash}" {self.Level} "{{levelname}}".
             }}}}
           """.format(
                **record.__dict__
            )
            self.conn.executeUpdate(q)
        except Exception as e:
            logging.error("Error with graph db logging", exc_info=True)
