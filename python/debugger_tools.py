import logging
import socket


def connect_debugger(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.2)  # 2 Second Timeout
    debugger_port_open = sock.connect_ex(("localhost", 2345))
    if debugger_port_open:
        try:
            logging.warning("ACCESSING DEBUGGING PORT 2345")
            import pydevd_pycharm

            pydevd_pycharm.settrace(
                "host.docker.internal",
                port=port,
                stdoutToServer=True,
                stderrToServer=True,
            )
        except:
            logging.warning("could not connect to debugger")
