import logging


def connect_debugger(port):
    try:
        logging.warning("ACCESSING DEBUGGING PORT 2345")
        import pydevd_pycharm

        pydevd_pycharm.settrace(
            "host.docker.internal", port=port, stdoutToServer=True, stderrToServer=True
        )
    except:
        logging.warning("could not connect to debugger")
