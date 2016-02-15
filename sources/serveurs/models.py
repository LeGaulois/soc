# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class ApiKeys(models.Model):
    token = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'api_keys'


class AutomaticExploitationMatchResults(models.Model):
    match_id = models.IntegerField(blank=True, null=True)
    run_id = models.IntegerField(blank=True, null=True)
    state = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'automatic_exploitation_match_results'


class AutomaticExploitationMatchSets(models.Model):
    workspace_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'automatic_exploitation_match_sets'


class AutomaticExploitationMatches(models.Model):
    module_detail_id = models.IntegerField(blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    nexpose_data_vulnerability_definition_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    match_set_id = models.IntegerField(blank=True, null=True)
    matchable_type = models.CharField(max_length=255, blank=True, null=True)
    matchable_id = models.IntegerField(blank=True, null=True)
    module_fullname = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'automatic_exploitation_matches'


class AutomaticExploitationRuns(models.Model):
    workspace_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    match_set_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'automatic_exploitation_runs'


class Clients(models.Model):
    host_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    ua_string = models.CharField(max_length=1024)
    ua_name = models.CharField(max_length=64, blank=True, null=True)
    ua_ver = models.CharField(max_length=32, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'clients'


class CredentialCoresTasks(models.Model):
    core_id = models.IntegerField(blank=True, null=True)
    task_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'credential_cores_tasks'


class CredentialLoginsTasks(models.Model):
    login_id = models.IntegerField(blank=True, null=True)
    task_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'credential_logins_tasks'


class Creds(models.Model):
    service_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.CharField(max_length=2048, blank=True, null=True)
    pass_field = models.CharField(db_column='pass', max_length=4096, blank=True, null=True)  # Field renamed because it was a Python reserved word.
    active = models.NullBooleanField()
    proof = models.CharField(max_length=4096, blank=True, null=True)
    ptype = models.CharField(max_length=256, blank=True, null=True)
    source_id = models.IntegerField(blank=True, null=True)
    source_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'creds'


class Events(models.Model):
    workspace_id = models.IntegerField(blank=True, null=True)
    host_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    critical = models.NullBooleanField()
    seen = models.NullBooleanField()
    username = models.CharField(max_length=255, blank=True, null=True)
    info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'events'


class ExploitAttempts(models.Model):
    host_id = models.IntegerField(blank=True, null=True)
    service_id = models.IntegerField(blank=True, null=True)
    vuln_id = models.IntegerField(blank=True, null=True)
    attempted_at = models.DateTimeField(blank=True, null=True)
    exploited = models.NullBooleanField()
    fail_reason = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    module = models.TextField(blank=True, null=True)
    session_id = models.IntegerField(blank=True, null=True)
    loot_id = models.IntegerField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    proto = models.CharField(max_length=255, blank=True, null=True)
    fail_detail = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'exploit_attempts'


class ExploitedHosts(models.Model):
    host_id = models.IntegerField()
    service_id = models.IntegerField(blank=True, null=True)
    session_uuid = models.CharField(max_length=8, blank=True, null=True)
    name = models.CharField(max_length=2048, blank=True, null=True)
    payload = models.CharField(max_length=2048, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'exploited_hosts'


class HostDetails(models.Model):
    host_id = models.IntegerField(blank=True, null=True)
    nx_console_id = models.IntegerField(blank=True, null=True)
    nx_device_id = models.IntegerField(blank=True, null=True)
    src = models.CharField(max_length=255, blank=True, null=True)
    nx_site_name = models.CharField(max_length=255, blank=True, null=True)
    nx_site_importance = models.CharField(max_length=255, blank=True, null=True)
    nx_scan_template = models.CharField(max_length=255, blank=True, null=True)
    nx_risk_score = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'host_details'


class Hosts(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    address = models.GenericIPAddressField()
    mac = models.CharField(max_length=255, blank=True, null=True)
    comm = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    os_name = models.CharField(max_length=255, blank=True, null=True)
    os_flavor = models.CharField(max_length=255, blank=True, null=True)
    os_sp = models.CharField(max_length=255, blank=True, null=True)
    os_lang = models.CharField(max_length=255, blank=True, null=True)
    arch = models.CharField(max_length=255, blank=True, null=True)
    workspace_id = models.IntegerField()
    updated_at = models.DateTimeField(blank=True, null=True)
    purpose = models.TextField(blank=True, null=True)
    info = models.CharField(max_length=65536, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    scope = models.TextField(blank=True, null=True)
    virtual_host = models.TextField(blank=True, null=True)
    note_count = models.IntegerField(blank=True, null=True)
    vuln_count = models.IntegerField(blank=True, null=True)
    service_count = models.IntegerField(blank=True, null=True)
    host_detail_count = models.IntegerField(blank=True, null=True)
    exploit_attempt_count = models.IntegerField(blank=True, null=True)
    cred_count = models.IntegerField(blank=True, null=True)
    detected_arch = models.CharField(max_length=255, blank=True, null=True)
    application = models.CharField(max_length=30, blank=True, null=True)
    criticite = models.CharField(max_length=15, blank=True, null=True)
    type_machine = models.CharField(max_length=30, blank=True, null=True)
    localisation = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hosts'
        unique_together = (('workspace_id', 'address'),)


class HostsTags(models.Model):
    host_id = models.IntegerField(blank=True, null=True)
    tag_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hosts_tags'


class Listeners(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    workspace_id = models.IntegerField()
    task_id = models.IntegerField(blank=True, null=True)
    enabled = models.NullBooleanField()
    owner = models.TextField(blank=True, null=True)
    payload = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    options = models.BinaryField(blank=True, null=True)
    macro = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'listeners'


class Loots(models.Model):
    workspace_id = models.IntegerField()
    host_id = models.IntegerField(blank=True, null=True)
    service_id = models.IntegerField(blank=True, null=True)
    ltype = models.CharField(max_length=512, blank=True, null=True)
    path = models.CharField(max_length=1024, blank=True, null=True)
    data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    content_type = models.CharField(max_length=255, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    module_run_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loots'


class Macros(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    owner = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    actions = models.BinaryField(blank=True, null=True)
    prefs = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'macros'


class MetasploitCredentialCores(models.Model):
    origin_id = models.IntegerField()
    origin_type = models.CharField(max_length=255)
    private_id = models.IntegerField(blank=True, null=True)
    public_id = models.IntegerField(blank=True, null=True)
    realm_id = models.IntegerField(blank=True, null=True)
    workspace_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    logins_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metasploit_credential_cores'
        unique_together = (('workspace_id', 'private_id'), ('workspace_id', 'realm_id', 'public_id'), ('workspace_id', 'public_id'), ('workspace_id', 'realm_id', 'public_id', 'private_id'), ('workspace_id', 'realm_id', 'private_id'), ('workspace_id', 'public_id', 'private_id'),)


class MetasploitCredentialLogins(models.Model):
    core_id = models.IntegerField()
    service_id = models.IntegerField()
    access_level = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=255)
    last_attempted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'metasploit_credential_logins'
        unique_together = (('core_id', 'service_id'), ('service_id', 'core_id'),)


class MetasploitCredentialOriginCrackedPasswords(models.Model):
    metasploit_credential_core_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'metasploit_credential_origin_cracked_passwords'


class MetasploitCredentialOriginImports(models.Model):
    filename = models.TextField()
    task_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'metasploit_credential_origin_imports'


class MetasploitCredentialOriginManuals(models.Model):
    user_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'metasploit_credential_origin_manuals'


class MetasploitCredentialOriginServices(models.Model):
    service_id = models.IntegerField()
    module_full_name = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'metasploit_credential_origin_services'
        unique_together = (('service_id', 'module_full_name'),)


class MetasploitCredentialOriginSessions(models.Model):
    post_reference_name = models.TextField()
    session_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'metasploit_credential_origin_sessions'
        unique_together = (('session_id', 'post_reference_name'),)


class MetasploitCredentialPrivates(models.Model):
    type = models.CharField(max_length=255)
    data = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    jtr_format = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metasploit_credential_privates'
        unique_together = (('type', 'data'),)


class MetasploitCredentialPublics(models.Model):
    username = models.CharField(unique=True, max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    type = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'metasploit_credential_publics'


class MetasploitCredentialRealms(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'metasploit_credential_realms'
        unique_together = (('key', 'value'),)


class ModRefs(models.Model):
    module = models.CharField(max_length=1024, blank=True, null=True)
    mtype = models.CharField(max_length=128, blank=True, null=True)
    ref = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mod_refs'


class ModuleActions(models.Model):
    detail_id = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_actions'


class ModuleArchs(models.Model):
    detail_id = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_archs'


class ModuleAuthors(models.Model):
    detail_id = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_authors'


class ModuleDetails(models.Model):
    mtime = models.DateTimeField(blank=True, null=True)
    file = models.TextField(blank=True, null=True)
    mtype = models.CharField(max_length=255, blank=True, null=True)
    refname = models.TextField(blank=True, null=True)
    fullname = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    license = models.CharField(max_length=255, blank=True, null=True)
    privileged = models.NullBooleanField()
    disclosure_date = models.DateTimeField(blank=True, null=True)
    default_target = models.IntegerField(blank=True, null=True)
    default_action = models.TextField(blank=True, null=True)
    stance = models.CharField(max_length=255, blank=True, null=True)
    ready = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'module_details'


class ModuleMixins(models.Model):
    detail_id = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_mixins'


class ModulePlatforms(models.Model):
    detail_id = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_platforms'


class ModuleRefs(models.Model):
    detail_id = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_refs'


class ModuleRuns(models.Model):
    attempted_at = models.DateTimeField(blank=True, null=True)
    fail_detail = models.TextField(blank=True, null=True)
    fail_reason = models.CharField(max_length=255, blank=True, null=True)
    module_fullname = models.TextField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    proto = models.CharField(max_length=255, blank=True, null=True)
    session_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    trackable_id = models.IntegerField(blank=True, null=True)
    trackable_type = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'module_runs'


class ModuleTargets(models.Model):
    detail_id = models.IntegerField(blank=True, null=True)
    index = models.IntegerField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_targets'


class NexposeConsoles(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    enabled = models.NullBooleanField()
    owner = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    password = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    version = models.TextField(blank=True, null=True)
    cert = models.TextField(blank=True, null=True)
    cached_sites = models.BinaryField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nexpose_consoles'


class Notes(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    ntype = models.CharField(max_length=512, blank=True, null=True)
    workspace_id = models.IntegerField()
    service_id = models.IntegerField(blank=True, null=True)
    host_id = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    critical = models.NullBooleanField()
    seen = models.NullBooleanField()
    data = models.TextField(blank=True, null=True)
    vuln_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notes'


class Profiles(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    active = models.NullBooleanField()
    name = models.TextField(blank=True, null=True)
    owner = models.TextField(blank=True, null=True)
    settings = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profiles'


class Refs(models.Model):
    ref_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=512, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'refs'


class ReportTemplates(models.Model):
    workspace_id = models.IntegerField()
    created_by = models.CharField(max_length=255, blank=True, null=True)
    path = models.CharField(max_length=1024, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'report_templates'


class Reports(models.Model):
    workspace_id = models.IntegerField()
    created_by = models.CharField(max_length=255, blank=True, null=True)
    rtype = models.CharField(max_length=255, blank=True, null=True)
    path = models.CharField(max_length=1024, blank=True, null=True)
    options = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    downloaded_at = models.DateTimeField(blank=True, null=True)
    task_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=63, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reports'


class Routes(models.Model):
    session_id = models.IntegerField(blank=True, null=True)
    subnet = models.CharField(max_length=255, blank=True, null=True)
    netmask = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'routes'


class SchemaMigrations(models.Model):
    version = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'schema_migrations'


class Services(models.Model):
    host = models.ForeignKey(Hosts, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    port = models.IntegerField()
    proto = models.CharField(max_length=16)
    state = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'services'
        unique_together = (('host', 'port', 'proto'),)


class SessionEvents(models.Model):
    session_id = models.IntegerField(blank=True, null=True)
    etype = models.CharField(max_length=255, blank=True, null=True)
    command = models.BinaryField(blank=True, null=True)
    output = models.BinaryField(blank=True, null=True)
    remote_path = models.CharField(max_length=255, blank=True, null=True)
    local_path = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'session_events'


class Sessions(models.Model):
    host_id = models.IntegerField(blank=True, null=True)
    stype = models.CharField(max_length=255, blank=True, null=True)
    via_exploit = models.CharField(max_length=255, blank=True, null=True)
    via_payload = models.CharField(max_length=255, blank=True, null=True)
    desc = models.CharField(max_length=255, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    platform = models.CharField(max_length=255, blank=True, null=True)
    datastore = models.TextField(blank=True, null=True)
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(blank=True, null=True)
    close_reason = models.CharField(max_length=255, blank=True, null=True)
    local_id = models.IntegerField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    module_run_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sessions'


class Tags(models.Model):
    user_id = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=1024, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    report_summary = models.BooleanField()
    report_detail = models.BooleanField()
    critical = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tags'


class TaskCreds(models.Model):
    task_id = models.IntegerField()
    cred_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'task_creds'


class TaskHosts(models.Model):
    task_id = models.IntegerField()
    host_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'task_hosts'


class TaskServices(models.Model):
    task_id = models.IntegerField()
    service_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'task_services'


class TaskSessions(models.Model):
    task_id = models.IntegerField()
    session_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'task_sessions'


class Tasks(models.Model):
    workspace_id = models.IntegerField()
    created_by = models.CharField(max_length=255, blank=True, null=True)
    module = models.CharField(max_length=255, blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    path = models.CharField(max_length=1024, blank=True, null=True)
    info = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    progress = models.IntegerField(blank=True, null=True)
    options = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    result = models.TextField(blank=True, null=True)
    module_uuid = models.CharField(max_length=8, blank=True, null=True)
    settings = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tasks'


class Users(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    crypted_password = models.CharField(max_length=255, blank=True, null=True)
    password_salt = models.CharField(max_length=255, blank=True, null=True)
    persistence_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    fullname = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    prefs = models.CharField(max_length=524288, blank=True, null=True)
    admin = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'users'


class VulnAttempts(models.Model):
    vuln_id = models.IntegerField(blank=True, null=True)
    attempted_at = models.DateTimeField(blank=True, null=True)
    exploited = models.NullBooleanField()
    fail_reason = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    module = models.TextField(blank=True, null=True)
    session_id = models.IntegerField(blank=True, null=True)
    loot_id = models.IntegerField(blank=True, null=True)
    fail_detail = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vuln_attempts'


class VulnDetails(models.Model):
    vuln_id = models.IntegerField(blank=True, null=True)
    cvss_score = models.FloatField(blank=True, null=True)
    cvss_vector = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    solution = models.TextField(blank=True, null=True)
    proof = models.BinaryField(blank=True, null=True)
    nx_console_id = models.IntegerField(blank=True, null=True)
    nx_device_id = models.IntegerField(blank=True, null=True)
    nx_vuln_id = models.CharField(max_length=255, blank=True, null=True)
    nx_severity = models.FloatField(blank=True, null=True)
    nx_pci_severity = models.FloatField(blank=True, null=True)
    nx_published = models.DateTimeField(blank=True, null=True)
    nx_added = models.DateTimeField(blank=True, null=True)
    nx_modified = models.DateTimeField(blank=True, null=True)
    nx_tags = models.TextField(blank=True, null=True)
    nx_vuln_status = models.TextField(blank=True, null=True)
    nx_proof_key = models.TextField(blank=True, null=True)
    src = models.CharField(max_length=255, blank=True, null=True)
    nx_scan_id = models.IntegerField(blank=True, null=True)
    nx_vulnerable_since = models.DateTimeField(blank=True, null=True)
    nx_pci_compliance_status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vuln_details'


class Vulns(models.Model):
    host = models.ForeignKey(Hosts, blank=True, null=True)
    service = models.ForeignKey(Services, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    info = models.CharField(max_length=65536, blank=True, null=True)
    exploited_at = models.DateTimeField(blank=True, null=True)
    vuln_detail_count = models.IntegerField(blank=True, null=True)
    vuln_attempt_count = models.IntegerField(blank=True, null=True)
    origin_id = models.IntegerField(blank=True, null=True)
    origin_type = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vulns'


class VulnsRefs(models.Model):
    ref_id = models.IntegerField(blank=True, null=True)
    vuln = models.ForeignKey(Vulns, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vulns_refs'


class WebForms(models.Model):
    web_site_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    path = models.TextField(blank=True, null=True)
    method = models.CharField(max_length=1024, blank=True, null=True)
    params = models.TextField(blank=True, null=True)
    query = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_forms'


class WebPages(models.Model):
    web_site_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    path = models.TextField(blank=True, null=True)
    query = models.TextField(blank=True, null=True)
    code = models.IntegerField()
    cookie = models.TextField(blank=True, null=True)
    auth = models.TextField(blank=True, null=True)
    ctype = models.TextField(blank=True, null=True)
    mtime = models.DateTimeField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    headers = models.TextField(blank=True, null=True)
    body = models.BinaryField(blank=True, null=True)
    request = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_pages'


class WebSites(models.Model):
    service_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    vhost = models.CharField(max_length=2048, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    options = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_sites'


class WebVulns(models.Model):
    web_site_id = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    path = models.TextField()
    method = models.CharField(max_length=1024)
    params = models.TextField()
    pname = models.TextField(blank=True, null=True)
    risk = models.IntegerField()
    name = models.CharField(max_length=1024)
    query = models.TextField(blank=True, null=True)
    category = models.TextField()
    confidence = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    blame = models.TextField(blank=True, null=True)
    request = models.BinaryField(blank=True, null=True)
    proof = models.BinaryField()
    owner = models.CharField(max_length=255, blank=True, null=True)
    payload = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'web_vulns'


class WmapRequests(models.Model):
    host = models.CharField(max_length=255, blank=True, null=True)
    address = models.GenericIPAddressField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    ssl = models.IntegerField(blank=True, null=True)
    meth = models.CharField(max_length=32, blank=True, null=True)
    path = models.TextField(blank=True, null=True)
    headers = models.TextField(blank=True, null=True)
    query = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    respcode = models.CharField(max_length=16, blank=True, null=True)
    resphead = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wmap_requests'


class WmapTargets(models.Model):
    host = models.CharField(max_length=255, blank=True, null=True)
    address = models.GenericIPAddressField(blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    ssl = models.IntegerField(blank=True, null=True)
    selected = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wmap_targets'


class WorkspaceMembers(models.Model):
    workspace_id = models.IntegerField()
    user_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'workspace_members'


class Workspaces(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    boundary = models.CharField(max_length=4096, blank=True, null=True)
    description = models.CharField(max_length=4096, blank=True, null=True)
    owner_id = models.IntegerField(blank=True, null=True)
    limit_to_network = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'workspaces'
