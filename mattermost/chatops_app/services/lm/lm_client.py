import base64
import hashlib
import hmac
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

import requests

from chatops_app.abstracts import LogMixin, ChatOpsError


class LmClientError(ChatOpsError):
    pass


class LmClient(LogMixin):
    DELTA_MULTIPLIERS = {
        'm': 60,
        'h': 60 * 60,
        'd': 60 * 60 * 24,
    }

    def __init__(self, params: Dict[str, Any], config: Dict, widgets_filepath: str):
        super().__init__()
        self.params = params
        self.lm_access_key = config['LM_ACCESS_KEY']
        self.lm_access_id = config["LM_ACCESS_ID"]
        self.base_rest_url = f'https://{config["LM_ACC"]}.logicmonitor.com/santaba/rest'
        self.widgets_filepath = widgets_filepath

    def get_widget_image(self):
        self.log_dict(self.params, 'Got params:')

        wid = self.params['widget_id'] or self.get_widget_id()
        filename = Path(__file__).parent / f'widget-{wid}.png'
        self._log.debug(f'{"filename": >16s} = {filename}')

        timeframe = self.params['timeframe']
        match = re.search(r'(?P<value>\d+)(?P<mult>[mhd])', timeframe)
        if not match:
            raise LmClientError(f'Wrong interval format: {timeframe}')

        delta_sec = int(match['value']) * self.DELTA_MULTIPLIERS[match['mult']]
        end_ts = int(time.time())
        start_ts = end_ts - delta_sec

        self.save_widget_graph(wid, start_ts, end_ts, filename)
        self._check_received_file(filename)

        return filename

    def _check_received_file(self, filename):
        if not self.is_text_file(filename):
            return
        self._log.error('Failed to get widget image')
        with open(filename) as err_file:
            file_content = err_file.read()
        try:
            lm_response = json.loads(file_content)
        except json.JSONDecodeError as ex:
            self._log.error(f'LM response:\n{file_content}')
            raise LmClientError(f'LM returned bullshit') from ex

        self.log_json(lm_response, 'LM response:')
        raise LmClientError(lm_response['errmsg'])

    @staticmethod
    def is_text_file(filename):
        proc = subprocess.run(['file', filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return b'ASCII text' in proc.stdout

    def get_widget_id(self):
        """
        Gets widget id by its name.
        Users don't want to use quotes for dashboard and widget names which contain spaces,
        that's why those parameters are taken as lists of words and joined together.
        Returns: widget id
        """
        dashboard = ''.join(self.params['dashboard_name_parts'])
        widget_name = ''.join(self.params['widget_name_parts'])

        wid_list = [w['wid'] for w in self._read_widgets_file()
                    if w['dbname'].replace(' ', '') == dashboard and w['wname'].replace(' ', '') == widget_name]
        if not wid_list:
            raise LmClientError(f'Widget id is not found for dashboard "{dashboard}" and widget name "{widget_name}"')
        if len(wid_list) > 1:
            raise LmClientError(f'More than one widget id found {wid_list} for '
                                f'dashboard "{dashboard}" and widget name "{widget_name}"')
        return wid_list[0]

    def get_dashboard_groups(self):
        """
        Returns:
            dashboards groups list sorted by name, each dashboard group name limited by 75 symbols
            and list size limited by 100 items because of Slack
        """
        dashboard_groups = {w['group'][:76] for w in self._read_widgets_file()}
        return sorted(dashboard_groups)[:100]

    def get_dashboards(self, dashboard_group: str):
        """
        Returns:
            dashboards list sorted by name, each dashboard name limited by 75 symbols because of Slack
        """
        dashboards = {w['dbname'][:76] for w in self._read_widgets_file() if w['group'] == dashboard_group}
        return sorted(dashboards)

    def get_widgets(self, dashboard: str):
        """
        Returns:
            widgets list sorted by name, each widget name limited by 75 symbols because of Slack
        """
        widgets = [w['wname'][:76] for w in self._read_widgets_file() if w['dbname'] == dashboard]
        return sorted(widgets)

    def _read_widgets_file(self):
        """
        The widgets file is updated every 30 minutes by means of external script and has such structures:
            {
            "wname": "fvsvms00xx.atl.five9.com-CPU-Load",
            "wid": 18410,
            "dbname": "eredkin: tmp",
            "did": 988,
            "group": "five9",
            "gid": 1
            },
        """
        with open(self.widgets_filepath) as file:
            return json.loads(file.read())

    def save_widget_graph(self, wid, start, end, filename):
        """
        Save widget to an image file
        Input parameters:
            wid : widget ID
            start : start time in sec since the Epoch
            end : end time in sec since the Epoch
            filename : path to file
        """
        content = self._get_lm_data(path=f'/dashboard/widgets/{wid}/data',
                                    params={'start': start, 'end': end, 'format': 'image'})
        self._log.info(f'Saving image to the file {filename} ...')
        with open(filename, 'wb') as file:
            file.write(content)

    def _get_lm_data(self, path, params):
        """
        Gets data from LM using REST API
        Input parameters:
            path  : str, Relative RESP API Path in LM e.g. "/dashboard/widgets/123456/data"
            params: dict, additional parameters
        Returns:
            Binary image or JSON object with information in case of errors
        """
        # Get current time in milliseconds
        epoch = str(int(time.time() * 1000))

        # Construct signature
        request_vars = 'GET' + epoch + path  # Request details
        hash_obj = hmac.new(bytes(self.lm_access_key, 'UTF-8'),
                            msg=bytes(request_vars, 'UTF-8'),
                            digestmod=hashlib.sha256)
        signature = base64.b64encode(bytes(hash_obj.hexdigest(), 'UTF-8')).decode('UTF-8')

        # Construct headers
        headers = {'Content-Type': 'application/json',
                   'Authorization': f'LMv1 {self.lm_access_id}:{signature}:{epoch}'}
        url = self.base_rest_url + path
        self._log.debug(f'URL: {url}')
        self._log.debug(f'Params: {params}')
        response = requests.get(url, headers=headers, params=params)
        return response.content
