import json
from json.decoder import JSONDecodeError
import pickle
from DemistoLive._1CommonServerPython import Demisto
from requests import post
from time import sleep
from pprint import pprint
import os.path
import os

config = json.load(open('d_live.json', 'r'))


def check_for_const(const):
    try:
        return os.environ[const]
    except KeyError:
        return config[const]


CACHE_CONTEXT = check_for_const('CACHE_CONTEXT')
API_KEY = check_for_const('API_KEY')
SERVER_URL = check_for_const('SERVER_URL').rstrip('/')
ARGS = check_for_const('ARGS')
COMMAND = check_for_const('COMMAND')
PARAMS = check_for_const('PARAMS')
INCIDENT_ID = check_for_const('INCIDENT_ID')
CACHE_FILE_NAME = check_for_const('CACHE_FILE_NAME')
POST_RESULTS = check_for_const('POST_RESULTS')
RETRY_COUNT = int(check_for_const('RETRY_COUNT'))
RETRY_TIME = int(check_for_const('RETRY_COUNT'))
IS_INTEGRATION = check_for_const('IS_INTEGRATION')
VERIFY_SSL = check_for_const('VERIFY_SSL')


class DemistoLive(Demisto):
    def __init__(self,
                 cache_context: bool = CACHE_CONTEXT,
                 args: dict = ARGS,
                 command: str = COMMAND,
                 params: dict = PARAMS,
                 is_integration: bool = IS_INTEGRATION):

        self.cache = cache_context
        self.context_entry_id = None
        self.__dd_args = args
        self.__dd_command = command
        self.__dd_params = params
        self.__dd_is_integration = is_integration

        super().__init__(self.request_context())

    def _load_context_from_api(self):
        data = {
            "id": "",
            "version": 0,
            "investigationId": INCIDENT_ID,
            "data": "!py script=\"return_results(demisto.callingContext)\"",
            "args": None,
            "markdown": False
        }
        return self._post_to_api('entry', data)


    @staticmethod
    def _write_context_cache(context):
        with open(CACHE_FILE_NAME, 'wb') as file:
            file.write(pickle.dumps(context))

    @staticmethod
    def _read_context_cache():
        return pickle.load(open(CACHE_FILE_NAME, 'rb'))

    def patch_local_vars_into_execution_context(self, context):
        context[u'args'] = self.__dd_args
        context[u'command'] = self.__dd_command
        context[u'params'] = self.__dd_params
        context[u'integration'] = self.__dd_is_integration
        return context

    def request_context(self):
        if self.cache and os.path.exists(CACHE_FILE_NAME):
            context = self._read_context_cache()
        else:
            entry = self._load_context_from_api()
            self.context_entry_id = entry.get('id')
            context = self.receive_context()
            if self.cache:
                self._write_context_cache(context)

        context = self.patch_local_vars_into_execution_context(context)
        return context

    def receive_context(self):
        response = self.get_command_response(self.context_entry_id).get('contents')
        return json.loads(response)

    def get_command_response(self, parent_id):

        def filter_entry_by_partent_id(entry):
            return entry.get('parentId') == parent_id

        params = {
            "categories": ['commandAndResults']
        }

        response = None
        retries = 0
        while not response and retries < RETRY_COUNT:
            query_resp = self._post_to_api(f'/investigation/{INCIDENT_ID}', params)
            entries = query_resp.get('entries')
            responses = filter(filter_entry_by_partent_id, entries)
            try:
                response = next(responses)
            except StopIteration:
                sleep(RETRY_TIME)
                retries += 1

        return response

    def _post_to_api(self, uri, data):
        return post(
            url=f'{SERVER_URL}/{uri}',
            headers={'Authorization': API_KEY,
                     'Content-Type': 'application/json'},
            verify=VERIFY_SSL,
            data=json.dumps(data),
        ).json()

    def __do(self, cmd):
        data = {
                "id": "",
                "version": 0,
                "investigationId": INCIDENT_ID,
                "data": f"!py script=`{cmd}`",
                "args": None,
                "markdown": False
            }
        resp = self._post_to_api('entry', data)
        resp_id = resp.get('id')
        return self.get_command_response(resp_id)

    def unpack_remote_method_response(self, results):
        contents = results.get('contents')
        try:
            contents = json.loads(contents)
            return contents.get('raw')
        except JSONDecodeError:
            return contents

    def call_demisto_remote_method(self, method, arg_string: str = ''):
        command_string = f'{{"raw": demisto.{method}({arg_string})}}'
        results = self.__do(f'return_results({command_string})')
        return self.unpack_remote_method_response(results)

    def executeCommand(self, command, args):
        args = json.dumps(args)
        arg_string = f'"{command}", {args}'
        return self.call_demisto_remote_method('executeCommand', arg_string)

    def demistoUrls(self):
        return self.call_demisto_remote_method('demistoUrls')

    def demistoVersion(self):
        return self.call_demisto_remote_method('demistoVersion')

    def heartbeat(self, msg):
        raise NotImplementedError()

    def string_to_arg_string(self, arg):
        if type(arg) is str:
            return f'\'{arg}\''
        return arg

    def check_for_strings(self, args):
        args = [self.string_to_arg_string(arg) for arg in args]
        return''.join(args)

    def info(self, *args):
        message = ''.join(args)
        print(f'INFO -- {message}')

    def error(self, *args):
        message = ''.join(args)
        print(f'ERROR -- {message}')

    def exception(self, ex):
        raise NotImplementedError()

    def debug(self, *args):
        message = ''.join(args)
        print(f'DEBUG -- {message}')

    def getAllSupportedCommands(self):
        return self.call_demisto_remote_method('getAllSupportedCommands').get('contents')

    def getModules(self):
        return self.call_demisto_remote_method('getModules').get('contents')

    def setContext(self, name, value):
        arg_string = f'\'{name}\', {value}'
        return self.call_demisto_remote_method('setContext', arg_string)

    def dt(self, data, q):
        arg_string = f'{str(data)}, \'{q}\''
        return self.call_demisto_remote_method('dt', arg_string)

    def results(self, results):
        if POST_RESULTS:
            self.call_demisto_remote_method('results', str(results))
        pprint(results)


demisto = DemistoLive()