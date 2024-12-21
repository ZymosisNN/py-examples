import allure

from log_mixin import LogMixin, quick_logging_setup

quick_logging_setup()


def test_allure_attachments():
    log = LogMixin()
    with allure.step('some step'):
        content = {
            'preved': 'medved',
            'items': [
                111, 222, 333
            ],
            'inner struct': {
                'param1': 'value',
                'param_list': [1, 2, 3, 4]
            }
        }

        log.log_and_report_list(['some', 'demo', 'list'], 'list attach')
        log.log_and_report_json(content, 'json attach')
        log.log_and_report_yaml(content, 'yaml attach')
        log.log_and_report_dict(content, 'dict attach', div_indent=50)
