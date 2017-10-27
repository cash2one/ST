import os
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(cur_dir, "../../"))
cfg_path = os.path.join(cur_dir, "../conf")

from yhklibs.db.postgresql import ModelBase, model_base_bind_engine
from yhklibs import yhk_app

environment = os.environ.get("START_ENV", "debug")

yhk_app.start(cfg_path, env=environment)

# 引用其它模块的model
from web import models

model_base_bind_engine(ModelBase, "master")
ModelBase.metadata.create_all()
