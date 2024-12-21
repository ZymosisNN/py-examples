from doit.action import CmdAction

DOIT_CONFIG = {
    # 'default_tasks': ['my_task_1', 'my_task_2'],
    # 'continue': True,
    'verbosity': 2,
    # 'reporter': 'json',
    'backend': 'json',
}


def task_simple_cmd():
    return {
        'actions': ['echo Preved Medved'],
    }


def task_complex_cmd():
    return {
        'actions': [['python', '-V']],
    }


def task_cmd_action():
    def cmd_maker():
        return 'echo Made by CmdAction'

    return {
        'actions': [CmdAction(cmd_maker)],
    }
