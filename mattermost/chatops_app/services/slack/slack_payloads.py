from dataclasses import dataclass


@dataclass(frozen=True)
class BaseSlackPayload:
    user_id: str
    user_name: str
    trigger_id: str
    command: str
    channel_id: str
    channel_name: str
    response_url: str
    token: str
    api_app_id: str
    dc: str
    initial_command: str

    def make_private_metadata(self) -> dict:
        return {
            'command': self.command,
            'channel_id': self.channel_id,
            'channel_name': self.channel_name,
            'response_url': self.response_url,
            'dc': self.dc,
        }


@dataclass(frozen=True)
class SlackPayload(BaseSlackPayload):
    text: str = ''


@dataclass(frozen=True)
class SlackModalPayload(BaseSlackPayload):
    event_type: str
    view: dict
    actions: dict
    private_metadata: dict

    def make_private_metadata(self) -> dict:
        data = super().make_private_metadata()
        data.update(self.private_metadata)
        return data
