from pathlib import Path
from urllib.parse import urlsplit, urlparse

DEFAULT_ENB_CONFIG_SRC = 'https://b.yadro.com/projects/TEL/repos/bts-oam-agent/raw/docker/sct/fs/opt/bts/oam/xml/config.xml?at='


obj = urlsplit(DEFAULT_ENB_CONFIG_SRC)

enb_config_name = Path(obj.path).name

print(obj)
print(enb_config_name)
