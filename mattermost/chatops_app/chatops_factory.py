from django.conf import settings

from chatops_app.chatops import ChatOps
from chatops_app.service_manager import ServiceManager
from chatops_app.services.command_str_parser import CmdStrParser
from chatops_app.services.imt import imt_parsers
from chatops_app.services.imt.modal_imt import ModalLogicImt
from chatops_app.services.imt.srv_imt_cmd import ImtCmdService
from chatops_app.services.lm import lm_parsers
from chatops_app.services.lm.modal_lm import ModalLogicLm
from chatops_app.services.lm.srv_lm_cmd import LmCmdService
from chatops_app.services.mgr import mgr_parsers
from chatops_app.services.mgr.modal_mgr import ModalLogicMgr
from chatops_app.services.mgr.srv_mgr_cmd import MgrCmdService
from chatops_app.services.slack.srv_slack_modal_transport import SlackModalTransportSrv
from chatops_app.services.slack.srv_slack_transport import SlackTransportSrv


def init():
    CmdStrParser.register_parsers('imt', imt_parsers.CMD_PARSERS)
    CmdStrParser.register_parsers('lmw', lm_parsers.CMD_PARSERS)
    CmdStrParser.register_parsers('mgr', mgr_parsers.CMD_PARSERS)


def get_srv_manager():
    srv_mgr = ServiceManager(threads_count=10)
    srv_mgr.register_service(SlackModalTransportSrv('slack_modal_transport', settings.SLACK_CONFIG))
    srv_mgr.register_service(SlackTransportSrv('slack_msg_transport', settings.SLACK_CONFIG))
    srv_mgr.register_service(ImtCmdService('imt', settings.IMT_CONFIG, settings.SAT_CONFIG))
    srv_mgr.register_service(LmCmdService('lmw', settings.LM_CONFIG, settings.WIDGETS_FILEPATH))
    srv_mgr.register_service(MgrCmdService('mgr', settings.MGR_CONFIG, settings.IMT_CONFIG, settings.SAT_CONFIG))

    return srv_mgr


def get_chatops():
    init()
    chatops = ChatOps(token=settings.SLACK_CONFIG['SLACK_OATH_TOKEN'], threads_count=10,
                      service_manager=get_srv_manager(), default_dc=settings.DC)
    chatops.register_modal_logic(ModalLogicImt('imt'))
    chatops.register_modal_logic(ModalLogicLm('lmw'))
    chatops.register_modal_logic(ModalLogicMgr('mgr'))

    return chatops
