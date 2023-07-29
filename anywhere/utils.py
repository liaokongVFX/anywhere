import json
import os

CONFIG_ROOT = os.path.expanduser('~/Anywhere').replace('\\', '/')
CONFIG_PATH = '{}/{}'.format(CONFIG_ROOT, 'AnywhereConfig.json')
TALK_HISTORY = '{}/{}'.format(CONFIG_ROOT, 'TalkHistory.json')


def save_config(config_type, _data):
    data = get_config()
    data.setdefault(config_type, {}).update(_data)

    if not os.path.exists(os.path.dirname(CONFIG_PATH)):
        os.makedirs(os.path.dirname(CONFIG_PATH))
    with open(CONFIG_PATH, 'w') as f:
        f.write(json.dumps(data, indent=2))


def get_config(config_type=None):
    if not os.path.exists(CONFIG_PATH):
        return {}

    with open(CONFIG_PATH) as f:
        data = json.loads(f.read())
        if config_type:
            return data.get(config_type, {})
        return data


class TalkHistoryStorage(object):
    def __init__(self):
        pass
