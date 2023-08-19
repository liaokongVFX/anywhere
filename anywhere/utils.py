import json
import os

CONFIG_ROOT = os.path.expanduser('~/Anywhere').replace('\\', '/')
CONFIG_PATH = '{}/{}'.format(CONFIG_ROOT, 'AnywhereConfig.json')
CHAT_HISTORY = '{}/{}'.format(CONFIG_ROOT, 'ChatHistory.json')
RESOURCES_PATH = '{}/resources'.format(os.path.dirname(__file__).replace('\\', '/'))


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

    def delete_message_by_index(self, chat_name, index):
        if (self._storage[chat_name]['messages'] and
                self._storage[chat_name]['messages'][0]['role'] == 'system'):
            index += 1
        self._storage[chat_name]['messages'].pop(index)
        self._save_history()

    def pop_message(self, chat_name):
        self._storage[chat_name]['messages'].pop()
        self._save_history()

    def get_message_by_index(self, chat_name, index):
        if (self._storage[chat_name]['messages'] and
                self._storage[chat_name]['messages'][0]['role'] == 'system'):
            index += 1
        return self._storage[chat_name]['messages'][: index]

    def replace_message_by_index(self, chat_name, message, index=None):
        if index is not None:
            if (self._storage[chat_name]['messages'] and
                    self._storage[chat_name]['messages'][0]['role'] == 'system'):
                index += 1
        else:
            index = len(self._storage[chat_name]['messages']) - 1
        try:
            self._storage[chat_name]['messages'][index]['content'] = message
        except:
            self._storage[chat_name]['messages'].append({'role': 'assistant', 'content': message})
        self._save_history()

    def set_system_message(self, chat_name, message):
        if ('messages' not in self._storage[chat_name] or
                not self._storage[chat_name]['messages']):
            self._storage[chat_name].setdefault('messages', []).append(
                {'role': 'system', 'content': message})
        else:
            if self._storage[chat_name]['messages'][0]['role'] == 'system':
                self._storage[chat_name]['messages'][0]['content'] = message
            else:
                self._storage[chat_name]['messages'].insert(
                    0, {'role': 'system', 'content': message})

        self._save_history()

    def delete_system_message(self, chat_name):
        if 'messages' not in self._storage[chat_name]:
            return
        if (not self._storage[chat_name]['messages'] or
                self._storage[chat_name]['messages'][0]['role'] != 'system'):
            return
        self._storage[chat_name]['messages'].pop(0)

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
