import MySQLdb
import socket


class DBSession(object):
    update = False

    def __init__(self, log, *args, **kwargs):
        self.options = kwargs
        self.log = log
        self.log.logDebug("Opening connection to %s" % self.options['host'])
        self.db = MySQLdb.connect(*args, **kwargs)
        self.cursor = self.db.cursor(MySQLdb.cursors.DictCursor)

    def __str__(self):
        return str(self.options)

    def commit(self):
        self.db.commit()

    def close(self):
        self.log.logDebug("Closing connection to %s" % self.options['host'])
        self.db.close()

    def _trimf9(self, val):
        if val.endswith('.five9.com'):
            return val.replace('.five9.com', '')

        return val

    def getMMPair(self, dh):
        q = "select dh.name from domain_host" \
            " join maintenance_group mg on mg.primary_core_fk = domain_host.id" \
            " left join domain_host dh on mg.maintenance_core_fk = dh.id and mg.maintenance_core_fk is not NULL" \
            " where domain_host.name='%s'" % dh

        self.cursor.execute(q)
        output = ''
        for item in self.cursor.fetchall():
            output = item['name']
        return output

    def getPDCDHs(self, bdcdh):

        q = "select dh1.name from domain " \
            " left join domain_host dh1 on domain.domain_host_fk = dh1.id " \
            " left join domain_host dh2 on dh2.name = '%s' " \
            " where bkp_domain_host_fk=dh2.id" % bdcdh

        self.cursor.execute(q)
        output = set()
        for item in self.cursor.fetchall():
            output.add(item['name'])
            mmpair = self.getMMPair(item['name'])
            if mmpair != '': output.add(mmpair)
        return output

    def getBDCDHs(self, pdcdh):

        q = "select dh2.name from domain " \
            " left join domain_host dh1 on domain.domain_host_fk = dh1.id " \
            " left join domain_host dh2 on domain.bkp_domain_host_fk = dh2.id " \
            " where dh1.name = '%s' and domain.bkp_domain_host_fk is not NULL" % pdcdh

        self.cursor.execute(q)
        output = set()
        for item in self.cursor.fetchall():
            output.add(item['name'])
            mmpair = self.getMMPair(item['name'])
            if mmpair != '': output.add(mmpair)
        return output

    def getDomainsByDH(self, dh):

        q = "select domain.id,account.num,pd.partition_fk from domain " \
            " join partition_domains pd on pd.domain_fk = domain.id " \
            " join tenant t on t.id = pd.partition_fk " \
            " join account on account.id = t.account_fk " \
            " join domain_host dh1 on domain.domain_host_fk = dh1.id " \
            " where dh1.name like '%s%s%s'" % ("%", dh, "%")

        self.cursor.execute(q)
        return self.cursor.fetchall()

    def getFive9Numbers(self):

        result = {}

        q = "select dnis.name number,dnis.partition_fk,pd.domain_fk,d.name domainName" \
            " from dnis " \
            " join partition_domains pd on pd.partition_fk = dnis.partition_fk " \
            " join domain d on d.id = pd.domain_fk"

        self.cursor.execute(q)
        for item in self.cursor.fetchall():
            result[str(item['number'])[-10:]] = {'domainId': item['domain_fk'], 'domainName': item['domainName']}

        return result

    def getDomainsByDH2(self, dh):

        q = "select domain.id,account.num,pd.partition_fk,dh2.name,nas_rec.name from domain " \
            " join partition_domains pd on pd.domain_fk = domain.id " \
            " join tenant t on t.id = pd.partition_fk " \
            " join account on account.id = t.account_fk " \
            " join domain_host dh1 on domain.domain_host_fk = dh1.id " \
            " left join domain_host dh2 on domain.bkp_domain_host_fk = dh2.id and domain.bkp_domain_host_fk is not NULL" \
            " left join nas nas_rec on domain.bkp_recordings_nas_fk = nas_rec.id and domain.bkp_recordings_nas_fk is not NULL" \
            " where dh1.name like '%s%s%s'" % ("%", dh, "%")

        self.cursor.execute(q)
        return self.cursor.fetchall()

    def getDomainIdBySCCTenant(self, scc_tenant_id):

        q = "select five9domainid from tenants where id = %s" % (scc_tenant_id)
        self.cursor.execute(q)
        return str(self.cursor.fetchall()[0]['five9domainid'])  # self.cursor.fetchall() returns something like {{'five9domainid': 4013},}

    def getMMSlaves(self):

        q = "select dh1.name as master,dh2.name as slave from maintenance_group mg " \
            "join domain_host dh1 on dh1.id = mg.primary_core_fk " \
            "join domain_host dh2 on dh2.id = mg.maintenance_core_fk"

        self.cursor.execute(q)

        masters = []
        slaves = []

        for item in self.cursor.fetchall():
            masters.append(item['master'])
            slaves.append(item['slave'])

        return masters, slaves

    # Return the list of Freedom servers
    def getFreedomServers(self, prefix='', dc=''):
        servers = []

        q = "select name from cluster_member " \
            "where name like '%s%s%s%s%s'" % ('%', prefix, '%', dc, '%')

        self.cursor.execute(q)

        for item in self.cursor.fetchall():
            servers.append(item['name'])

        return servers

    # Return the list of active core-servers
    def getActiveCoreServers(self, dc=''):
        allsrvs = []
        actsrvs = []

        slvs = self.getMMSlaves()[1]

        q = "select name from host " \
            "where name like '%score%s%s%s' " \
            "and provider_fk in (" % ('%', '%', dc, '%') + ",".join(self._getActiveEnvIDs()) + ")"

        self.cursor.execute(q)

        for item in self.cursor.fetchall():
            if not (item['name'] in slvs):
                allsrvs.append(item['name'])

        for srv in allsrvs:
            if 'a.' in srv and srv.replace('a.', '.') in allsrvs:
                continue
            actsrvs.append(srv)

        return actsrvs

    # Return the list of active env-servers
    def getActiveEnvServers(self, dc=''):

        q = "select name from host " \
            "where name not like 'core%' and name not like 'msg%' " \
            "and name not like 'sip%' and name not like 'envdummy%' and provider_fk in (" + ",".join(self._getActiveEnvIDs()) + ")"

        self.cursor.execute(q)

        srvs = []
        for item in self.cursor.fetchall():
            if (dc == '') or (dc in item['name']):
                srvs.append(item['name'])
        return srvs

    # Return the list of active env-servers
    def getInactiveEnvServers(self):

        q = "select name from host " \
            "where name not like 'core%' and name not like 'msg%' " \
            "and name not like 'sip%' and name not like 'envdummy%' and provider_fk not in (" + ",".join(self._getActiveEnvIDs()) + ")"

        self.cursor.execute(q)

        srvs = []
        for item in self.cursor.fetchall():
            srvs.append(item['name'])
        return srvs

    def getServersByProvIDs(self, prids):

        q = "select * from host where provider_fk in (" + prids + ")"

        self.cursor.execute(q)

        srvs = []
        for item in self.cursor.fetchall():
            srvs.append(item['name'])
        return srvs

    def getServersInfoByProvIDs(self, prids):
        data = {}

        q = "select h.name,p.software_version from host h join provider p on p.id=h.provider_fk where h.provider_fk in (" + prids + ")"

        self.cursor.execute(q)

        for item in self.cursor.fetchall():
            data[item['name']] = {'software_version': item['software_version']}

        return data

    def getServersInfo(self, hosts):
        data = {}

        q = "select h.name,p.software_version from host h join provider p on p.id=h.provider_fk where h.name in (" + hosts + ")"

        self.cursor.execute(q)

        for item in self.cursor.fetchall():
            data[item['name']] = {'software_version': item['software_version']}

        return data

    def getVerintServers(self):

        q = "select domain.id, domain.name," \
            " if (extents.flags & (1<<53), 1, 0) as 'Workforce Management (WFM)'," \
            " if (extents.flags & (1<<14), 1, 0) as 'Quality Management (QM)'," \
            " domain.wfm_ris_address as 'WFM Primary RIS Address'," \
            " domain.wfm_secondary_ris_address as 'WFM Secondary RIS Address'," \
            " domain.wfm_em_address as 'WFM EM Address'," \
            " domain.wfm_verint_code as 'WFM Verint Code'," \
            " if (domain.wfm_verint_flags & 1, 1, 0) as 'WFM_OUTBOUND_STATS'," \
            " if (domain.wfm_verint_flags & (1<<1), 1, 0) as 'WFM_INBOUND_STATS'," \
            " if (domain.wfm_verint_flags & (1<<2), 1, 0) as 'WFM_AGENT_STATE'," \
            " if (domain.wfm_verint_flags & (1<<3), 1, 0) as 'WFM_LIST_STATS'," \
            " if (domain.wfm_queue_type=1, 'QUEUE_TYPE_CAMPAIGN', 'QUEUE_TYPE_SKILL') as WfmQueueType," \
            " (select domain_host.name from domain_host where domain_host.id=getDomainHostByDomainIdFunc(domain.id)) as 'domainHost'" \
            " from tenant p" \
            " left join account on p.account_fk=account.id" \
            " left join extents on extents.account_fk=account.id" \
            " left join partition_domains on partition_domains.partition_fk=p.id" \
            " left join domain on partition_domains.domain_fk=domain.id" \
            " where p.flags & 1 = 0 /* enabled */" \
            " and extents.flags & (1<<14) /* QM_VERINT */"

        self.cursor.execute(q)

        srvs = []
        for item in self.cursor.fetchall():
            if not (item['domainHost'] in srvs):
                srvs.append(item['domainHost'])
        return srvs

    def getCalabrioServers(self):

        q = "select domain.id, domain.name, (select domain_host.name from domain_host where domain_host.id=getDomainHostByDomainIdFunc(domain.id)) as 'domainHost'" \
            " from tenant p" \
            " left join account on p.account_fk=account.id" \
            " left join extents on extents.account_fk=account.id" \
            " left join partition_domains on partition_domains.partition_fk=p.id" \
            " left join domain on partition_domains.domain_fk=domain.id" \
            " where p.flags & 1 = 0 /* enabled */" \
            " and extents.flags & (1<<10) /* CALABRIO_ENABLED */"

        self.cursor.execute(q)

        srvs = []
        for item in self.cursor.fetchall():
            if not (item['domainHost'] in srvs):
                srvs.append(item['domainHost'])
        return srvs

    def getSCCSVCservers(self, DC):

        q = 'select distinct host from cluster_member where name like "%sccsvc%' + DC + '%"'
        self.cursor.execute(q)
        srvs = []
        for item in self.cursor.fetchall():
            srvs.append(item['host'])
        return srvs

    def getDomainFarm(self):
        q = "select f.name, d.id from domain d join farm f on f.id = d.farm_fk"

        self.cursor.execute(q)

        domainFarm = {}
        for item in self.cursor.fetchall():
            domainFarm[str(item['id'])] = item['name']

        return domainFarm

    def getDomainJmxInfo(self, did):
        """
        Returns {currentHost, domainId, domainName}
        """
        q = """ select ch.name currentHost, d.id domainId, d.name domainName
                from domain d
                join domain_host dh on dh.id=d.domain_host_fk
                left join domain_host bh on bh.id=d.bkp_domain_host_fk
                join domain_host ch on ch.name=
                    if((select t.name from ha_operations hao
                        join ha_operation_domains had on had.operation_fk = hao.id
                        join ha_operation_types t on (t.ordinal = hao.ha_operation_type_fk)
                        where had.domain_fk = d.id order by hao.timestamp_ms desc limit 1) like '%BACKUP%', bh.name, dh.name)
                where d.id = """ + did

        self.cursor.execute(q)

        item = self.cursor.fetchone()

        return item

    def getDomainInfoById(self, domainIds=[]):
        q = "select f.name as farmName, f.id as farmId, f_nvoip_pdc.name as pdcVoiceFarmName, f_nvoip_bdc.name as bdcVoiceFarmName, d.id as domainId, d.name as domainName," \
            " dh.name as domainHost, a.num accountNum, pd.partition_fk partitionId," \
            " (d.flags & (1 << 43)) as nvoip_flag, if((d.flags & (1 << 35)) > 0, 'Yes', 'No') as 24by7_flag," \
            " (select count(*) from station_group sg where sg.partition_fk = t.id and sg.primary_region_fk is NULL and sg.secondary_region_fk is NULL) as sg_fvs," \
            " (select count(*) from station_group sg where sg.partition_fk = t.id and (sg.primary_region_fk is not NULL or sg.secondary_region_fk is not NULL)) as sg_fgv," \
            " dbs.host pdcMasterDb, dbs_bk.host bdcMasterDb, t.db_name" \
            " from tenant t" \
            " left join partition_domains pd on pd.partition_fk=t.id" \
            " left join domain d on pd.domain_fk=d.id" \
            " join domain_host dh on dh.id = d.domain_host_fk" \
            " join account a on a.id = t.account_fk" \
            " left join farm f on f.id = d.farm_fk" \
            " join data_source ds on ds.name = t.ds_name" \
            " join db_server dbs on dbs.id = ds.primary_db_server_fk" \
            " left join primary_db_server pds on pds.db_server_fk=dbs.id" \
            " left join db_server dbs_bk on dbs_bk.id = pds.backup_db_server_fk" \
            " left join farm f_nvoip_pdc on f_nvoip_pdc.id = d.pdc_nvoip_farm_fk" \
            " left join farm f_nvoip_bdc on f_nvoip_bdc.id = d.bdc_nvoip_farm_fk"

        if len(domainIds):
            q += ' where d.id in ' + str(domainIds).replace('[', '(').replace(']', ')')

        self.cursor.execute(q)

        result = {}
        for item in self.cursor.fetchall():
            if item['domainId'] == None: continue

            domainInfo = {}

            domainInfo['domainId'] = item['domainId']
            domainInfo['partitionId'] = item['partitionId']
            domainInfo['domainName'] = item['domainName']
            domainInfo['domainHost'] = item['domainHost']
            domainInfo['accountNum'] = item['accountNum']
            domainInfo['pdcMasterDb'] = '' if item['pdcMasterDb'] == None else socket.getfqdn(item['pdcMasterDb'])
            domainInfo['bdcMasterDb'] = '' if item['bdcMasterDb'] == None else socket.getfqdn(item['bdcMasterDb'])
            domainInfo['dbName'] = item['db_name']
            domainInfo['farmName'] = '' if item['farmName'] == None else item['farmName']
            domainInfo['pdcVoiceFarmName'] = '' if item['pdcVoiceFarmName'] == None else item['pdcVoiceFarmName']
            domainInfo['bdcVoiceFarmName'] = '' if item['bdcVoiceFarmName'] == None else item['bdcVoiceFarmName']
            domainInfo['farmId'] = '' if item['farmId'] == None else item['farmId']
            domainInfo['24by7'] = item['24by7_flag']

            # 'nvoip' = No | FVS | FGV | Both
            if item['nvoip_flag'] == 0:
                domainInfo['nvoip'] = 'No'
            elif item['sg_fgv'] == 0:
                domainInfo['nvoip'] = 'FVS'
            elif item['sg_fvs'] == 0:
                domainInfo['nvoip'] = 'FGV'
            else:
                domainInfo['nvoip'] = 'Both'

            # if domainInfo['nvoip'] != 'No':
            #    print domainInfo

            result[str(item['domainId'])] = domainInfo

        return result

    def getAllDomainsInfo(self):
        return self.getDomainInfoById()

    def getDomainNameById(self, did):
        q = "select name from domain where id = %s" % did
        self.cursor.execute(q)
        return str(self.cursor.fetchall()[0]['name'])

    def getAcBoards(self, dc):
        result = []

        q = "select name from board_cfg where name like '%" + dc + "%'"

        self.cursor.execute(q)
        for item in self.cursor.fetchall():
            corename = item['name'].split(':')[0]
            suffix = item['name'].split(':')[2]

            tsname = corename.replace('core', 'ts')
            if suffix == '1':
                tsname = tsname.replace('.' + dc, 'a.' + dc)

            result.append(tsname)

        return result

    def getPrompts(self, dInfo):
        result = []
        dId = dInfo['domainId']
        pId = dInfo['partitionId']

        prompts_q = ["select trim(filename) path from prompt where filename is not null and domain_fk=%s" % dId,
                     "select filename path FROM domain_language_prompt",
                     "select filename path from tts_prompt where domain_fk=%s" % dId,
                     "select filename path from system_overridden_prompt where domain_fk=%s" % dId,
                     "select filename path from email_uploaded_file where partition_fk=%d" % pId,
                     "select user_group.greeting_path path from domain_user_groups " \
                     "  left join user_group on user_group.id=domain_user_groups.user_group_fk " \
                     "  where greeting_path is not null and domain_user_groups.domain_fk=%s" % dId]

        for q in prompts_q:
            self.cursor.execute(q)
            for item in self.cursor.fetchall():
                if item['path']: result.append(item['path'])

        return result

    def getAgentStates(self, partitionId, start, end):
        result = {}

        q = "select e.name,count(*) cnt" \
            " from partition_%s_audit a" \
            " join event_type e on e.id = a.event_type" \
            " where ts >= (unix_timestamp('%s') * 1000) and ts <= (unix_timestamp('%s') * 1000) group by e.name" % (partitionId, start, end)

        self.cursor.execute(q)
        for item in self.cursor.fetchall():
            result[item['name']] = item['cnt']

        return result

    def getDnisData(self):
        result = {}

        q = """select case when d.name like '+%' then substr(d.name,2,18) else d.name end dnis, t.name tenantName, t.id tenantId
                from tenant t
                left join dnis d on d.partition_fk = t.id
                where (t.flags & 1) < 1"""

        self.cursor.execute(q)
        index = 0
        for item in self.cursor.fetchall():
            if item['dnis'] == None: index += 1

            result[item['dnis'] or 'NULL_%d' % index] = {'tenantName': item['tenantName'], 'tenantId': item['tenantId'], 'dnis': (item['dnis'] or 'NULL')}

        return result

    def getPromptsWithNames(self, dInfo):
        result = []
        dId = dInfo['domainId']
        pId = dInfo['partitionId']

        prompts_q = ["select trim(filename) path, name from prompt where filename is not null and domain_fk=%s" % dId,
                     "select dlp.filename path, concat(p.name, ' ', dlp.language) name FROM domain_language_prompt dlp join prompt p on p.id = dlp.prompt_fk where dlp.prompt_fk is not null",
                     "select dlp.filename path, concat(p.name, ' ', dlp.language) name FROM domain_language_prompt dlp join system_overridden_prompt sop on sop.id = dlp.system_prompt_fk join prompt p on p.id = sop.prompt_fk where dlp.system_prompt_fk > 0",
                     "select filename path, name from tts_prompt where domain_fk=%s" % dId,
                     "select sop.filename path, p.name from system_overridden_prompt sop left join prompt p on p.id = sop.prompt_fk where sop.domain_fk=%s" % dId,
                     "select filename path, name from email_uploaded_file where partition_fk=%d" % pId,
                     "select user_group.greeting_path path, user_group.name from domain_user_groups " \
                     "  left join user_group on user_group.id=domain_user_groups.user_group_fk " \
                     "  where greeting_path is not null and domain_user_groups.domain_fk=%s" % dId]

        for q in prompts_q:
            self.cursor.execute(q)
            for item in self.cursor.fetchall():
                if item['path']: result.append({'path': item['path'], 'name': item['name']})

        return result

    # Gets NAS related info for all domains or for a particular domain (did)
    def getActiveDomainsNasInfo(self, dc, did='all'):
        q = "select d.id as domainId, d.name as domainName, t.db_name, db.host, dh.name as domainHost, pd.partition_fk partitionId," \
            " n.name prompts_nas, n.mount_point prompts_mount," \
            " db_bk.host bkp_db," \
            " n1.name bkp_prompts_nas, n1.mount_point bkp_prompts_mount," \
            " (select group_concat(fvp_n.name) from domain_nas dn join nas fvp_n on fvp_n.id = dn.nas_fk and fvp_n.name like 'fvp%' where dn.domain_fk = d.id) fvpnases" \
            " from domain d" \
            " join partition_domains pd on pd.domain_fk = d.id" \
            " join tenant t on t.id = pd.partition_fk" \
            " join data_source ds on ds.name = t.ds_name" \
            " join db_server db on db.id = ds.primary_db_server_fk" \
            " left join primary_db_server pds ON pds.db_server_fk=db.id" \
            " left join db_server db_bk ON db_bk.id=pds.backup_db_server_fk" \
            " join nas n on n.id=d.prompts_nas_fk" \
            " left join nas n1 on n1.id=d.bkp_prompts_nas_fk" \
            " join domain_host dh on dh.id = d.domain_host_fk" \
            " where (t.flags & 1) < 1 and (d.flags & (1<< 17)) < 1 and t.flags&2 = 0" \
            " and dh.name not like 'sip%%' and dh.name like '%." + dc + ".%'"

        if did != 'all':
            q += " and d.id = " + did

        self.cursor.execute(q)

        result = {}
        for item in self.cursor.fetchall():
            if item['domainId'] == None: continue

            domainInfo = {}

            domainInfo['domainId'] = item['domainId']
            domainInfo['domainName'] = item['domainName']
            domainInfo['domainHost'] = item['domainHost']
            domainInfo['dbname'] = item['db_name']
            domainInfo['dbhost'] = item['host']
            domainInfo['prompts_nas'] = item['prompts_nas']
            domainInfo['prompts_mount'] = item['prompts_mount']
            domainInfo['bkp_prompts_nas'] = item['bkp_prompts_nas']
            domainInfo['bkp_prompts_mount'] = item['bkp_prompts_mount']
            domainInfo['partitionId'] = item['partitionId']
            domainInfo['bkp_dbhost'] = item['bkp_db']
            domainInfo['fvpnases'] = item['fvpnases'].split(',') if item['fvpnases'] else []

            result[str(item['domainId'])] = domainInfo

        return result

    def getWfmRisData(self):
        result = {}

        q = "select distinct siprec_otg_name, wfm_ris_address, wfm_secondary_ris_address from domain where siprec_otg_name is not null and wfm_ris_address is not null"
        self.cursor.execute(q)

        for item in self.cursor.fetchall():
            ris_name = item['wfm_ris_address'].split(':')[0]
            ris_port = item['wfm_ris_address'].split(':')[1]
            result[ris_name] = {'otg': item['siprec_otg_name'], 'port': ris_port, 'primary': True}

            if item['wfm_secondary_ris_address']:
                ris_name = item['wfm_secondary_ris_address'].split(':')[0]
                ris_port = item['wfm_secondary_ris_address'].split(':')[1]
                result[ris_name] = {'otg': item['siprec_otg_name'], 'port': ris_port, 'primary': False}

        return result

    def getAllFdmDomainsInfo(self):
        q = "select f.name as farmName, f.id as farmId, d.id as domainId, d.name as domainName, dh.name as domainHost, ch.name as currentHost," \
            " (d.flags & (1 << 43)) as nvoip_flag, if((d.flags & (1 << 35)) > 0, 'Yes', 'No') as 24by7_flag," \
            " (select count(*) from station_group sg where sg.partition_fk = t.id and sg.primary_region_fk is NULL and sg.secondary_region_fk is NULL) as sg_fvs," \
            " (select count(*) from station_group sg where sg.partition_fk = t.id and (sg.primary_region_fk is not NULL or sg.secondary_region_fk is not NULL)) as sg_fgv" \
            " from tenant t" \
            " left join partition_domains pd on pd.partition_fk=t.id" \
            " left join domain d on pd.domain_fk=d.id" \
            " left join domain_host dh on dh.id = d.domain_host_fk" \
            " left join domain_host bh on bh.id=d.bkp_domain_host_fk" \
            " join farm f on f.id = d.farm_fk" \
            " left join domain_host ch on ch.name=if(f.name like '%ATL%' or f.name like '%AMS%', bh.name, dh.name)"

        self.cursor.execute(q)

        result = {}
        for item in self.cursor.fetchall():
            if item['domainId'] == None: continue

            domainInfo = {}

            domainInfo['domainId'] = item['domainId']
            domainInfo['domainName'] = item['domainName']
            domainInfo['domainHost'] = item['domainHost']
            domainInfo['currentHost'] = item['currentHost']
            domainInfo['farmName'] = '' if item['farmName'] == None else item['farmName']
            domainInfo['farmId'] = '' if item['farmId'] == None else item['farmId']
            domainInfo['24by7'] = item['24by7_flag']

            # 'nvoip' = No | FVS | FGV | Both
            if item['nvoip_flag'] == 0:
                domainInfo['nvoip'] = 'No'
            elif item['sg_fgv'] == 0:
                domainInfo['nvoip'] = 'FVS'
            elif item['sg_fvs'] == 0:
                domainInfo['nvoip'] = 'FGV'
            else:
                domainInfo['nvoip'] = 'Both'

            # if domainInfo['nvoip'] != 'No':
            #    print domainInfo

            result[str(item['domainId'])] = domainInfo

        return result

    def _getActiveEnvIDs(self):
        q = "select p.id from tenant t " \
            "inner join provider_partitions pp on pp.partition_fk = t.id " \
            "inner join provider p on p.id = pp.provider_fk " \
            "left join partition_domains pd on pd.partition_fk=t.id " \
            "left join domain d on pd.domain_fk=d.id " \
            "left join domain_host dh on dh.id = d.domain_host_fk " \
            "where t.flags&1 = 0 and dh.name not like '%999%' group by 1"

        self.cursor.execute(q)

        ids = []
        for item in self.cursor.fetchall():
            ids.append(str(item['id']))
        return ids

    def _iterate_over(self, tc, q):
        try:
            tc.execute(q)
            for item in tc.fetchall():
                # in case if we're getting data from maindb, cursor is DictCursor, so it'll return dict, instead of tuple
                if isinstance(item, dict):
                    item = item.values()

                yield item[0]
        except:
            # print "error query: %s, error %s" % (q, e)
            pass

    def _iterate(self, tc, q):
        for i in self._iterate_over(tc, q):
            yield i
