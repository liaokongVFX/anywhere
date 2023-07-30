import json
import os

CONFIG_ROOT = os.path.expanduser('~/Anywhere').replace('\\', '/')
CONFIG_PATH = '{}/{}'.format(CONFIG_ROOT, 'AnywhereConfig.json')
CHAT_HISTORY = '{}/{}'.format(CONFIG_ROOT, 'ChatHistory.json')


def save_config(config_type, _data, data_type='dict', is_set=False):
    data = get_config(data_type=data_type)
    if not is_set:
        if data_type == 'dict':
            data.setdefault(config_type, {}).update(_data)
        else:
            data.setdefault(config_type, []).append(_data)
    else:
        data[config_type] = _data

    if not os.path.exists(os.path.dirname(CONFIG_PATH)):
        os.makedirs(os.path.dirname(CONFIG_PATH))
    with open(CONFIG_PATH, 'w') as f:
        f.write(json.dumps(data, indent=2))


def get_config(config_type=None, data_type='dict'):
    default = {} if data_type == 'dict' else []
    if not os.path.exists(CONFIG_PATH):
        return default

    with open(CONFIG_PATH) as f:
        data = json.loads(f.read())
        if config_type:
            return data.get(config_type, default)
        return data


class ChatHistoryStorage(object):
    def __init__(self):
        self._storage = self._get_history()

    @staticmethod
    def _get_history():
        if not os.path.exists(CHAT_HISTORY):
            return {}

        with open(CHAT_HISTORY) as f:
            data = json.loads(f.read())
            return data

    def _save_history(self):
        if not os.path.exists(os.path.dirname(CHAT_HISTORY)):
            os.makedirs(os.path.dirname(CHAT_HISTORY))
        with open(CHAT_HISTORY, 'w') as f:
            f.write(json.dumps(self._storage, indent=2))

    def get_messages(self, chat_name):
        return self._storage.get(chat_name, {}).get('messages', [])

    def append_messages(self, chat_name, message):
        self._storage[chat_name].setdefault('messages', []).append(message)
        self._save_history()

    def get_common_config(self, chat_name):
        return self._storage.get(chat_name, {}).get('common', {})

    def set_common_config(self, chat_name, config):
        self._storage.setdefault(chat_name, {}).setdefault('common', {}).update(config)
        self._save_history()

    def change_common_config_name(self, old_name, chat_name, config=None):
        data = self._storage.pop(old_name)
        if config:
            data.get('common', {}).update(config)

        self._storage[chat_name] = data
        self._save_history()

    def get_history_names(self):
        return list(self._storage.keys())

    def get_histories(self):
        return self._storage

    def delete_history(self, chat_name):
        self._storage.pop(chat_name, None)
        self._save_history()


chat_history_storage = ChatHistoryStorage()
