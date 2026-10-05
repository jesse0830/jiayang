# SmarDaten 表名英文→中文翻译词典

用于 Excel 表名翻译任务。以下为完整去重表名翻译对照（核心字典，约387条）。
本字典之外的增量翻译（77条新表名，含 DW_* 系列21条）见 `new-table-name-additions-202607.md`。

## 工作流引擎 (ACT_)

| 表名 | 中文含义 |
|------|---------|
| ACT_EVT_LOG | 事件日志 |
| ACT_GE_BYTEARRAY | 字节数组（二进制数据） |
| ACT_GE_PROPERTY | 全局属性配置 |
| ACT_HI_ATTACHMENT | 历史附件 |
| ACT_HI_COMMENT | 历史评论 |
| ACT_HI_DETAIL | 历史详情 |
| ACT_HI_IDENTITYLINK | 历史参与者 |
| ACT_HI_PROCINST | 历史流程实例 |
| ACT_HI_TASKINST | 历史任务实例 |
| ACT_HI_VARINST | 历史变量实例 |
| ACT_ID_GROUP | 用户组 |
| ACT_ID_INFO | 用户信息 |
| ACT_ID_MEMBERSHIP | 组成员关系 |
| ACT_ID_USER | 用户 |
| ACT_PROCDEF_INFO | 流程定义信息 |
| ACT_RE_DEPLOYMENT | 流程部署 |
| ACT_RE_MODEL | 流程模型 |
| ACT_RE_PROCDEF | 流程定义 |
| ACT_RU_DEADLETTER_JOB | 运行时死信任务 |
| ACT_RU_EVENT_SUBSCR | 运行时事件订阅 |
| ACT_RU_EXECUTION | 运行时执行实例 |
| ACT_RU_IDENTITYLINK | 运行时参与者 |
| ACT_RU_JOB | 运行时定时任务 |
| ACT_RU_SUSPENDED_JOB | 运行时挂起任务 |
| ACT_RU_TASK | 运行时任务 |
| ACT_RU_TIMER_JOB | 运行时定时器任务 |
| ACT_RU_VARIABLE | 运行时变量 |

## 调度任务 (QRTZ_)

| 表名 | 中文含义 |
|------|---------|
| QRTZ_BLOB_TRIGGERS | 调度触发器（Blob） |
| QRTZ_CALENDARS | 调度日历 |
| QRTZ_CRON_TRIGGERS | Cron表达式触发器 |
| QRTZ_FIRED_TRIGGERS | 已触发的调度任务 |
| QRTZ_LOCKS | 调度锁 |
| QRTZ_PAUSED_TRIGGER_GRPS | 暂停的触发器组 |
| QRTZ_SCHEDULER_STATE | 调度器状态 |
| QRTZ_SIMPLE_TRIGGERS | 简单触发器 |

## 表引用关系 (SREF_)

| 表名 | 中文含义 |
|------|---------|
| SREF_CON_TAB134222686_LEVEL | 表引用层级（134222686） |
| SREF_CON_TAB134222686_REFED | 表被引用关系（134222686） |
| SREF_CON_TAB134222686_REFING | 表引用关系（134222686） |
| SREF_CON_TAB134222687_LEVEL | 表引用层级（134222687） |
| SREF_CON_TAB134222687_REFED | 表被引用关系（134222687） |
| SREF_CON_TAB134222687_REFING | 表引用关系（134222687） |
| SREF_CON_TAB134222689_LEVEL | 表引用层级（134222689） |
| SREF_CON_TAB134222689_REFED | 表被引用关系（134222689） |
| SREF_CON_TAB134222689_REFING | 表引用关系（134222689） |

## 系统基础 (SYS_)

| 表名 | 中文含义 |
|------|---------|
| SYS_AUTH | 系统权限 |
| SYS_DICT | 系统字典 |
| SYS_ENTERPRISE | 系统企业信息 |
| SYS_EXT_ATTRIBUTE_DEFINITION | 扩展属性定义 |
| SYS_LOG | 系统日志 |
| SYS_MDICT | 系统多语言字典 |
| SYS_ROLE_OFFICE | 角色岗位 |
| SYS_TENANT | 租户 |
| SYS_THIRDAPP | 第三方应用 |
| SYS_USER_ICON | 用户头像 |

## 数睿平台业务模块 (TS_)

### 数据治理与分析
| 表名 | 中文含义 |
|------|---------|
| TS_ANALYSIS_DATASET | 分析数据集 |
| TS_ANALYSIS_PREPARE | 分析数据准备 |
| TS_ANALYSIS_SHEET | 分析工作表 |
| TS_ASSET_ASSOCIATIONS_CHOOSE | 资产关联选择 |
| TS_BIGSCREEN_DISPLAY_CONDITION | 大屏显示条件 |
| TS_BIGSCREEN_TP_SLIDE_MASTER | 大屏模板幻灯片母版 |
| TS_DASHBOARD_PREVIEW_TEMPLATE | 仪表盘预览模板 |
| TS_DASHBOARD_PRINT_TEMPLATE | 仪表盘打印模板 |
| TS_REPORT | 报表 |
| TS_REPORT_CELL | 报表单元格 |
| TS_REPORT_SHEET | 报表工作表 |
| TS_REPORT_STRUCTURES | 报表结构 |

### 考勤模块
| 表名 | 中文含义 |
|------|---------|
| TS_ATTENDANCE_CLOCK_RECORD | 考勤打卡记录 |
| TS_ATTEND_CLOCK_RECORD_SUM | 考勤打卡汇总 |
| TS_ATTEND_CORRECT_CLOCK_RULE | 考勤修正规则 |
| TS_ATTEND_GROUP_SPECIAL_DAY | 考勤组特殊日期 |
| TS_ATTEND_GROUP_WORK_DAY | 考勤组工作日 |
| TS_ATTEND_OVERTIME_RULE | 加班规则 |
| TS_ATTEND_OVERTIME_RULE_DETAIL | 加班规则明细 |

### 数据连接器 (Dataconnector)
| 表名 | 中文含义 |
|------|---------|
| TS_DATACONNECTOR_FLUME_CONF | 数据连接器Flume配置 |
| TS_DATACONNECTOR_FLUME_LOG | 数据连接器Flume日志 |
| TS_DATACONNECTOR_MONITOR | 数据连接器监控 |

### 数据治理 (Datagov)
| 表名 | 中文含义 |
|------|---------|
| TS_DATAGOVERN_AUDIT_HIS | 数据治理审计历史 |
| TS_DATAGOVERN_AUDIT_RESULT | 数据治理审计结果 |
| TS_DATAGOVERN_AUDIT_TASK | 数据治理审计任务 |
| TS_DATAGOVERN_AUDIT_TASK_CONF | 数据治理审计任务配置 |
| TS_DATAGOVERN_DATA_STANDARD | 数据治理标准 |
| TS_DATAGOVERN_QUALITY_RULE | 数据治理质量规则 |
| TS_DATAGOVERN_RULE_PARAM | 数据治理规则参数 |

### 数据应用 (Datapp)
| 表名 | 中文含义 |
|------|---------|
| TS_DATAPP_AUTH_DEFINITION | 数据应用权限定义 |
| TS_DATAPP_BUTTON_ROLE | 数据应用按钮角色 |
| TS_DATAPP_COMPONENT_LIBRARY | 数据应用组件库 |
| TS_DATAPP_COMPONENT_ROLE | 数据应用组件角色 |
| TS_DATAPP_DATA_DIMENSION | 数据应用数据维度 |
| TS_DATAPP_OAUTH_ROLE | 数据应用OAuth角色 |
| TS_DATAPP_PAGEMAP_OPTCONFIG | 数据应用页面映射配置 |
| TS_DATAPP_PAGE_CONFIG_PHONE | 数据应用手机端页面配置 |
| TS_DATAPP_PAGE_MAPPING_CUST | 数据应用页面映射定制 |
| TS_DATAPP_PERMISSION_GROUP | 数据应用权限组 |
| TS_DATAPP_REMEMBER_OPERATION | 数据应用操作记忆 |
| TS_DATAPP_ROLE_DATA_DIMENSION | 数据应用角色数据维度 |

### 数据服务 (Dataservice)
| 表名 | 中文含义 |
|------|---------|
| TS_DATASERVICE_ACCESS_CONFIG | 数据服务访问配置 |
| TS_DATASERVICE_ACCESS_PARAM | 数据服务访问参数 |

### 详情 (Detail)
| 表名 | 中文含义 |
|------|---------|
| TS_DETAIL_CORRELATION_COLUMN | 详情关联列 |
| TS_DETAIL_DISPLAY_CONDITION | 详情显示条件 |
| TS_DETAIL_RESUME_INFO_COLUMN | 详情摘要信息列 |
| TS_DETAIL_SUBTABLE_DISPLAY | 详情子表显示配置 |

### 流程 (Flow)
| 表名 | 中文含义 |
|------|---------|
| TS_FLOW_COMPONENT_CONFIG_EXT | 流程组件扩展配置 |
| TS_FLOW_COMPONENT_CON_AUTH | 流程组件连接权限 |
| TS_FLOW_COMPONENT_CON_CONFIG | 流程组件连接配置 |
| TS_FLOW_COMPONENT_INSTANCE | 流程组件实例 |
| TS_FLOW_COMPONENT_ITEM_CONFIG | 流程组件项配置 |
| TS_FLOW_INSTANCE_APPROVAL_LOG | 流程实例审批日志 |

### 表单 (Form)
| 表名 | 中文含义 |
|------|---------|
| TS_FORM_COLUMN_REQUIRED_DETAIL | 表单字段必填明细 |
| TS_FORM_COMPONENT_CONFIG_EXT | 表单组件扩展配置 |
| TS_FORM_COMPONENT_DATASERVICE | 表单组件数据服务 |
| TS_FORM_VIEW_CANVAS_ELEMENT | 表单视图画布元素 |
| TS_FORM_VIEW_COLUMN_MAPPING | 表单视图字段映射 |
| TS_FORM_VIEW_CORRELATION_COL | 表单视图关联列 |
| TS_FORM_VIEW_DEFAULT_BUTTON | 表单视图默认按钮 |
| TS_FORM_VIEW_DETAIL_BUTTON | 表单视图详情按钮 |
| TS_FORM_VIEW_EXPORT_TEMPLATE | 表单视图导出模板 |

### 列表 (List)
| 表名 | 中文含义 |
|------|---------|
| TS_LIST_COLUMN_COMPONENT_PERMISSION | 列表列组件权限 |
| TS_LIST_COLUMN_ROLE_PERMISSION | 列表列角色权限 |
| TS_LIST_COLUMN_RULE_PERMISSION | 列表列规则权限 |
| TS_LIST_COMPONENT_DATA_SORT | 列表组件数据排序 |
| TS_LIST_COMPONENT_EXP_IMPORT | 列表组件导出导入 |
| TS_LIST_COMPONENT_QRY_COMBINED | 列表组件组合查询 |
| TS_LIST_COMPONENT_WIDTH | 列表组件宽度 |
| TS_LIST_CORRELATION_COLUMN | 列表关联列 |

### 其他 TS_ 表
| 表名 | 中文含义 |
|------|---------|
| TS_EXAMINATION_RESULT_DETAIL | 考试结果明细 |
| TS_EXT_PLUGIN_BEAN | 外部插件Bean |
| TS_PERMISSION_GROUP_ROLE | 权限组角色 |
| TS_REGISTER_BROWSER_RECORD | 注册浏览器记录 |
| TS_SCHEDULER_TASK_CONTROL_RECORD | 调度任务控制记录 |
| TS_SEARCHDESIGN_PARTICIPLE | 检索设计分词 |
| TS_SEARCHDESIGN_RELATEDWORDS | 检索设计关联词 |
| TS_SERVICE_API_TRANS_MAPPING | 服务API转换映射 |
| TS_SERVICE_ORCHESTRATION_ID_LOG | 服务编排ID日志 |
| TS_SERVICE_SUBSCRIBE_CONFIG | 服务订阅配置 |
| TS_SOURCE_COLLECTION_HISTORY | 数据源采集历史 |
| TS_SOURCE_COLLECTION_RESULT | 数据源采集结果 |
| TS_SYSHOME_HELP_CENTER | 系统主页帮助中心 |
| TS_SYSHOME_POSTER | 系统主页海报 |
| TS_VERSION_INSTALL_MAPPING | 版本安装映射 |
| TS_VERSION_INSTALL_MAPPING_DET | 版本安装映射明细 |

## 数睿核心业务表 (T_SDATA_)

### 应用与访问
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_ACCESSKEY | 访问密钥 |
| T_SDATA_APPROVAL | 审批 |
| T_SDATA_APPROVAL_AUTH | 审批权限 |
| T_SDATA_APP_BILL | 应用账单 |
| T_SDATA_APP_COMMENT | 应用评论 |
| T_SDATA_APP_DEFINITION_HISTORY | 应用定义历史 |
| T_SDATA_APP_DEFINITION_ORDER | 应用定义订单 |
| T_SDATA_APP_GROUP | 应用分组 |
| T_SDATA_APP_GROUP_OBJECT | 应用分组对象 |
| T_SDATA_APP_GROUP_USER | 应用分组用户 |
| T_SDATA_APP_INSTANT | 应用即时消息 |
| T_SDATA_APP_INTRODUCE_URL | 应用介绍链接 |
| T_SDATA_APP_RECENT | 最近使用应用 |
| T_SDATA_APP_THUMBSUP | 应用点赞 |
| T_SDATA_CUSTOM_APP | 自定义应用 |

### 资产 (Asset)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_ASSETCATA | 资产目录 |
| T_SDATA_ASSETCATA_GROUP | 资产目录分组 |
| T_SDATA_ASSETCATA_HISTORY | 资产目录历史 |
| T_SDATA_ASSETCATA_INFOS | 资产目录信息 |
| T_SDATA_ASSETCATA_OPTLOG | 资产目录操作日志 |
| T_SDATA_ASSETS_ASSOCIATIONS | 资产关联关系 |
| T_SDATA_ASSETS_DATALIST | 资产数据列表 |
| T_SDATA_ASSETS_FKREFS | 资产外键引用 |
| T_SDATA_ASSET_AUTH | 资产权限 |
| T_SDATA_ASSET_BATCH_AUTH | 资产批量授权 |
| T_SDATA_ASSET_DATA_ANALYSIS | 资产数据分析 |
| T_SDATA_ASSET_LIFE_CYCLE | 资产生命周期 |
| T_SDATA_ASSET_SYNREPORT | 资产同步报告 |
| T_SDATA_COMMON_ASSETS | 公共资产 |
| T_SDATA_GRAPH_ASSET_RELATION | 图谱资产关系 |

### 考勤 (Attendance)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_ATTENDANCE_DATE | 考勤日期 |
| T_SDATA_ATTENDANCE_FESTIVAL | 考勤节假日 |
| T_SDATA_ATTENDANCE_GROUP | 考勤组 |
| T_SDATA_ATTENDANCE_GROUP_FLOW | 考勤组流程 |
| T_SDATA_ATTENDANCE_GROUP_PLACE | 考勤组地点 |
| T_SDATA_ATTENDANCE_GROUP_RULE | 考勤组规则 |
| T_SDATA_ATTENDANCE_GROUP_USER | 考勤组用户 |
| T_SDATA_ATTENDANCE_GROUP_WIFI | 考勤组WiFi |
| T_SDATA_ATTENDANCE_LATE_RULE | 迟到规则 |
| T_SDATA_ATTENDANCE_RECORD | 考勤记录 |
| T_SDATA_ATTENDANCE_SHIFT | 考勤班次 |
| T_SDATA_ATTENDANCE_SHIFT_TIME | 考勤班次时间 |

### 大屏与仪表盘
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_BIGSCREEN | 大屏 |
| T_SDATA_BIGSCREEN_JUMP | 大屏跳转 |
| T_SDATA_DASHBOARD | 仪表盘 |
| T_SDATA_DASHBOARD_COMMENT | 仪表盘评论 |
| T_SDATA_DASHBOARD_META | 仪表盘元数据 |
| T_SDATA_DASHBOARD_META_HISTORY | 仪表盘元数据历史 |

### 控制流 (ControlFlow)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_CONTROLFLOW | 控制流 |
| T_SDATA_CONTROLFLOW_AUTH | 控制流权限 |
| T_SDATA_CONTROLFLOW_LOG | 控制流日志 |
| T_SDATA_CONTROLFLOW_NODELOG | 控制流节点日志 |
| T_SDATA_CONTROLFLOW_WARN | 控制流告警 |
| T_SDATA_CONTROLFLOW_WARN_TYPE | 控制流告警类型 |

### 数据市场 (Datamart)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DATAMART_BILL | 数据市场账单 |
| T_SDATA_DATAMART_DEFINITIONS | 数据市场定义 |
| T_SDATA_DATAMART_DETAILS | 数据市场明细 |
| T_SDATA_DATAMART_FAVORITE | 数据市场收藏 |
| T_SDATA_DATAMART_OBJECT | 数据市场对象 |
| T_SDATA_DATAMART_ORDER | 数据市场订单 |
| T_SDATA_DATAMART_TAGS | 数据市场标签 |
| T_SDATA_DATAMART_TIMES | 数据市场访问次数 |

### 数据应用 (Datapp)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DATAPP_ANNOTATION | 数据应用注释 |
| T_SDATA_DATAPP_BUTTON | 数据应用按钮 |
| T_SDATA_DATAPP_PAGE_BLOOD | 数据应用页面血缘 |
| T_SDATA_DATAPP_PAGE_CUSTOMIZE | 数据应用页面定制 |
| T_SDATA_DATAPP_PAGE_VARIABLE | 数据应用页面变量 |
| T_SDATA_DATAPP_RELATION | 数据应用关系 |

### 数据服务 (Dataservice)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DATASERVICE | 数据服务 |
| T_SDATA_DATASERVICE_AUTH | 数据服务权限 |
| T_SDATA_DATASERVICE_CONSUME | 数据服务消费 |
| T_SDATA_DATASERVICE_EXT_CONFIG | 数据服务扩展配置 |
| T_SDATA_DATASERVICE_LOG | 数据服务日志 |

### 数据交换 (Dataswitch)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DATASWITCH | 数据交换 |
| T_SDATA_DATASWITCH_CONF | 数据交换配置 |

### 详情 (Detail)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DETAIL_ARTICLE_CONFIG | 详情文章配置 |
| T_SDATA_DETAIL_BASIC_CONFIG | 详情基本配置 |
| T_SDATA_DETAIL_BUTTON | 详情按钮 |
| T_SDATA_DETAIL_CANVAS_CONFIG | 详情画布配置 |
| T_SDATA_DETAIL_COMMENT | 详情评论 |
| T_SDATA_DETAIL_COMPONENT | 详情组件 |
| T_SDATA_DETAIL_CORRELATION | 详情关联 |
| T_SDATA_DETAIL_EXPORT_TEMPLATE | 详情导出模板 |
| T_SDATA_DETAIL_PAGE_CONFIG | 详情页面配置 |
| T_SDATA_DETAIL_RESUME_CONFIG | 详情摘要配置 |

### 数据通 (DataTong)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DT_API | 数据通API |
| T_SDATA_DT_LIVING_CUSTOM_EVENT | 数据通自定义事件 |

### 考试 (Examination)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_EXAMINATION | 考试 |
| T_SDATA_EXAMINATION_BANK | 考试题库 |
| T_SDATA_EXAMINATION_CLASS | 考试班级 |
| T_SDATA_EXAMINATION_DETAIL | 考试明细 |
| T_SDATA_EXAMINATION_MANAGER | 考试管理 |
| T_SDATA_EXAMINATION_RESULT | 考试成绩 |
| T_SDATA_EXAMINATION_TEST | 考试试卷 |

### 流程 (Flow)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_FLOW_AUTH | 流程权限 |
| T_SDATA_FLOW_CATA | 流程分类 |
| T_SDATA_FLOW_COMPONENT | 流程组件 |
| T_SDATA_FLOW_COMPONENT_CON | 流程组件连接 |
| T_SDATA_FLOW_COMPONENT_CONFIG | 流程组件配置 |
| T_SDATA_FLOW_COMPONENT_ITEM | 流程组件项 |
| T_SDATA_FLOW_CONFIG | 流程配置 |
| T_SDATA_FLOW_DEFINITION | 流程定义 |
| T_SDATA_FLOW_INSTANCE | 流程实例 |
| T_SDATA_FLOW_INSTANCE_TASK | 流程实例任务 |

### 表单 (Form)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_FORM_ASSET_COLUMN | 表单资产列 |
| T_SDATA_FORM_BUTTON | 表单按钮 |
| T_SDATA_FORM_CHILD | 表单子表 |
| T_SDATA_FORM_CHILD_BUTTON | 表单子表按钮 |
| T_SDATA_FORM_COLUMN | 表单字段列 |
| T_SDATA_FORM_COLUMN_LINK | 表单字段链接 |
| T_SDATA_FORM_COLUMN_MAPPING | 表单字段映射 |
| T_SDATA_FORM_COLUMN_MULTIPLE | 表单多选列 |
| T_SDATA_FORM_COLUMN_STYLE | 表单字段样式 |
| T_SDATA_FORM_COMMENT | 表单评论 |
| T_SDATA_FORM_COMPONENT_CONFIG | 表单组件配置 |
| T_SDATA_FORM_CORRELATION | 表单关联 |
| T_SDATA_FORM_DATA_ATTR | 表单数据属性 |
| T_SDATA_FORM_DATA_TEMP | 表单临时数据 |
| T_SDATA_FORM_EXT | 表单扩展 |
| T_SDATA_FORM_JOINT_SEARCH | 表单联合搜索 |
| T_SDATA_FORM_LOG | 表单日志 |
| T_SDATA_FORM_MANDATORY_COLUMN | 表单必填列 |
| T_SDATA_FORM_READ_PROCESS | 表单阅读流程 |
| T_SDATA_FORM_SERIAL_NUM | 表单流水号 |
| T_SDATA_FORM_VIEW_APPEND | 表单视图追加 |
| T_SDATA_FORM_VIEW_AUTH | 表单视图权限 |
| T_SDATA_FORM_VIEW_BUTTON | 表单视图按钮 |
| T_SDATA_FORM_VIEW_CANVAS | 表单视图画布 |
| T_SDATA_FORM_VIEW_COLUMN | 表单视图列 |
| T_SDATA_FORM_VIEW_CONDITION | 表单视图条件 |
| T_SDATA_FORM_VIEW_CONFIG | 表单视图配置 |
| T_SDATA_FORM_VIEW_CONFIG_PLUS | 表单视图高级配置 |
| T_SDATA_FORM_VIEW_CORRELATION | 表单视图关联 |
| T_SDATA_FORM_VIEW_DISPLAY | 表单视图显示 |
| T_SDATA_FORM_VIEW_FILTER | 表单视图筛选 |
| T_SDATA_FORM_VIEW_MODE_COLUMN | 表单视图模式列 |
| T_SDATA_FORM_VIEW_ORDER | 表单视图排序 |
| T_SDATA_FORM_VIEW_PROCESS | 表单视图流程 |
| T_SDATA_FORM_VIEW_VARIABLE | 表单视图变量 |

### 列表 (List)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_LIST_CALENDAR | 列表日历视图 |
| T_SDATA_LIST_CANVAS | 列表画布 |
| T_SDATA_LIST_CANVAS_CARD | 列表画布卡片 |
| T_SDATA_LIST_CANVAS_INFO | 列表画布信息 |
| T_SDATA_LIST_CANVAS_LIST | 列表画布列表 |
| T_SDATA_LIST_CARD | 列表卡片 |
| T_SDATA_LIST_CATALOG | 列表目录 |
| T_SDATA_LIST_COMPONENT_SORT | 列表组件排序 |
| T_SDATA_LIST_CORRELATION | 列表关联 |
| T_SDATA_LIST_CUSTOMIZE | 列表定制 |
| T_SDATA_LIST_FILTER | 列表筛选 |
| T_SDATA_LIST_FILTER_CUSTOM | 列表自定义筛选 |
| T_SDATA_LIST_INFORMATION | 列表信息 |
| T_SDATA_LIST_PROCESS | 列表流程 |
| T_SDATA_LIST_TIMELINE | 列表时间线 |
| T_SDATA_LIST_WATCHBOARD | 列表看板 |

### 质量 (Quality)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_QA_REPORT | 质量报告 |
| T_SDATA_QA_SOLR | 质量Solr索引 |
| T_SDATA_QUALITYTASK | 质量任务 |
| T_SDATA_QUALITYTASK_COLDATA | 质量任务列数据 |
| T_SDATA_QUALITYTASK_LOG | 质量任务日志 |
| T_SDATA_QUALITYTASK_MAPPING | 质量任务映射 |
| T_SDATA_QUALITYTASK_TABLEDATA | 质量任务表数据 |
| T_SDATA_QUALITY_RULES | 质量规则 |

### 检索 (Search)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_FULLSEARCH_HISTORY | 全文搜索历史 |
| T_SDATA_SEARCHDESIGN | 检索设计 |
| T_SDATA_SEARCHDESIGN_SYNONYM | 检索设计同义词 |
| T_SDATA_SEARCHUNIT | 检索单元 |
| T_SDATA_SEARCH_DICT_HEAT | 搜索词典热度 |
| T_SDATA_SEARCH_DICT_RELEVANCE | 搜索词典相关性 |
| T_SDATA_SEARCH_DICT_SYNONYM | 搜索词典同义词 |
| T_SDATA_SEARCH_DICT_TERM | 搜索词典词条 |
| T_SDATA_SEARCH_ENGINE | 搜索引擎 |
| T_SDATA_SEARCH_ENGINE_AUTH | 搜索引擎权限 |
| T_SDATA_DS_SEARCH_ENGINE | 数据源搜索引擎 |

### 版本 (Version)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_VERSION_ARCHIVE | 版本归档 |
| T_SDATA_VERSION_DETAIL | 版本明细 |
| T_SDATA_VERSION_PACKAGE_V3 | 版本包（V3） |
| T_SDATA_VERSION_USER_MAPPING | 版本用户映射 |

### 其他 T_SDATA_ 表
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_ANALYSIS_RAIL | 分析轨迹 |
| T_SDATA_ANALYSIS_REFS | 分析引用 |
| T_SDATA_ANALYSIS_RULES | 分析规则 |
| T_SDATA_ANALYSIS_RULES_CON | 分析规则条件 |
| T_SDATA_ANALYSIS_RULES_HISTORY | 分析规则历史 |
| T_SDATA_API_TRANS | API转换 |
| T_SDATA_API_TRANS_LOG | API转换日志 |
| T_SDATA_API_TRANS_MAPPING | API转换映射 |
| T_SDATA_CHAPTER_TEMPLATE | 章节模板 |
| T_SDATA_CLUSTER_CONF | 集群配置 |
| T_SDATA_COMMON_STRUCTURES | 公共结构 |
| T_SDATA_COMPONENT_RELATION | 组件关系 |
| T_SDATA_CONNECTOR_INCREMENT | 连接器增量 |
| T_SDATA_COOPERATION | 协作 |
| T_SDATA_CUSTOM_SERVICE | 自定义服务 |
| T_SDATA_DATACONNECTOR_RULE | 数据连接器规则 |
| T_SDATA_DATACONNECTOR_RULE_CONF | 数据连接器规则配置 |
| T_SDATA_DATAEXTRACTOR | 数据抽取器 |
| T_SDATA_DATAFLOW_IO_METRICS | 数据流IO指标 |
| T_SDATA_DATAFLOW_NODE_CONF | 数据流节点配置 |
| T_SDATA_DATAREPORTING | 数据填报 |
| T_SDATA_DISCOUNT | 折扣 |
| T_SDATA_DISCOUNT_DETAIL | 折扣明细 |
| T_SDATA_ENTER_HISTORY | 入库历史 |
| T_SDATA_ENTER_RULE | 入库规则 |
| T_SDATA_EXTERNAL_USER | 外部用户 |
| T_SDATA_EXTPROGRAM | 外部程序 |
| T_SDATA_EXTPROGRAM_LOG | 外部程序日志 |
| T_SDATA_FAVORITES | 收藏 |
| T_SDATA_FEEDBACK | 反馈 |
| T_SDATA_HOUSEHOLDER | 户长（负责人员） |
| T_SDATA_INFO_BUTTON | 信息按钮 |
| T_SDATA_INFO_MANAGE | 信息管理 |
| T_SDATA_INVITE_LOG | 邀请日志 |
| T_SDATA_LICENSE_REPORT | License报告 |
| T_SDATA_LINEAGE_ITEM | 血缘项目 |
| T_SDATA_LINEAGE_MONITOR | 血缘监控 |
| T_SDATA_LOGIC | 逻辑 |
| T_SDATA_MODEL | 模型 |
| T_SDATA_MODEL_ASSET_AUTH | 模型资产权限 |
| T_SDATA_MODEL_RELATION | 模型关系 |
| T_SDATA_NOTIFY | 消息通知 |
| T_SDATA_PRIVACY_APPROVE | 隐私审批 |
| T_SDATA_PRIVILEGE | 权限 |
| T_SDATA_QUICK_NEWS | 快捷资讯 |
| T_SDATA_REALTIMESTREAM_DEFINITIONS | 实时流定义 |
| T_SDATA_RECOMMEND_CODE | 推荐码 |
| T_SDATA_SCHEDULER_PROPERTY | 调度器属性 |
| T_SDATA_SCHEDULE_CON | 调度连接 |
| T_SDATA_SECRETKEY | 密钥 |
| T_SDATA_SECURITY_DEFINITION | 安全定义 |
| T_SDATA_SERVICE_API_TRANS | 服务API转换 |
| T_SDATA_SERVICE_API_TRANS_LOG | 服务API转换日志 |
| T_SDATA_SOURCE_COLLECTION_RULE | 数据源采集规则 |
| T_SDATA_SSO_SECRET_INFO | SSO密钥信息 |
| T_SDATA_STANDARD_MAPPING | 标准映射 |
| T_SDATA_STYLE | 样式 |
| T_SDATA_STYLE_PROPERTY | 样式属性 |
| T_SDATA_SYSTEM_CLUSTER | 系统集群 |
| T_SDATA_SYSTEM_CLUSTER_SYNC | 系统集群同步 |
| T_SDATA_TEMPLATE | 模板 |
| T_SDATA_THEME_COMPONENT_STYLE | 主题组件样式 |
| T_SDATA_THIRDPARTYLOGIN | 第三方登录 |
| T_SDATA_THIRDPARTY_INTF_LOG | 第三方接口日志 |
| T_SDATA_TRIGGERS | 触发器 |
| T_SDATA_USER_MAPPING_RULE | 用户映射规则 |
| T_SDATA_VIDEO_SOURCES | 视频源 |
| T_SDATA_WARNING | 告警 |
| T_SDATA_WX_USER | 微信用户 |
