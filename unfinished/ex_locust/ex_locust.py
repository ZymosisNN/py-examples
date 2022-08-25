"""
locust -f ex_locust.py -u 1000 -r 100 --host http://labtools003.infra.five9lab.com:8080
"""
import random
import logging
from locust import FastHttpUser, task, constant, constant_throughput


class LoadUser(FastHttpUser):
    # wait_time = constant(6)
    wait_time = constant_throughput(0.15)
    stop_timeout = 5
    auth_header = '934ot5580492cj58'
    headers = {'Authorization': auth_header}

    @task
    def send_metrics(self):
        datapoints = [{'name': 'load_test_dp_aggreg_type_none',
                       'aggregationType': None,
                       'value': random.randrange(1, 10)
                       }, ]

        data = {'resourceName': 'LM_API_Proxy_Load',
                'datasourceGroup': None,
                'datasourceName': 'LM_API_Proxy_Load_DS',
                'instances': [{'name': 'LM_API_Proxy_Load_inst',
                               'datapoints': datapoints
                               }]
                }

        with self.client.post('/metrics', json=data, headers=self.headers, catch_response=True) as resp:
            logging.info(f'{LoadUser.fullname()} response code: {resp.status_code}')
            if resp.text:
                rate_limit_err = 'proxy rate limit'
                logging.info(f' |-- response text: {resp.text}\n')
                if resp.status_code == 429 and rate_limit_err in resp.text:
                    resp.success()
