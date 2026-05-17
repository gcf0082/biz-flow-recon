#!/usr/bin/env python3
"""Generate _plan.md for Elasticsearch REST endpoints."""

import os

# Read all extracted routes
routes_file = '/tmp/opencode/all_routes.txt'
routes = []
if os.path.exists(routes_file):
    with open(routes_file) as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split('|')
                if len(parts) == 4:
                    routes.append({
                        'class': parts[0],
                        'method': parts[1],
                        'path': parts[2],
                        'file': parts[3]
                    })

print(f"Loaded {len(routes)} routes")

# Build the output
output = []
output.append('<!--')
output.append('子任务拆分计划。planner 子代理写入 _results/_plan.md。')
output.append('')
output.append('按"审计优先级"（启发式分流 hint，**不是风险结论**）从高到低排序：')
output.append('- high：涉及 auth/login/password/token/script/exec/admin/api-key/saml/oidc/oauth/crypto/encrypt/decrypt/sign/webhook/callback/upload/download/import/export/redirect/proxy 等关键词；或 PUT/DELETE/PATCH 涉及核心业务对象（用户/角色/权限/密钥/凭证/密码/许可）；或涉及安全/鉴权/脚本执行/文件操作/数据导入导出')
output.append('- medium：search/list/query（SQL 注入面 potential）、update/delete（数据修改）、其他带 body 的 POST')
output.append('- low：纯只读 GET / health / metric / config 查询 / 元数据返回')
output.append('')
output.append('子功能 priority 取其内部 endpoint 最高一档。')
output.append('')
output.append('注意：这是一个大型项目（~488 个处理器，543+ 路由），拆分粒度按业务域/maven模块划分。')
output.append('-->')
output.append('')
output.append('# Elasticsearch — 子任务拆分')
output.append('')
output.append('总体策略：按业务域/maven模块划分；按审计优先级 high → medium → low 排序。')
output.append('')
output.append('## 子任务')
output.append('')
output.append('```yaml')
output.append('sub_features:')

# HIGH PRIORITY FEATURES
high_features = []
medium_features = []
low_features = []

# Group 1: Security - User Management & Authentication
sec_user = {
    'name': '安全 — 用户管理与认证',
    'slug': 'security-user-authn',
    'priority': 'high',
    'scope': ['x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/user/',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/RestAuthenticateAction.java',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/RestDelegatePkiAuthenticationAction.java'],
    'endpoints': [
        ('POST', '/_security/user/{username}', 'RestPutUserAction', 'RestPutUserAction.java:46', 'high'),
        ('PUT', '/_security/user/{username}', 'RestPutUserAction', 'RestPutUserAction.java:46', 'high'),
        ('DELETE', '/_security/user/{username}', 'RestDeleteUserAction', 'RestDeleteUserAction.java:38', 'high'),
        ('GET', '/_security/user/{username}', 'RestGetUsersAction', 'RestGetUsersAction.java:40', 'medium'),
        ('PUT', '/_security/user/{username}/_password', 'RestChangePasswordAction', 'RestChangePasswordAction.java:48', 'high'),
        ('POST', '/_security/user/{username}/_password', 'RestChangePasswordAction', 'RestChangePasswordAction.java:48', 'high'),
        ('PUT', '/_security/user/_password', 'RestChangePasswordAction', 'RestChangePasswordAction.java:48', 'high'),
        ('POST', '/_security/user/_password', 'RestChangePasswordAction', 'RestChangePasswordAction.java:48', 'high'),
        ('GET', '/_security/_authenticate', 'RestAuthenticateAction', 'RestAuthenticateAction.java:42', 'high'),
        ('POST', '/_security/delegate_pki', 'RestDelegatePkiAuthenticationAction', 'RestDelegatePkiAuthenticationAction.java:48', 'high'),
        ('POST', '/_security/user/{username}/_enable', 'RestSetEnabledAction', 'RestSetEnabledAction.java:40', 'high'),
        ('POST', '/_security/user/{username}/_disable', 'RestSetEnabledAction', 'RestSetEnabledAction.java:40', 'high'),
        ('GET', '/_security/user/_privileges', 'RestGetUserPrivilegesAction', 'RestGetUserPrivilegesAction.java:49', 'medium'),
        ('GET', '/_security/_query/user', 'RestQueryUserAction', 'RestQueryUserAction.java:81', 'medium'),
        ('POST', '/_security/_query/user', 'RestQueryUserAction', 'RestQueryUserAction.java:81', 'medium'),
        ('GET', '/_security/user/_has_privileges', 'RestHasPrivilegesAction', 'RestHasPrivilegesAction.java:60', 'medium'),
        ('POST', '/_security/user/_has_privileges', 'RestHasPrivilegesAction', 'RestHasPrivilegesAction.java:60', 'medium'),
        ('GET', '/_security/profile/_has_privileges', 'RestProfileHasPrivilegesAction', 'RestProfileHasPrivilegesAction.java:40', 'medium'),
        ('POST', '/_security/profile/_has_privileges', 'RestProfileHasPrivilegesAction', 'RestProfileHasPrivilegesAction.java:40', 'medium'),
    ]
}
high_features.append(sec_user)

# Group 2: API Key management
sec_apikey = {
    'name': '安全 — API 密钥管理',
    'slug': 'security-api-key',
    'priority': 'high',
    'scope': ['x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/apikey/'],
    'endpoints': [
        ('POST', '/_security/api_key', 'RestCreateApiKeyAction', 'RestCreateApiKeyAction.java:47', 'high'),
        ('PUT', '/_security/api_key', 'RestCreateApiKeyAction', 'RestCreateApiKeyAction.java:47', 'high'),
        ('POST', '/_security/api_key/grant', 'RestGrantApiKeyAction', 'RestGrantApiKeyAction.java:114', 'high'),
        ('PUT', '/_security/api_key/grant', 'RestGrantApiKeyAction', 'RestGrantApiKeyAction.java:114', 'high'),
        ('DELETE', '/_security/api_key', 'RestInvalidateApiKeyAction', 'RestInvalidateApiKeyAction.java:60', 'high'),
        ('GET', '/_security/api_key', 'RestGetApiKeyAction', 'RestGetApiKeyAction.java:41', 'high'),
        ('PUT', '/_security/api_key/{ids}', 'RestUpdateApiKeyAction', 'RestUpdateApiKeyAction.java:40', 'high'),
        ('GET', '/_security/_query/api_key', 'RestQueryApiKeyAction', 'RestQueryApiKeyAction.java:105', 'medium'),
        ('POST', '/_security/_query/api_key', 'RestQueryApiKeyAction', 'RestQueryApiKeyAction.java:105', 'medium'),
        ('POST', '/_security/cross_cluster/api_key', 'RestCreateCrossClusterApiKeyAction', 'RestCreateCrossClusterApiKeyAction.java:76', 'high'),
        ('PUT', '/_security/cross_cluster/api_key/{id}', 'RestUpdateCrossClusterApiKeyAction', 'RestUpdateCrossClusterApiKeyAction.java:64', 'high'),
        ('POST', '/_security/api_key/_bulk_update', 'RestBulkUpdateApiKeyAction', 'RestBulkUpdateApiKeyAction.java:41', 'high'),
        ('POST', '/_security/api_key/clone', 'RestCloneApiKeyAction', 'RestCloneApiKeyAction.java:71', 'high'),
        ('PUT', '/_security/api_key/clone', 'RestCloneApiKeyAction', 'RestCloneApiKeyAction.java:71', 'high'),
        ('POST', '/_security/api_key/{ids}/_clear_cache', 'RestClearApiKeyCacheAction', 'RestClearApiKeyCacheAction.java:39', 'medium'),
    ]
}
high_features.append(sec_apikey)

# Group 3: SAML/OIDC/OAuth2
sec_saml = {
    'name': '安全 — SAML / OIDC / OAuth2 认证',
    'slug': 'security-saml-oidc-oauth',
    'priority': 'high',
    'scope': ['x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/saml/',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/oidc/',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/oauth2/'],
    'endpoints': [
        ('POST', '/_security/saml/authenticate', 'RestSamlAuthenticateAction', 'RestSamlAuthenticateAction.java:74', 'high'),
        ('POST', '/_security/saml/prepare', 'RestSamlPrepareAuthenticationAction', 'RestSamlPrepareAuthenticationAction.java:56', 'high'),
        ('POST', '/_security/saml/logout', 'RestSamlLogoutAction', 'RestSamlLogoutAction.java:52', 'high'),
        ('POST', '/_security/saml/invalidate', 'RestSamlInvalidateSessionAction', 'RestSamlInvalidateSessionAction.java:54', 'high'),
        ('POST', '/_security/saml/complete_logout', 'RestSamlCompleteLogoutAction', 'RestSamlCompleteLogoutAction.java:70', 'high'),
        ('GET', '/_security/saml/metadata/{idp}', 'RestSamlSpMetadataAction', 'RestSamlSpMetadataAction.java:37', 'medium'),
        ('POST', '/_security/oidc/authenticate', 'RestOpenIdConnectAuthenticateAction', 'RestOpenIdConnectAuthenticateAction.java:56', 'high'),
        ('POST', '/_security/oidc/prepare', 'RestOpenIdConnectPrepareAuthenticationAction', 'RestOpenIdConnectPrepareAuthenticationAction.java:55', 'high'),
        ('POST', '/_security/oidc/logout', 'RestOpenIdConnectLogoutAction', 'RestOpenIdConnectLogoutAction.java:47', 'high'),
        ('POST', '/_security/oauth2/token', 'RestGetTokenAction', 'RestGetTokenAction.java:86', 'high'),
        ('DELETE', '/_security/oauth2/token', 'RestInvalidateTokenAction', 'RestInvalidateTokenAction.java:71', 'high'),
    ]
}
high_features.append(sec_saml)

# Group 4: Role & Privilege Management
sec_role = {
    'name': '安全 — 角色与权限管理',
    'slug': 'security-role-privilege',
    'priority': 'high',
    'scope': ['x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/role/',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/privilege/',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/rolemapping/'],
    'endpoints': [
        ('POST', '/_security/role/{name}', 'RestPutRoleAction', 'RestPutRoleAction.java:43', 'high'),
        ('PUT', '/_security/role/{name}', 'RestPutRoleAction', 'RestPutRoleAction.java:43', 'high'),
        ('DELETE', '/_security/role/{name}', 'RestDeleteRoleAction', 'RestDeleteRoleAction.java:38', 'high'),
        ('POST', '/_security/role/_bulk', 'RestBulkPutRolesAction', 'RestBulkPutRolesAction.java:39', 'high'),
        ('DELETE', '/_security/role/_bulk', 'RestBulkDeleteRolesAction', 'RestBulkDeleteRolesAction.java:45', 'high'),
        ('POST', '/_security/privilege/{application}/{privilege}', 'RestPutPrivilegesAction', 'RestPutPrivilegesAction.java:45', 'high'),
        ('PUT', '/_security/privilege/{application}/{privilege}', 'RestPutPrivilegesAction', 'RestPutPrivilegesAction.java:45', 'high'),
        ('DELETE', '/_security/privilege/{application}/{privilege}', 'RestDeletePrivilegesAction', 'RestDeletePrivilegesAction.java:42', 'high'),
        ('POST', '/_security/role_mapping/{name}', 'RestPutRoleMappingAction', 'RestPutRoleMappingAction.java:44', 'high'),
        ('PUT', '/_security/role_mapping/{name}', 'RestPutRoleMappingAction', 'RestPutRoleMappingAction.java:44', 'high'),
        ('DELETE', '/_security/role_mapping/{name}', 'RestDeleteRoleMappingAction', 'RestDeleteRoleMappingAction.java:38', 'high'),
        ('GET', '/_security/role/{name}', 'RestGetRolesAction', 'RestGetRolesAction.java:40', 'medium'),
        ('GET', '/_security/role', 'RestGetRolesAction', 'RestGetRolesAction.java:40', 'medium'),
        ('GET', '/_security/_query/role', 'RestQueryRoleAction', 'RestQueryRoleAction.java:80', 'medium'),
        ('POST', '/_security/_query/role', 'RestQueryRoleAction', 'RestQueryRoleAction.java:80', 'medium'),
        ('POST', '/_security/role/{name}/_clear_cache', 'RestClearRolesCacheAction', 'RestClearRolesCacheAction.java:32', 'medium'),
        ('GET', '/_security/privilege/{application}/{privilege}', 'RestGetPrivilegesAction', 'RestGetPrivilegesAction.java:47', 'medium'),
        ('GET', '/_security/privilege/_builtin', 'RestGetBuiltinPrivilegesAction', 'RestGetBuiltinPrivilegesAction.java:65', 'low'),
        ('POST', '/_security/privilege/{application}/_clear_cache', 'RestClearPrivilegesCacheAction', 'RestClearPrivilegesCacheAction.java:39', 'medium'),
        ('GET', '/_security/role_mapping/{name}', 'RestGetRoleMappingsAction', 'RestGetRoleMappingsAction.java:39', 'medium'),
        ('GET', '/_security/role_mapping', 'RestGetRoleMappingsAction', 'RestGetRoleMappingsAction.java:39', 'medium'),
    ]
}
high_features.append(sec_role)

# Group 5: Service Account
sec_svc = {
    'name': '安全 — 服务账号与令牌',
    'slug': 'security-service-account',
    'priority': 'high',
    'scope': ['x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/service/'],
    'endpoints': [
        ('POST', '/_security/service/{namespace}/{service}/credential/token/{name}', 'RestCreateServiceAccountTokenAction', 'RestCreateServiceAccountTokenAction.java:38', 'high'),
        ('PUT', '/_security/service/{namespace}/{service}/credential/token/{name}', 'RestCreateServiceAccountTokenAction', 'RestCreateServiceAccountTokenAction.java:38', 'high'),
        ('DELETE', '/_security/service/{namespace}/{service}/credential/token/{name}', 'RestDeleteServiceAccountTokenAction', 'RestDeleteServiceAccountTokenAction.java:36', 'high'),
        ('GET', '/_security/service/{namespace}/{service}', 'RestGetServiceAccountAction', 'RestGetServiceAccountAction.java:34', 'medium'),
        ('GET', '/_security/service/{namespace}', 'RestGetServiceAccountAction', 'RestGetServiceAccountAction.java:34', 'medium'),
        ('GET', '/_security/service', 'RestGetServiceAccountAction', 'RestGetServiceAccountAction.java:34', 'medium'),
        ('GET', '/_security/service/{namespace}/{service}/credential', 'RestGetServiceAccountCredentialsAction', 'RestGetServiceAccountCredentialsAction.java:34', 'medium'),
        ('POST', '/_security/service/{namespace}/{service}/credential/token/{name}/_clear_cache', 'RestClearServiceAccountTokenStoreCacheAction', 'RestClearServiceAccountTokenStoreCacheAction.java:37', 'medium'),
    ]
}
high_features.append(sec_svc)

# Group 6: Security Other (Realm/Settings/Enrollment/Profile)
sec_other = {
    'name': '安全 — Realm / 缓存 / 设置 / 注册 / 用户画像',
    'slug': 'security-other',
    'priority': 'high',
    'scope': ['x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/realm/',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/settings/',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/enrollment/',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/stats/',
              'x-pack/plugin/security/src/main/java/org/elasticsearch/xpack/security/rest/action/profile/'],
    'endpoints': [
        ('POST', '/_security/realm/{realms}/_clear_cache', 'RestClearRealmCacheAction', 'RestClearRealmCacheAction.java:32', 'medium'),
        ('GET', '/_security/settings', 'RestGetSecuritySettingsAction', 'RestGetSecuritySettingsAction.java:36', 'low'),
        ('PUT', '/_security/settings', 'RestUpdateSecuritySettingsAction', 'RestUpdateSecuritySettingsAction.java:36', 'high'),
        ('GET', '_security/enroll/node', 'RestNodeEnrollmentAction', 'RestNodeEnrollmentAction.java:42', 'high'),
        ('GET', '/_security/enroll/kibana', 'RestKibanaEnrollAction', 'RestKibanaEnrollAction.java:42', 'high'),
        ('GET', '/_security/stats', 'RestSecurityStatsAction', 'RestSecurityStatsAction.java:42', 'low'),
        ('POST', '/_security/profile/_activate', 'RestActivateProfileAction', 'RestActivateProfileAction.java:65', 'high'),
        ('GET', '/_security/profile/{uid}', 'RestGetProfilesAction', 'RestGetProfilesAction.java:37', 'medium'),
        ('GET', '/_security/profile/_suggest', 'RestSuggestProfilesAction', 'RestSuggestProfilesAction.java:65', 'medium'),
        ('POST', '/_security/profile/_suggest', 'RestSuggestProfilesAction', 'RestSuggestProfilesAction.java:65', 'medium'),
        ('POST', '/_security/profile/{uid}/_enable', 'RestEnableProfileAction', 'RestEnableProfileAction.java:35', 'high'),
        ('POST', '/_security/profile/{uid}/_disable', 'RestDisableProfileAction', 'RestDisableProfileAction.java:35', 'high'),
        ('POST', '/_security/profile/{uid}/_data', 'RestUpdateProfileDataAction', 'RestUpdateProfileDataAction.java:51', 'high'),
    ]
}
high_features.append(sec_other)

# Group 7: Stored Scripts
stored_scripts = {
    'name': '存储脚本 & 脚本执行',
    'slug': 'stored-scripts',
    'priority': 'high',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/admin/cluster/RestPutStoredScriptAction.java',
              'server/src/main/java/org/elasticsearch/rest/action/admin/cluster/RestGetStoredScriptAction.java',
              'server/src/main/java/org/elasticsearch/rest/action/admin/cluster/RestDeleteStoredScriptAction.java',
              'modules/lang-painless/src/main/java/org/elasticsearch/painless/action/PainlessExecuteAction.java',
              'modules/lang-painless/src/main/java/org/elasticsearch/painless/action/PainlessContextAction.java'],
    'endpoints': [
        ('POST', '/_scripts/{id}', 'RestPutStoredScriptAction', 'RestPutStoredScriptAction.java:35', 'high'),
        ('PUT', '/_scripts/{id}', 'RestPutStoredScriptAction', 'RestPutStoredScriptAction.java:35', 'high'),
        ('POST', '/_scripts/{id}/{context}', 'RestPutStoredScriptAction', 'RestPutStoredScriptAction.java:35', 'high'),
        ('PUT', '/_scripts/{id}/{context}', 'RestPutStoredScriptAction', 'RestPutStoredScriptAction.java:35', 'high'),
        ('DELETE', '/_scripts/{id}', 'RestDeleteStoredScriptAction', 'RestDeleteStoredScriptAction.java:36', 'high'),
        ('GET', '/_scripts/{id}', 'RestGetStoredScriptAction', 'RestGetStoredScriptAction.java:31', 'high'),
        ('GET', '/_scripts/painless/_execute', 'PainlessExecuteAction.RestAction', 'PainlessExecuteAction.java:903', 'high'),
        ('POST', '/_scripts/painless/_execute', 'PainlessExecuteAction.RestAction', 'PainlessExecuteAction.java:903', 'high'),
    ]
}
high_features.append(stored_scripts)

# Group 8: License Management
license_mgmt = {
    'name': '许可证管理',
    'slug': 'license-management',
    'priority': 'high',
    'scope': ['x-pack/plugin/core/src/main/java/org/elasticsearch/license/'],
    'endpoints': [
        ('POST', '/_license', 'RestPutLicenseAction', 'RestPutLicenseAction.java:31', 'high'),
        ('PUT', '/_license', 'RestPutLicenseAction', 'RestPutLicenseAction.java:31', 'high'),
        ('DELETE', '/_license', 'RestDeleteLicenseAction', 'RestDeleteLicenseAction.java:32', 'high'),
        ('GET', '/_license', 'RestGetLicenseAction', 'RestGetLicenseAction.java:28', 'medium'),
        ('POST', '/_license/start_trial', 'RestPostStartTrialLicense', 'RestPostStartTrialLicense.java:35', 'high'),
        ('POST', '/_license/start_basic', 'RestPostStartBasicLicense', 'RestPostStartBasicLicense.java:28', 'high'),
        ('GET', '/_license/basic_status', 'RestGetBasicStatus', 'RestGetBasicStatus.java:26', 'low'),
        ('GET', '/_license/trial_status', 'RestGetTrialStatus', 'RestGetTrialStatus.java:26', 'low'),
        ('GET', '/_license/feature_usage', 'RestGetFeatureUsageAction', 'RestGetFeatureUsageAction.java:24', 'low'),
    ]
}
high_features.append(license_mgmt)

# Group 9: SSL Certificates
ssl_cert = {
    'name': 'SSL 证书管理',
    'slug': 'ssl-certificates',
    'priority': 'high',
    'scope': ['x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/ssl/rest/'],
    'endpoints': [
        ('GET', '/_ssl/certificates', 'RestGetCertificateInfoAction', 'RestGetCertificateInfoAction.java:43', 'high'),
    ]
}
high_features.append(ssl_cert)

# Group 10: Watcher
watcher = {
    'name': 'Watcher — 监控告警',
    'slug': 'watcher',
    'priority': 'high',
    'scope': ['x-pack/plugin/watcher/src/main/java/org/elasticsearch/xpack/watcher/rest/action/'],
    'endpoints': [
        ('POST', '/_watcher/watch/{id}', 'RestPutWatchAction', 'RestPutWatchAction.java:35', 'high'),
        ('PUT', '/_watcher/watch/{id}', 'RestPutWatchAction', 'RestPutWatchAction.java:35', 'high'),
        ('DELETE', '/_watcher/watch/{id}', 'RestDeleteWatchAction', 'RestDeleteWatchAction.java:30', 'high'),
        ('GET', '/_watcher/watch/{id}', 'RestGetWatchAction', 'RestGetWatchAction.java:30', 'medium'),
        ('POST', '/_watcher/watch/_execute', 'RestExecuteWatchAction', 'RestExecuteWatchAction.java:55', 'high'),
        ('POST', '/_watcher/watch/{id}/_execute', 'RestExecuteWatchAction', 'RestExecuteWatchAction.java:55', 'high'),
        ('POST', '/_watcher/watch/{id}/_ack/{actions}', 'RestAckWatchAction', 'RestAckWatchAction.java:34', 'high'),
        ('POST', '/_watcher/watch/{id}/_activate', 'RestActivateWatchAction', 'RestActivateWatchAction.java:34', 'high'),
        ('POST', '/_watcher/watch/{id}/_deactivate', 'RestActivateWatchAction', 'RestActivateWatchAction.java:34', 'high'),
        ('GET', '/_watcher/stats/{metric}', 'RestWatcherStatsAction', 'RestWatcherStatsAction.java:30', 'low'),
        ('POST', '/_watcher/_start', 'RestWatchServiceAction.StopRestHandler', 'RestWatchServiceAction.java:25', 'medium'),
        ('POST', '/_watcher/_stop', 'RestWatchServiceAction.StopRestHandler', 'RestWatchServiceAction.java:25', 'medium'),
        ('GET', '/_watcher/settings', 'RestGetWatcherSettingsAction', 'RestGetWatcherSettingsAction.java:34', 'low'),
        ('PUT', '/_watcher/settings', 'RestUpdateWatcherSettingsAction', 'RestUpdateWatcherSettingsAction.java:33', 'high'),
        ('GET', '/_watcher/_query/watches', 'RestQueryWatchesAction', 'RestQueryWatchesAction.java:24', 'medium'),
        ('POST', '/_watcher/_query/watches', 'RestQueryWatchesAction', 'RestQueryWatchesAction.java:24', 'medium'),
    ]
}
high_features.append(watcher)

# Group 11: Snapshot operations
snapshot_ops = {
    'name': '快照 — 创建 / 恢复 / 删除 / 克隆 / 挂载 / SLM',
    'slug': 'snapshot-operations',
    'priority': 'high',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/admin/cluster/ (snapshot-related)',
              'x-pack/plugin/slm/src/main/java/',
              'x-pack/plugin/searchable-snapshots/src/main/java/'],
    'endpoints': [
        ('PUT', '/_snapshot/{repository}/{snapshot}', 'RestCreateSnapshotAction', 'RestCreateSnapshotAction.java:33', 'high'),
        ('POST', '/_snapshot/{repository}/{snapshot}', 'RestCreateSnapshotAction', 'RestCreateSnapshotAction.java:33', 'high'),
        ('DELETE', '/_snapshot/{repository}/{snapshot}', 'RestDeleteSnapshotAction', 'RestDeleteSnapshotAction.java:32', 'high'),
        ('POST', '/_snapshot/{repository}/{snapshot}/_restore', 'RestRestoreSnapshotAction', 'RestRestoreSnapshotAction.java:34', 'high'),
        ('PUT', '/_snapshot/{repository}/{snapshot}/_clone/{target_snapshot}', 'RestCloneSnapshotAction', 'RestCloneSnapshotAction.java:30', 'high'),
        ('PUT', '/_slm/policy/{name}', 'RestPutSnapshotLifecycleAction', 'RestPutSnapshotLifecycleAction.java:30', 'high'),
        ('DELETE', '/_slm/policy/{name}', 'RestDeleteSnapshotLifecycleAction', 'RestDeleteSnapshotLifecycleAction.java:28', 'high'),
        ('POST', '/_slm/policy/{name}/_execute', 'RestExecuteSnapshotLifecycleAction', 'RestExecuteSnapshotLifecycleAction.java:29', 'high'),
        ('POST', '/_slm/_execute_retention', 'RestExecuteSnapshotRetentionAction', 'RestExecuteSnapshotRetentionAction.java:28', 'medium'),
        ('POST', '/_snapshot/{repository}/{snapshot}/_mount', 'RestMountSearchableSnapshotAction', 'RestMountSearchableSnapshotAction.java:27', 'high'),
    ]
}
high_features.append(snapshot_ops)

# Group 12: Prometheus
prometheus = {
    'name': 'Prometheus 远程写入 & Query',
    'slug': 'prometheus',
    'priority': 'high',
    'scope': ['x-pack/plugin/prometheus/src/main/java/org/elasticsearch/xpack/prometheus/rest/'],
    'endpoints': [
        ('POST', '/_prometheus/api/v1/write', 'PrometheusRemoteWriteRestAction', 'PrometheusRemoteWriteRestAction.java:48', 'high'),
        ('POST', '/_prometheus/metrics/{dataset}/api/v1/write', 'PrometheusRemoteWriteRestAction', 'PrometheusRemoteWriteRestAction.java:48', 'high'),
        ('POST', '/_prometheus/metrics/{dataset}/{namespace}/api/v1/write', 'PrometheusRemoteWriteRestAction', 'PrometheusRemoteWriteRestAction.java:48', 'high'),
        ('GET', '/_prometheus/api/v1/query', 'PrometheusInstantQueryRestAction', 'PrometheusInstantQueryRestAction.java:57', 'medium'),
        ('GET', '/_prometheus/api/v1/query_range', 'PrometheusQueryRangeRestAction', 'PrometheusQueryRangeRestAction.java:39', 'medium'),
        ('GET', '/_prometheus/api/v1/labels', 'PrometheusLabelsRestAction', 'PrometheusLabelsRestAction.java:46', 'medium'),
        ('GET', '/_prometheus/api/v1/label/{name}/values', 'PrometheusLabelValuesRestAction', 'PrometheusLabelValuesRestAction.java:55', 'medium'),
        ('GET', '/_prometheus/api/v1/series', 'PrometheusSeriesRestAction', 'PrometheusSeriesRestAction.java:46', 'medium'),
        ('GET', '/_prometheus/api/v1/metadata', 'PrometheusMetadataRestAction', 'PrometheusMetadataRestAction.java:40', 'low'),
    ]
}
high_features.append(prometheus)

# Group 13: OTel Ingestion
otel = {
    'name': 'OTel 数据摄取 (OTLP)',
    'slug': 'otel-ingestion',
    'priority': 'high',
    'scope': ['x-pack/plugin/otel-data/src/main/java/org/elasticsearch/xpack/oteldata/otlp/'],
    'endpoints': [
        ('POST', '/_otlp/v1/traces', 'OTLPTracesRestAction', 'OTLPTracesRestAction.java:33', 'high'),
        ('POST', '/_otlp/v1/metrics', 'OTLPMetricsRestAction', 'OTLPMetricsRestAction.java:33', 'high'),
        ('POST', '/_otlp/v1/logs', 'OTLPLogsRestAction', 'OTLPLogsRestAction.java:33', 'high'),
    ]
}
high_features.append(otel)

# Group 14: Inference API
inference = {
    'name': '推理 API (Inference)',
    'slug': 'inference',
    'priority': 'high',
    'scope': ['x-pack/plugin/inference/src/main/java/org/elasticsearch/xpack/inference/rest/'],
    'endpoints': [
        ('PUT', '_inference/{task_type_or_inference_id}', 'RestPutInferenceModelAction', 'RestPutInferenceModelAction.java:38', 'high'),
        ('PUT', '_inference/{task_type}/{inference_id}', 'RestPutInferenceModelAction', 'RestPutInferenceModelAction.java:38', 'high'),
        ('PUT', '_inference/{task_type_or_inference_id}/_update', 'RestUpdateInferenceModelAction', 'RestUpdateInferenceModelAction.java:38', 'high'),
        ('PUT', '_inference/{task_type}/{inference_id}/_update', 'RestUpdateInferenceModelAction', 'RestUpdateInferenceModelAction.java:38', 'high'),
        ('POST', '_inference/{task_type_or_inference_id}', 'RestInferenceAction', 'RestInferenceAction.java:32', 'high'),
        ('POST', '_inference/{task_type}/{inference_id}', 'RestInferenceAction', 'RestInferenceAction.java:32', 'high'),
        ('POST', '_inference/{task_type_or_inference_id}/_stream', 'RestStreamInferenceAction', 'RestStreamInferenceAction.java:41', 'high'),
        ('POST', '_inference/{task_type}/{inference_id}/_stream', 'RestStreamInferenceAction', 'RestStreamInferenceAction.java:41', 'high'),
        ('DELETE', '_inference/{task_type_or_inference_id}', 'RestDeleteInferenceEndpointAction', 'RestDeleteInferenceEndpointAction.java:40', 'high'),
        ('DELETE', '_inference/{task_type}/{inference_id}', 'RestDeleteInferenceEndpointAction', 'RestDeleteInferenceEndpointAction.java:40', 'high'),
        ('PUT', '_inference/_ccm', 'RestPutCCMConfigurationAction', 'RestPutCCMConfigurationAction.java:44', 'high'),
        ('DELETE', '_inference/_ccm', 'RestDeleteCCMConfigurationAction', 'RestDeleteCCMConfigurationAction.java:44', 'high'),
        ('GET', '_inference', 'RestGetInferenceModelAction', 'RestGetInferenceModelAction.java:40', 'low'),
        ('GET', '_inference/_all', 'RestGetInferenceModelAction', 'RestGetInferenceModelAction.java:40', 'low'),
        ('GET', '_inference/{task_type_or_inference_id}', 'RestGetInferenceModelAction', 'RestGetInferenceModelAction.java:40', 'low'),
        ('GET', '_inference/{task_type}/{inference_id}', 'RestGetInferenceModelAction', 'RestGetInferenceModelAction.java:40', 'low'),
        ('GET', '_inference/_services', 'RestGetInferenceServicesAction', 'RestGetInferenceServicesAction.java:35', 'low'),
        ('GET', '_inference/.diagnostics', 'RestGetInferenceDiagnosticsAction', 'RestGetInferenceDiagnosticsAction.java:33', 'low'),
        ('GET', '_inference/_ccm', 'RestGetCCMConfigurationAction', 'RestGetCCMConfigurationAction.java:42', 'low'),
    ]
}
high_features.append(inference)

# Group 15: ES|QL
esql = {
    'name': 'ES|QL 查询引擎',
    'slug': 'esql-query',
    'priority': 'high',
    'scope': ['x-pack/plugin/esql/src/main/java/org/elasticsearch/xpack/esql/action/',
              'x-pack/plugin/esql/src/main/java/org/elasticsearch/xpack/esql/datasources/',
              'x-pack/plugin/esql/src/main/java/org/elasticsearch/xpack/esql/view/'],
    'endpoints': [
        ('POST', '/_query', 'RestEsqlQueryAction', 'RestEsqlQueryAction.java:40', 'high'),
        ('POST', '/_query/async', 'RestEsqlAsyncQueryAction', 'RestEsqlAsyncQueryAction.java:30', 'medium'),
        ('GET', '/_query/async/{id}', 'RestEsqlGetAsyncResultAction', 'RestEsqlGetAsyncResultAction.java:28', 'low'),
        ('POST', '/_query/async/{id}/stop', 'RestEsqlStopAsyncAction', 'RestEsqlStopAsyncAction.java:25', 'medium'),
        ('PUT', '/_query/data_source/{name}', 'RestPutDataSourceAction', 'RestPutDataSourceAction.java:35', 'high'),
        ('DELETE', '/_query/data_source/{name}', 'RestDeleteDataSourceAction', 'RestDeleteDataSourceAction.java:33', 'high'),
        ('GET', '/_query/data_source/{name}', 'RestGetDataSourceAction', 'RestGetDataSourceAction.java:31', 'medium'),
        ('PUT', '/_query/dataset/{name}', 'RestPutDatasetAction', 'RestPutDatasetAction.java:34', 'high'),
        ('DELETE', '/_query/dataset/{name}', 'RestDeleteDatasetAction', 'RestDeleteDatasetAction.java:33', 'high'),
        ('PUT', '/_query/view/{name}', 'RestPutViewAction', 'RestPutViewAction.java:34', 'high'),
        ('DELETE', '/_query/view/{name}', 'RestDeleteViewAction', 'RestDeleteViewAction.java:33', 'high'),
    ]
}
high_features.append(esql)

# Group 16: SQL
sql = {
    'name': 'SQL 查询',
    'slug': 'sql',
    'priority': 'high',
    'scope': ['x-pack/plugin/sql/src/main/java/org/elasticsearch/xpack/sql/plugin/'],
    'endpoints': [
        ('POST', '/_sql', 'RestSqlQueryAction', 'RestSqlQueryAction.java:46', 'high'),
        ('GET', '/_sql', 'RestSqlQueryAction', 'RestSqlQueryAction.java:46', 'medium'),
        ('POST', '/_sql/translate', 'RestSqlTranslateAction', 'RestSqlTranslateAction.java:41', 'medium'),
        ('GET', '/_sql/stats', 'RestSqlStatsAction', 'RestSqlStatsAction.java:23', 'low'),
    ]
}
high_features.append(sql)

# Group 17: Core Document API
core_doc = {
    'name': '核心文档 API',
    'slug': 'core-document',
    'priority': 'high',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/document/'],
    'endpoints': [
        ('POST', '/{index}/_doc/{id}', 'RestIndexAction', 'RestIndexAction.java:59', 'high'),
        ('PUT', '/{index}/_doc/{id}', 'RestIndexAction', 'RestIndexAction.java:59', 'high'),
        ('POST', '/{index}/_doc', 'RestIndexAction', 'RestIndexAction.java:59', 'high'),
        ('DELETE', '/{index}/_doc/{id}', 'RestDeleteAction', 'RestDeleteAction.java:34', 'high'),
        ('POST', '/_bulk', 'RestBulkAction', 'RestBulkAction.java:80', 'high'),
        ('POST', '/{index}/_bulk', 'RestBulkAction', 'RestBulkAction.java:80', 'high'),
        ('POST', '/{index}/_create/{id}', 'RestIndexAction.CreateHandler', 'RestIndexAction.java:81', 'high'),
        ('PUT', '/{index}/_create/{id}', 'RestIndexAction.CreateHandler', 'RestIndexAction.java:81', 'high'),
        ('POST', '/{index}/_update/{id}', 'RestUpdateAction', 'RestUpdateAction.java:38', 'medium'),
        ('GET', '/{index}/_doc/{id}', 'RestGetAction', 'RestGetAction.java:41', 'low'),
        ('GET', '/{index}/_source/{id}', 'RestGetSourceAction', 'RestGetSourceAction.java:44', 'low'),
    ]
}
high_features.append(core_doc)

# Group 18: Reindex
reindex = {
    'name': 'Reindex / Update-By-Query / Delete-By-Query',
    'slug': 'reindex',
    'priority': 'high',
    'scope': ['modules/reindex/src/main/java/org/elasticsearch/reindex/',
              'modules/reindex-management/src/main/java/'],
    'endpoints': [
        ('POST', '/_reindex', 'RestReindexAction', 'RestReindexAction.java:53', 'high'),
        ('POST', '/_update_by_query', 'RestUpdateByQueryAction', 'RestUpdateByQueryAction.java:41', 'high'),
        ('POST', '/_delete_by_query', 'RestDeleteByQueryAction', 'RestDeleteByQueryAction.java:40', 'high'),
        ('GET', '/_reindex/{task_id}', 'RestGetReindexAction', 'RestGetReindexAction.java:41', 'medium'),
        ('GET', '/_reindex', 'RestListReindexAction', 'RestListReindexAction.java:41', 'low'),
        ('POST', '/_reindex/{task_id}/_rethrottle', 'RestReindexRethrottleAction', 'RestReindexRethrottleAction.java:42', 'medium'),
        ('POST', '/_reindex/{task_id}/_cancel', 'RestCancelReindexAction', 'RestCancelReindexAction.java:40', 'medium'),
    ]
}
high_features.append(reindex)

# Group 19: Node Secure Settings
node_secure = {
    'name': '节点安全设置重载',
    'slug': 'node-secure-settings',
    'priority': 'high',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/admin/cluster/RestReloadSecureSettingsAction.java'],
    'endpoints': [
        ('POST', '/_nodes/reload_secure_settings', 'RestReloadSecureSettingsAction', 'RestReloadSecureSettingsAction.java:40', 'high'),
        ('POST', '/_nodes/{nodeId}/reload_secure_settings', 'RestReloadSecureSettingsAction', 'RestReloadSecureSettingsAction.java:40', 'high'),
    ]
}
high_features.append(node_secure)

# ============ MEDIUM PRIORITY ============

# Search API
search = {
    'name': '搜索 API',
    'slug': 'search',
    'priority': 'medium',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/search/',
              'modules/lang-mustache/src/main/java/org/elasticsearch/script/mustache/'],
    'endpoints': [
        ('GET', '/_search', 'RestSearchAction', 'RestSearchAction.java:93', 'medium'),
        ('POST', '/_search', 'RestSearchAction', 'RestSearchAction.java:93', 'medium'),
        ('GET', '/_msearch', 'RestMultiSearchAction', 'RestMultiSearchAction.java:69', 'medium'),
        ('POST', '/_msearch', 'RestMultiSearchAction', 'RestMultiSearchAction.java:69', 'medium'),
        ('GET', '/_search/scroll', 'RestSearchScrollAction', 'RestSearchScrollAction.java:40', 'medium'),
        ('POST', '/_search/scroll', 'RestSearchScrollAction', 'RestSearchScrollAction.java:40', 'medium'),
        ('DELETE', '/_search/scroll', 'RestClearScrollAction', 'RestClearScrollAction.java:33', 'medium'),
        ('GET', '/_search/template', 'RestSearchTemplateAction', 'RestSearchTemplateAction.java:50', 'medium'),
        ('POST', '/_search/template', 'RestSearchTemplateAction', 'RestSearchTemplateAction.java:50', 'medium'),
        ('GET', '/_count', 'RestCountAction', 'RestCountAction.java:48', 'low'),
        ('POST', '/_count', 'RestCountAction', 'RestCountAction.java:48', 'low'),
    ]
}
medium_features.append(search)

# Index Management
index_mgmt = {
    'name': '索引管理 (创建/删除/设置/映射/别名/滚动/调整)',
    'slug': 'index-management',
    'priority': 'medium',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/admin/indices/'],
    'endpoints': [
        ('PUT', '/{index}', 'RestCreateIndexAction', 'RestCreateIndexAction.java:39', 'medium'),
        ('DELETE', '/{index}', 'RestDeleteIndexAction', 'RestDeleteIndexAction.java:33', 'medium'),
        ('PUT', '/{index}/_settings', 'RestUpdateSettingsAction', 'RestUpdateSettingsAction.java:35', 'medium'),
        ('PUT', '/{index}/_mapping', 'RestPutMappingAction', 'RestPutMappingAction.java:38', 'medium'),
        ('POST', '/{index}/_close', 'RestCloseIndexAction', 'RestCloseIndexAction.java:43', 'medium'),
        ('POST', '/{index}/_open', 'RestOpenIndexAction', 'RestOpenIndexAction.java:34', 'medium'),
        ('POST', '/_forcemerge', 'RestForceMergeAction', 'RestForceMergeAction.java:40', 'medium'),
        ('POST', '/_aliases', 'RestIndicesAliasesAction', 'RestIndicesAliasesAction.java:40', 'medium'),
        ('POST', '/{index}/_rollover', 'RestRolloverIndexAction', 'RestRolloverIndexAction.java:40', 'medium'),
        ('POST', '/{index}/_shrink/{target}', 'RestResizeHandler', 'RestResizeHandler.java:58', 'medium'),
        ('POST', '/{index}/_split/{target}', 'RestResizeHandler', 'RestResizeHandler.java:58', 'medium'),
        ('POST', '/{index}/_clone/{target}', 'RestResizeHandler', 'RestResizeHandler.java:58', 'medium'),
        ('POST', '/_cache/clear', 'RestClearIndicesCacheAction', 'RestClearIndicesCacheAction.java:31', 'medium'),
        ('PUT', '/{index}/_block/{block}', 'RestAddIndexBlockAction', 'RestAddIndexBlockAction.java:35', 'medium'),
        ('DELETE', '/{index}/_block/{block}', 'RestRemoveIndexBlockAction', 'RestRemoveIndexBlockAction.java:35', 'medium'),
    ]
}
medium_features.append(index_mgmt)

# Data Streams
data_streams = {
    'name': '数据流管理',
    'slug': 'data-streams',
    'priority': 'medium',
    'scope': ['modules/data-streams/src/main/java/org/elasticsearch/datastreams/'],
    'endpoints': [
        ('PUT', '/_data_stream/{name}', 'RestCreateDataStreamAction', 'RestCreateDataStreamAction.java:34', 'medium'),
        ('DELETE', '/_data_stream/{name}', 'RestDeleteDataStreamAction', 'RestDeleteDataStreamAction.java:35', 'medium'),
        ('PUT', '/_data_stream/{name}/_lifecycle', 'RestPutDataStreamLifecycleAction', 'RestPutDataStreamLifecycleAction.java:46', 'medium'),
        ('DELETE', '/_data_stream/{name}/_lifecycle', 'RestDeleteDataStreamLifecycleAction', 'RestDeleteDataStreamLifecycleAction.java:36', 'medium'),
        ('PUT', '/_data_stream/{name}/_settings', 'RestUpdateDataStreamSettingsAction', 'RestUpdateDataStreamSettingsAction.java:38', 'medium'),
        ('PUT', '/_data_stream/{name}/_mappings', 'RestUpdateDataStreamMappingsAction', 'RestUpdateDataStreamMappingsAction.java:39', 'medium'),
        ('PUT', '/_data_stream/{name}/_options', 'RestPutDataStreamOptionsAction', 'RestPutDataStreamOptionsAction.java:42', 'medium'),
        ('DELETE', '/_data_stream/{name}/_options', 'RestDeleteDataStreamOptionsAction', 'RestDeleteDataStreamOptionsAction.java:36', 'medium'),
        ('POST', '/_data_stream/_migrate/{name}', 'RestMigrateToDataStreamAction', 'RestMigrateToDataStreamAction.java:34', 'medium'),
        ('POST', '/_data_stream/_promote/{name}', 'RestPromoteDataStreamAction', 'RestPromoteDataStreamAction.java:30', 'medium'),
    ]
}
medium_features.append(data_streams)

# Ingest Pipeline
ingest = {
    'name': 'Ingest Pipeline 管理',
    'slug': 'ingest-pipeline',
    'priority': 'medium',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/ingest/',
              'modules/ingest-geoip/src/main/java/org/elasticsearch/ingest/geoip/direct/'],
    'endpoints': [
        ('PUT', '/_ingest/pipeline/{id}', 'RestPutPipelineAction', 'RestPutPipelineAction.java:38', 'medium'),
        ('DELETE', '/_ingest/pipeline/{id}', 'RestDeletePipelineAction', 'RestDeletePipelineAction.java:31', 'medium'),
        ('POST', '/_ingest/pipeline/_simulate', 'RestSimulatePipelineAction', 'RestSimulatePipelineAction.java:33', 'medium'),
        ('POST', '/_ingest/_simulate', 'RestSimulateIngestAction', 'RestSimulateIngestAction.java:56', 'medium'),
        ('PUT', '/_ingest/geoip/database/{id}', 'RestPutDatabaseConfigurationAction', 'RestPutDatabaseConfigurationAction.java:31', 'medium'),
        ('DELETE', '/_ingest/geoip/database/{id}', 'RestDeleteDatabaseConfigurationAction', 'RestDeleteDatabaseConfigurationAction.java:29', 'medium'),
    ]
}
medium_features.append(ingest)

# ILM
ilm = {
    'name': 'ILM — 索引生命周期管理',
    'slug': 'ilm',
    'priority': 'medium',
    'scope': ['x-pack/plugin/ilm/src/main/java/org/elasticsearch/xpack/ilm/action/'],
    'endpoints': [
        ('PUT', '/_ilm/policy/{name}', 'RestPutLifecycleAction', 'RestPutLifecycleAction.java:30', 'medium'),
        ('DELETE', '/_ilm/policy/{name}', 'RestDeleteLifecycleAction', 'RestDeleteLifecycleAction.java:31', 'medium'),
        ('POST', '/_ilm/move/{name}', 'RestMoveToStepAction', 'RestMoveToStepAction.java:28', 'medium'),
        ('POST', '/_ilm/migrate_to_data_tiers', 'RestMigrateToDataTiersAction', 'RestMigrateToDataTiersAction.java:29', 'medium'),
        ('POST', '/{index}/_ilm/retry', 'RestRetryAction', 'RestRetryAction.java:28', 'medium'),
        ('POST', '/{index}/_ilm/remove', 'RestRemoveIndexLifecyclePolicyAction', 'RestRemoveIndexLifecyclePolicyAction.java:30', 'medium'),
        ('POST', '/_ilm/start', 'RestStartILMAction', 'RestStartILMAction.java:28', 'medium'),
        ('POST', '/_ilm/stop', 'RestStopAction', 'RestStopAction.java:28', 'medium'),
    ]
}
medium_features.append(ilm)

# Transform
transform = {
    'name': 'Transform — 数据变换',
    'slug': 'transform',
    'priority': 'medium',
    'scope': ['x-pack/plugin/transform/src/main/java/org/elasticsearch/xpack/transform/rest/action/'],
    'endpoints': [
        ('PUT', '/_transform/{id}', 'RestPutTransformAction', 'RestPutTransformAction.java:50', 'medium'),
        ('DELETE', '/_transform/{id}', 'RestDeleteTransformAction', 'RestDeleteTransformAction.java:28', 'medium'),
        ('POST', '/_transform/{id}/_start', 'RestStartTransformAction', 'RestStartTransformAction.java:37', 'medium'),
        ('POST', '/_transform/{id}/_stop', 'RestStopTransformAction', 'RestStopTransformAction.java:27', 'medium'),
        ('POST', '/_transform/{id}/_schedule_now', 'RestScheduleNowTransformAction', 'RestScheduleNowTransformAction.java:30', 'medium'),
        ('POST', '/_transform/{id}/_update', 'RestUpdateTransformAction', 'RestUpdateTransformAction.java:40', 'medium'),
        ('POST', '/_transform/{id}/_reset', 'RestResetTransformAction', 'RestResetTransformAction.java:28', 'medium'),
        ('POST', '/_transform/{id}/_preview', 'RestPreviewTransformAction', 'RestPreviewTransformAction.java:46', 'medium'),
        ('POST', '/_transform/_upgrade', 'RestUpgradeTransformsAction', 'RestUpgradeTransformsAction.java:30', 'medium'),
    ]
}
medium_features.append(transform)

# Cluster Management
cluster_mgmt = {
    'name': '集群管理 (设置/路由/任务/投票排除/仓库验证)',
    'slug': 'cluster-management',
    'priority': 'medium',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/admin/cluster/'],
    'endpoints': [
        ('PUT', '/_cluster/settings', 'RestClusterUpdateSettingsAction', 'RestClusterUpdateSettingsAction.java:36', 'medium'),
        ('POST', '/_cluster/reroute', 'RestClusterRerouteAction', 'RestClusterRerouteAction.java:35', 'medium'),
        ('POST', '/_cluster/voting_config_exclusions', 'RestAddVotingConfigExclusionAction', 'RestAddVotingConfigExclusionAction.java:30', 'medium'),
        ('DELETE', '/_cluster/voting_config_exclusions', 'RestClearVotingConfigExclusionsAction', 'RestClearVotingConfigExclusionsAction.java:27', 'medium'),
        ('POST', '/_tasks/_cancel', 'RestCancelTasksAction', 'RestCancelTasksAction.java:32', 'medium'),
        ('POST', '/_snapshot/{repository}/_verify', 'RestVerifyRepositoryAction', 'RestVerifyRepositoryAction.java:32', 'medium'),
        ('POST', '/_snapshot/{repository}/_cleanup', 'RestCleanupRepositoryAction', 'RestCleanupRepositoryAction.java:31', 'medium'),
        ('POST', '/_internal/prevalidate_node_removal', 'RestPrevalidateNodeRemovalAction', 'RestPrevalidateNodeRemovalAction.java:29', 'medium'),
    ]
}
medium_features.append(cluster_mgmt)

# Index Templates
templates = {
    'name': '索引模板管理',
    'slug': 'index-templates',
    'priority': 'medium',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/admin/indices/ (template)'],
    'endpoints': [
        ('PUT', '/_index_template/{name}', 'RestPutComposableIndexTemplateAction', 'RestPutComposableIndexTemplateAction.java:48', 'medium'),
        ('DELETE', '/_index_template/{name}', 'RestDeleteComposableIndexTemplateAction', 'RestDeleteComposableIndexTemplateAction.java:31', 'medium'),
        ('PUT', '/_component_template/{name}', 'RestPutComponentTemplateAction', 'RestPutComponentTemplateAction.java:47', 'medium'),
        ('DELETE', '/_component_template/{name}', 'RestDeleteComponentTemplateAction', 'RestDeleteComponentTemplateAction.java:31', 'medium'),
        ('POST', '/_index_template/_simulate', 'RestSimulateIndexTemplateAction', 'RestSimulateIndexTemplateAction.java:34', 'medium'),
        ('POST', '/_index_template/_simulate_index/{name}', 'RestSimulateIndexTemplateAction', 'RestSimulateIndexTemplateAction.java:34', 'medium'),
        ('PUT', '/_template/{name}', 'RestPutIndexTemplateAction', 'RestPutIndexTemplateAction.java:34', 'medium'),
        ('DELETE', '/_template/{name}', 'RestDeleteIndexTemplateAction', 'RestDeleteIndexTemplateAction.java:26', 'medium'),
    ]
}
medium_features.append(templates)

# Async Search
async_search = {
    'name': '异步搜索',
    'slug': 'async-search',
    'priority': 'medium',
    'scope': ['x-pack/plugin/async-search/src/main/java/org/elasticsearch/xpack/search/'],
    'endpoints': [
        ('POST', '/_async_search', 'RestSubmitAsyncSearchAction', 'RestSubmitAsyncSearchAction.java:50', 'medium'),
        ('GET', '/_async_search/{id}', 'RestGetAsyncSearchAction', 'RestGetAsyncSearchAction.java:35', 'low'),
        ('DELETE', '/_async_search/{id}', 'RestDeleteAsyncSearchAction', 'RestDeleteAsyncSearchAction.java:30', 'medium'),
    ]
}
medium_features.append(async_search)

# ML Anomaly Detection
ml_anomaly = {
    'name': '机器学习 — 异常检测作业',
    'slug': 'ml-anomaly-jobs',
    'priority': 'medium',
    'scope': ['x-pack/plugin/ml/src/main/java/org/elasticsearch/xpack/ml/rest/job/',
              'x-pack/plugin/ml/src/main/java/org/elasticsearch/xpack/ml/rest/results/',
              'x-pack/plugin/ml/src/main/java/org/elasticsearch/xpack/ml/rest/datafeeds/',
              'x-pack/plugin/ml/src/main/java/org/elasticsearch/xpack/ml/rest/calendar/',
              'x-pack/plugin/ml/src/main/java/org/elasticsearch/xpack/ml/rest/filter/'],
    'endpoints': [
        ('PUT', '/_ml/anomaly_detectors/{job_id}', 'RestPutJobAction', 'RestPutJobAction.java:34', 'medium'),
        ('DELETE', '/_ml/anomaly_detectors/{job_id}', 'RestDeleteJobAction', 'RestDeleteJobAction.java:37', 'medium'),
        ('POST', '/_ml/anomaly_detectors/{job_id}/_open', 'RestOpenJobAction', 'RestOpenJobAction.java:34', 'medium'),
        ('POST', '/_ml/anomaly_detectors/{job_id}/_close', 'RestCloseJobAction', 'RestCloseJobAction.java:31', 'medium'),
        ('POST', '/_ml/anomaly_detectors/{job_id}/_flush', 'RestFlushJobAction', 'RestFlushJobAction.java:36', 'medium'),
        ('POST', '/_ml/anomaly_detectors/{job_id}/_data', 'RestPostDataAction', 'RestPostDataAction.java:31', 'medium'),
        ('POST', '/_ml/anomaly_detectors/{job_id}/_update', 'RestPostJobUpdateAction', 'RestPostJobUpdateAction.java:32', 'medium'),
        ('PUT', '/_ml/datafeeds/{datafeed_id}', 'RestPutDatafeedAction', 'RestPutDatafeedAction.java:34', 'medium'),
        ('DELETE', '/_ml/datafeeds/{datafeed_id}', 'RestDeleteDatafeedAction', 'RestDeleteDatafeedAction.java:32', 'medium'),
        ('POST', '/_ml/datafeeds/{datafeed_id}/_start', 'RestStartDatafeedAction', 'RestStartDatafeedAction.java:37', 'medium'),
        ('POST', '/_ml/datafeeds/{datafeed_id}/_stop', 'RestStopDatafeedAction', 'RestStopDatafeedAction.java:36', 'medium'),
        ('POST', '/_ml/datafeeds/{datafeed_id}/_preview', 'RestPreviewDatafeedAction', 'RestPreviewDatafeedAction.java:32', 'medium'),
        ('POST', '/_ml/datafeeds/{datafeed_id}/_update', 'RestUpdateDatafeedAction', 'RestUpdateDatafeedAction.java:34', 'medium'),
    ]
}
medium_features.append(ml_anomaly)

# ML Trained Models
ml_models = {
    'name': '机器学习 — 训练模型与推理',
    'slug': 'ml-trained-models',
    'priority': 'medium',
    'scope': ['x-pack/plugin/ml/src/main/java/org/elasticsearch/xpack/ml/rest/inference/',
              'x-pack/plugin/ml/src/main/java/org/elasticsearch/xpack/ml/rest/modelsnapshots/'],
    'endpoints': [
        ('PUT', '/_ml/trained_models/{model_id}', 'RestPutTrainedModelAction', 'RestPutTrainedModelAction.java:30', 'medium'),
        ('DELETE', '/_ml/trained_models/{model_id}', 'RestDeleteTrainedModelAction', 'RestDeleteTrainedModelAction.java:31', 'medium'),
        ('POST', '/_ml/trained_models/{model_id}/deployment/_start', 'RestStartTrainedModelDeploymentAction', 'RestStartTrainedModelDeploymentAction.java:56', 'medium'),
        ('POST', '/_ml/trained_models/{model_id}/deployment/_stop', 'RestStopTrainedModelDeploymentAction', 'RestStopTrainedModelDeploymentAction.java:35', 'medium'),
        ('POST', '/_ml/trained_models/{model_id}/_infer', 'RestInferTrainedModelAction', 'RestInferTrainedModelAction.java:40', 'medium'),
        ('PUT', '/_ml/trained_models/{model_id}/vocabulary', 'RestPutTrainedModelVocabularyAction', 'RestPutTrainedModelVocabularyAction.java:30', 'medium'),
        ('PUT', '/_ml/trained_models/{model_id}/definition_part', 'RestPutTrainedModelDefinitionPartAction', 'RestPutTrainedModelDefinitionPartAction.java:31', 'medium'),
        ('PUT', '/_ml/trained_models/{model_id}/model_aliases/{alias}', 'RestPutTrainedModelAliasAction', 'RestPutTrainedModelAliasAction.java:29', 'medium'),
        ('DELETE', '/_ml/trained_models/{model_id}/model_aliases/{alias}', 'RestDeleteTrainedModelAliasAction', 'RestDeleteTrainedModelAliasAction.java:29', 'medium'),
    ]
}
medium_features.append(ml_models)

# ML Data Frame Analytics
ml_dfa = {
    'name': '机器学习 — 数据帧分析',
    'slug': 'ml-data-frame-analytics',
    'priority': 'medium',
    'scope': ['x-pack/plugin/ml/src/main/java/org/elasticsearch/xpack/ml/rest/dataframe/'],
    'endpoints': [
        ('PUT', '/_ml/data_frame/analytics/{id}', 'RestPutDataFrameAnalyticsAction', 'RestPutDataFrameAnalyticsAction.java:41', 'medium'),
        ('DELETE', '/_ml/data_frame/analytics/{id}', 'RestDeleteDataFrameAnalyticsAction', 'RestDeleteDataFrameAnalyticsAction.java:28', 'medium'),
        ('POST', '/_ml/data_frame/analytics/{id}/_start', 'RestStartDataFrameAnalyticsAction', 'RestStartDataFrameAnalyticsAction.java:29', 'medium'),
        ('POST', '/_ml/data_frame/analytics/{id}/_stop', 'RestStopDataFrameAnalyticsAction', 'RestStopDataFrameAnalyticsAction.java:28', 'medium'),
        ('POST', '/_ml/data_frame/analytics/{id}/_update', 'RestPostDataFrameAnalyticsUpdateAction', 'RestPostDataFrameAnalyticsUpdateAction.java:32', 'medium'),
        ('POST', '/_ml/data_frame/analytics/{id}/_preview', 'RestPreviewDataFrameAnalyticsAction', 'RestPreviewDataFrameAnalyticsAction.java:35', 'medium'),
        ('POST', '/_ml/data_frame/_evaluate', 'RestEvaluateDataFrameAction', 'RestEvaluateDataFrameAction.java:28', 'medium'),
        ('POST', '/_ml/data_frame/_explain', 'RestExplainDataFrameAnalyticsAction', 'RestExplainDataFrameAnalyticsAction.java:35', 'medium'),
    ]
}
medium_features.append(ml_dfa)

# ============ LOW PRIORITY ============

# Cat API
cat_api = {
    'name': 'Cat API',
    'slug': 'cat-api',
    'priority': 'low',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/cat/',
              'x-pack/plugin/transform/src/main/java/org/elasticsearch/xpack/transform/rest/action/RestCatTransformAction.java',
              'x-pack/plugin/ml/src/main/java/org/elasticsearch/xpack/ml/rest/cat/'],
    'endpoints': [
        ('GET', '/_cat', 'RestCatAction', 'RestCatAction.java:42', 'low'),
        ('GET', '/_cat/indices', 'RestIndicesAction', 'RestIndicesAction.java:65', 'low'),
        ('GET', '/_cat/nodes', 'RestNodesAction', 'RestNodesAction.java:74', 'low'),
        ('GET', '/_cat/shards', 'RestShardsAction', 'RestShardsAction.java:63', 'low'),
        ('GET', '/_cat/health', 'RestHealthAction', 'RestHealthAction.java:34', 'low'),
        ('GET', '/_cat/tasks', 'RestTasksAction', 'RestTasksAction.java:54', 'low'),
        ('GET', '/_cat/count', 'RestCountAction', 'RestCountAction.java:46', 'low'),
        ('GET', '/_cat/aliases', 'RestAliasAction', 'RestAliasAction.java:35', 'low'),
        ('GET', '/_cat/templates', 'RestTemplatesAction', 'RestTemplatesAction.java:39', 'low'),
        ('GET', '/_cat/snapshots', 'RestSnapshotAction', 'RestSnapshotAction.java:42', 'low'),
        ('GET', '/_cat/plugins', 'RestPluginsAction', 'RestPluginsAction.java:42', 'low'),
        ('GET', '/_cat/repositories', 'RestRepositoriesAction', 'RestRepositoriesAction.java:36', 'low'),
        ('GET', '/_cat/segments', 'RestSegmentsAction', 'RestSegmentsAction.java:48', 'low'),
        ('GET', '/_cat/thread_pool', 'RestThreadPoolAction', 'RestThreadPoolAction.java:58', 'low'),
        ('GET', '/_cat/fielddata', 'RestFielddataAction', 'RestFielddataAction.java:35', 'low'),
        ('GET', '/_cat/nodeattrs', 'RestNodeAttrsAction', 'RestNodeAttrsAction.java:42', 'low'),
        ('GET', '/_cat/pending_tasks', 'RestPendingClusterTasksAction', 'RestPendingClusterTasksAction.java:33', 'low'),
        ('GET', '/_cat/master', 'RestMasterAction', 'RestMasterAction.java:34', 'low'),
        ('GET', '/_cat/recovery', 'RestCatRecoveryAction', 'RestCatRecoveryAction.java:48', 'low'),
        ('GET', '/_cat/component_templates', 'RestCatComponentTemplateAction', 'RestCatComponentTemplateAction.java:61', 'low'),
    ]
}
low_features.append(cat_api)

# Stats / Info Readonly
stats_info = {
    'name': '集群/节点/索引 统计信息 (只读)',
    'slug': 'cluster-stats-readonly',
    'priority': 'low',
    'scope': ['server/src/main/java/org/elasticsearch/rest/action/admin/cluster/ (stats/info)',
              'server/src/main/java/org/elasticsearch/rest/action/admin/indices/ (stats/info)'],
    'endpoints': [
        ('GET', '/_cluster/stats', 'RestClusterStatsAction', 'RestClusterStatsAction.java:38', 'low'),
        ('GET', '/_cluster/health', 'RestClusterHealthAction', 'RestClusterHealthAction.java:35', 'low'),
        ('GET', '/_cluster/state', 'RestClusterStateAction', 'RestClusterStateAction.java:35', 'low'),
        ('GET', '/_cluster/settings', 'RestClusterGetSettingsAction', 'RestClusterGetSettingsAction.java:27', 'low'),
        ('GET', '/_cluster/pending_tasks', 'RestPendingClusterTasksAction', 'RestPendingClusterTasksAction.java:32', 'low'),
        ('GET', '/_tasks', 'RestListTasksAction', 'RestListTasksAction.java:46', 'low'),
        ('GET', '/_nodes/stats', 'RestNodesStatsAction', 'RestNodesStatsAction.java:46', 'low'),
        ('GET', '/_nodes', 'RestNodesInfoAction', 'RestNodesInfoAction.java:53', 'low'),
        ('GET', '/_nodes/hot_threads', 'RestNodesHotThreadsAction', 'RestNodesHotThreadsAction.java:38', 'low'),
        ('GET', '/_nodes/usage', 'RestNodesUsageAction', 'RestNodesUsageAction.java:35', 'low'),
        ('GET', '/_stats', 'RestIndicesStatsAction', 'RestIndicesStatsAction.java:42', 'low'),
        ('GET', '/_field_caps', 'RestFieldCapabilitiesAction', 'RestFieldCapabilitiesAction.java:40', 'low'),
        ('GET', '/_health_report', 'RestGetHealthAction', 'RestGetHealthAction.java:31', 'low'),
        ('GET', '/_features', 'RestSnapshottableFeaturesAction', 'RestSnapshottableFeaturesAction.java:30', 'low'),
        ('GET', '/_script_language', 'RestGetScriptLanguageAction', 'RestGetScriptLanguageAction.java:27', 'low'),
        ('GET', '/_script_context', 'RestGetScriptContextAction', 'RestGetScriptContextAction.java:27', 'low'),
        ('GET', '/_resolve/index/{name}', 'RestResolveIndexAction', 'RestResolveIndexAction.java:52', 'low'),
    ]
}
low_features.append(stats_info)

# X-Pack Info
xpack_info = {
    'name': 'X-Pack Info / Usage / Deprecation',
    'slug': 'xpack-info',
    'priority': 'low',
    'scope': ['x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/rest/action/',
              'x-pack/plugin/deprecation/src/main/java/org/elasticsearch/xpack/deprecation/'],
    'endpoints': [
        ('GET', '/_xpack', 'RestXPackInfoAction', 'RestXPackInfoAction.java:39', 'low'),
        ('GET', '/_xpack/usage', 'RestXPackUsageAction', 'RestXPackUsageAction.java:28', 'low'),
        ('GET', '/_migration/deprecations', 'RestDeprecationInfoAction', 'RestDeprecationInfoAction.java:30', 'low'),
    ]
}
low_features.append(xpack_info)

# Helper to format YAML
def fmt_yaml_endpoint(ep):
    method, path, cls, file_line, prio = ep
    slug = path.strip('/').replace('/', '-').replace('{', '').replace('}', '').replace('_', '-')
    if slug.startswith('-'):
        slug = slug[1:]
    return f'''      - method: {method}
        path: {path}
        class_method: {cls}#routes
        file_line: {file_line}
        expected_output: endpoint-{method}-{slug}.md
        priority: {prio}'''

def fmt_yaml_feature(f):
    lines = []
    lines.append(f'  - name: {f["name"]}')
    lines.append(f'    slug: {f["slug"]}')
    lines.append(f'    priority: {f["priority"]}')
    lines.append('    scope:')
    for s in f['scope']:
        lines.append(f'      - {s}')
    lines.append('    endpoints:')
    for ep in f['endpoints']:
        lines.append(fmt_yaml_endpoint(ep))
    return '\n'.join(lines)

# Write all features
all_features = high_features + medium_features + low_features
for f in all_features:
    output.append('')
    output.append(fmt_yaml_feature(f))

# Separate sections for clarity
# Re-write with section headers
output2 = []
output2.append('<!--')
output2.append('子任务拆分计划。planner 子代理写入 _results/_plan.md。')
output2.append('')
output2.append('按"审计优先级"（启发式分流 hint，**不是风险结论**）从高到低排序：')
output2.append('- high：涉及 auth/login/password/token/script/exec/admin/api-key/saml/oidc/oauth/crypto/encrypt/decrypt/sign/webhook/callback/upload/download/import/export/redirect/proxy 等关键词；或 PUT/DELETE/PATCH 涉及核心业务对象（用户/角色/权限/密钥/凭证/密码/许可）；或涉及安全/鉴权/脚本执行/文件操作/数据导入导出')
output2.append('- medium：search/list/query（SQL 注入面 potential）、update/delete（数据修改）、其他带 body 的 POST')
output2.append('- low：纯只读 GET / health / metric / config 查询 / 元数据返回')
output2.append('')
output2.append('子功能 priority 取其内部 endpoint 最高一档。')
output2.append('')
output2.append('注意：这是一个大型项目（~488 个处理器，543+ 路由），拆分粒度按业务域/maven模块划分。')
output2.append('-->')
output2.append('')
output2.append('# Elasticsearch — 子任务拆分')
output2.append('')
output2.append('总体策略：按业务域/maven模块划分；按审计优先级 high → medium → low 排序。')
output2.append('')
output2.append('## 子任务')
output2.append('')
output2.append('```yaml')
output2.append('sub_features:')

for f in high_features:
    output2.append('')
    output2.append(fmt_yaml_feature(f))

for f in medium_features:
    output2.append('')
    output2.append(fmt_yaml_feature(f))

for f in low_features:
    output2.append('')
    output2.append(fmt_yaml_feature(f))

output2.append('')
output2.append('```')

final_content = '\n'.join(output2)
with open('/root/projects/tmp8/elasticsearch/_results/_plan.md', 'w') as f:
    f.write(final_content)

print(f"Written {len(final_content)} bytes to _results/_plan.md")
print(f"Features: {len(high_features)} high, {len(medium_features)} medium, {len(low_features)} low")
print(f"Total endpoints: {sum(len(f['endpoints']) for f in all_features)}")
