import argparse
import os
import sys
import logging

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(cur_dir, "../../"))

from yhklibs import yhk_app
from yhklibs.web.prosanic import YHKHttpProtocol
from web.prosanic import prosanic
from web.core.api import init_header

cfg_path = os.path.join(cur_dir, "conf")


def start():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", help="执行环境", type=str, default="debug", choices=["debug", "demo", "prod"])
    parser.add_argument("--debug", help="debug", type=bool, default=True)
    parser.add_argument("--host", help="启动host", type=str, default="0.0.0.0")
    parser.add_argument("--port", help="启动port", type=int, default=8080)
    args = parser.parse_args()
    args.environment = os.environ.get("START_ENV", args.environment)

    logging.basicConfig(level=logging.DEBUG)

    yhk_app.start(cfg_path, env=args.environment)
    init_header()

    prosanic.run(host=args.host, port=args.port, debug=args.debug, protocol=YHKHttpProtocol)


if __name__ == "__main__":
    start()
