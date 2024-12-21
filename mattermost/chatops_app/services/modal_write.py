import json
from typing import Optional, Union, List, Dict

from slack_sdk.models import views, blocks

from chatops_app.services.modal_read import find_by_id, find_by_key, ModalUtilsError


def plain(text: str):
    return blocks.PlainTextObject(text=text)


def section_static_select(*, block_id: str, title: str, action_id: str, options, placeholder: Optional[str] = None):
    return blocks.SectionBlock(
        block_id=block_id,
        text=title,
        accessory=blocks.StaticSelectElement(placeholder=placeholder, action_id=action_id, options=options)
    )


def actions_static_select(*, block_id: str, placeholder: str, action_id: str, options):
    return blocks.ActionsBlock(
        block_id=block_id,
        elements=[blocks.StaticSelectElement(placeholder=placeholder, action_id=action_id, options=options)]
    )


def text_input(title: str, value: str, initial_value: Optional[str] = None):
    return blocks.InputBlock(
        label=title,
        element=blocks.PlainTextInputElement(action_id=value, placeholder=' ', initial_value=initial_value)
    )


def option(text: str = '---', value: Union[int, str] = 'None'):
    return blocks.Option(text=plain(text), value=value)


def checkbox(block_id: str, opts: Dict[str, str], title: Optional[str] = None):
    return blocks.InputBlock(block_id=block_id,
                             label=plain(title or ' '),
                             element=blocks.CheckboxesElement(options=[option(text=opts['text'], value=opts['value'])]),
                             optional=True)


def build_view(title: str, block_list: List[blocks.Block], private_metadata: Union[Dict, str, None]):
    view = views.View(type='modal', title=title, submit='Submit', close='Cancel', blocks=block_list)
    if private_metadata:
        if isinstance(private_metadata, Dict):
            private_metadata = json.dumps(private_metadata)
        view.private_metadata = private_metadata
    return view


def build_empty_section(block_id: str):
    return blocks.SectionBlock(block_id=block_id, text=plain(' '))


__option_direct = option(text='to me only', value='send_ephemeral')
__option_channel = option(text='to all in this channel', value='send_to_channel')
RESULT_DESTINATION_BLOCK = blocks.InputBlock(
    label='Result will be shown:',
    element=blocks.RadioButtonsElement(action_id='cmd_result_destination',
                                       initial_option=__option_direct,
                                       options=[__option_direct, __option_channel])
)

DIVIDER = blocks.DividerBlock()


def add_into_selector(node: Dict,
                      selector_id: str,
                      item_list: Union[List[Dict[str, str]], List[str]],
                      clear: bool):
    """
    Find selector in node and add defined items into its options
    """
    selector = find_by_id(node, selector_id)
    if not selector:
        raise ModalUtilsError(f'Selector with id="{selector_id}" is not found')

    options: List = find_by_key(selector, 'options')
    if not options:
        raise ModalUtilsError(f'Selector with id="{selector_id}" has no key "options"')

    items = [{'text': i, 'value': i} if isinstance(i, str) else i for i in item_list]
    items = [option(item['text'], item['value']).to_dict() for item in items]

    if clear:
        options.clear()
    options.extend(items)


def build_input_blocks(args: List[Dict[str, str]]):
    block_list = []
    for arg in args:
        input_type = arg['input_type']
        if input_type == 'checkbox':
            block_list.append(
                checkbox(block_id=arg['name'], opts={'text': arg['title'], 'value': arg['name']}).to_dict()
            )
        elif input_type == 'entry':
            block_list.append(text_input(arg['title'], arg['name']).to_dict())
        else:
            raise ModalUtilsError(f'Unknown input type: {input_type}')

    return block_list


def replace_block(node: Dict, block_id: str, new_blocks: List[Dict]):
    block_list: List = node['blocks']
    old_block = find_by_id(block_list, block_id)
    for n, block in enumerate(block_list):
        if block == old_block:
            break
    else:
        raise ModalUtilsError(f'Block with id "{block_id}" is not found')

    node['blocks'] = block_list[:n] + new_blocks + block_list[n + 1:]
