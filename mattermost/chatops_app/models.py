from django.db import models


class SlackUser(models.Model):
    """
    name: Slack user name
    slack_user_id: User ID in Slack
    groups_list: Slack groups of the user (separated by space)
    allowed_commands: Slash commands allowed for the user besides ones in groups (separated by space)
    """
    name = models.CharField('Username', max_length=50)
    slack_user_id = models.CharField('Slack user ID', max_length=20)
    groups_list = models.CharField('Slack user groups', max_length=200, default='', blank=True)
    allowed_commands = models.CharField('Extra allowed commands', max_length=400, default='', blank=True)

    def __str__(self):
        return f'{self.name} (groups: {self.groups_list}, allowed commands: {self.allowed_commands})'


class ServicePermissions(models.Model):
    """
    service: Slash command (without leading "/")
    permissions: Slack user groups which are allowed to use this command (separated by space)
    """
    service = models.CharField(max_length=20)
    allowed_groups = models.CharField(max_length=400, default='', blank=True)

    def __str__(self):
        return f'{self.service}: {self.allowed_groups}'


class MgrQueueState(models.Model):
    name = models.CharField(verbose_name='Name', max_length=20)

    def __str__(self):
        return self.name


class MgrQueue(models.Model):
    name = models.CharField(verbose_name='Name', max_length=100)
    direction = models.CharField(verbose_name='Direction', max_length=20)
    timer = models.CharField(verbose_name='Timer', max_length=20)
    time_opened = models.DateTimeField(verbose_name='Time opened', auto_now_add=True)
    time_closed = models.DateTimeField(verbose_name='Time closed', null=True, blank=True)
    opened_by = models.ForeignKey(SlackUser, on_delete=models.PROTECT, verbose_name='Opened by', related_name='%(class)s_related')
    closed_by = models.ForeignKey(SlackUser, on_delete=models.PROTECT, verbose_name='Closed by', null=True)
    state = models.ForeignKey(MgrQueueState, on_delete=models.PROTECT, verbose_name='State')

    def __str__(self):
        return (f'MGR Queue(name: {self.name}, direction: {self.direction}, timer: {self.timer},'
                f' state: {self.state.name})')

    def to_dict(self):
        return {
            'name': self.name,
            'direction': self.direction,
            'state': self.state.name,
            'opened_by': self.opened_by.name,
            'time_opened': self.time_opened,
            'closed_by': self.closed_by.name if self.closed_by else None,
            'time_closed': self.time_closed if self.time_closed else None,
            'timer': self.timer,
        }


class MgrDomainState(models.Model):
    name = models.CharField(verbose_name='Name', max_length=20)

    def __str__(self):
        return self.name


class MgrDomain(models.Model):
    domain_id = models.IntegerField(verbose_name='Domain ID')
    name = models.CharField(verbose_name='Domain name', max_length=50)
    queue = models.ForeignKey(MgrQueue, on_delete=models.CASCADE, verbose_name='MGR queue')
    requested_by = models.ForeignKey(SlackUser, on_delete=models.PROTECT, verbose_name='Requested by', related_name='%(class)s_related')
    processed_by = models.ForeignKey(SlackUser, on_delete=models.PROTECT, verbose_name='Processed by', null=True)
    state = models.ForeignKey(MgrDomainState, on_delete=models.PROTECT, verbose_name='State', null=True)

    def __str__(self):
        return f'MGR domain(id: {self.domain_id}, name: {self.name}, queue: {self.queue}, state: {self.state.name})'

    def to_dict(self):
        return {
            'domain_id': self.domain_id,
            'name': self.name,
            'queue': self.queue.name,
            'state': self.state.name if self.state else None,
            'requested_by': self.requested_by.name,
            'processed_by': self.processed_by.name if self.processed_by else None,
        }
