# 新增表名翻译映射（2026-07-15 会话）

本次新增翻译映射来自 DASHBOARD.xlsx 的 Sheet1（45 个 T_SDATA_* 表名）
和 SHANGHAI_AREA_BUSINESS sheet（21 个 DW_* 表名 + INFO_* 表名）。

## ACT_HI_ 补充

| 表名 | 中文含义 |
|------|---------|
| ACT_HI_ACTINST | 历史活动实例 |

## TS_ 补充（数据应用角色）

| 表名 | 中文含义 |
|------|---------|
| TS_DATAPP_ROLE | 数据应用角色 |
| TS_DATAPP_ROLE_MENU | 数据应用角色菜单 |
| TS_SERVICE_ORCHESTRATION | 服务编排 |
| TS_SERVICE_ORCHESTRATION_ID_LOG | 服务编排ID日志 |

## T_SDATA_ 新增（来自新 DASHBOARD 文件的 45 张表）

### 应用定义
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_APP_DEFINITION | 应用定义 |
| T_SDATA_APP_DEFINITION_EXTENSION | 应用定义扩展 |

### 大屏与仪表盘
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DASHBOARD_CARD | 仪表盘卡片 |
| T_SDATA_DASHBOARD_CARD_DEFINITION | 仪表盘卡片定义 |
| T_SDATA_DASHBOARD_TEMPLATE | 仪表盘模板 |
| T_SDATA_DASHBOARD_WARN | 仪表盘告警 |
| T_SDATA_BIGSCREEN_PAGE | 大屏页面 |

### 数据连接器
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DATACONNECTOR | 数据连接器 |
| T_SDATA_DATACONNECTOR_BOOTSTRAP | 数据连接器启动配置 |
| T_SDATA_DATACONNECTOR_CONF | 数据连接器配置 |
| T_SDATA_DATACONNECTOR_OWNCONF | 数据连接器自有配置 |
| T_SDATA_DATACONNECTOR_RUN_LOG | 数据连接器运行日志 |

### 数据应用
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DATAPP_MENU | 数据应用菜单 |
| T_SDATA_DATAPP_MENU_BUTTON | 数据应用菜单按钮 |
| T_SDATA_DATAPP_PAGE | 数据应用页面 |
| T_SDATA_DATAPP_PAGE_DEFINITION | 数据应用页面定义 |

### 数据服务
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_DATASERVICE_DEFINITION | 数据服务定义 |
| T_SDATA_DATASERVICE_GROUP | 数据服务组 |

### 消息通知
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_MESSAGE_CODE | 消息编码 |
| T_SDATA_MESSAGE_TEMPLATE | 消息模板 |
| T_SDATA_MESSAGE_TEMPLATE_CONF | 消息模板配置 |

### 文件与存储
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_FILE | 文件 |
| T_SDATA_FILE_CATEGORY | 文件分类 |

### 流程
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_FLOW_CONF | 流程配置（补充） |
| T_SDATA_FLOW_TRIGGER | 流程触发器 |

### 表单 (补充)
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_FORM_GROUP | 表单分组 |

### 其他新增
| 表名 | 中文含义 |
|------|---------|
| T_SDATA_COMPRESS | 压缩配置 |
| T_SDATA_DATA_QUERY | 数据查询 |
| T_SDATA_DATAGROUP | 数据分组 |
| T_SDATA_DATAREPORTING_EXCEL | 数据填报Excel模板 |
| T_SDATA_DIC_CACHE | 字典缓存 |
| T_SDATA_DOCUMENT | 文档 |
| T_SDATA_DOCUMENT_CATEGORY | 文档分类 |
| T_SDATA_DOCUMENT_TEMPLATE | 文档模板 |
| T_SDATA_ETL | ETL数据转换 |
| T_SDATA_EXCEL_ANALYSIS | Excel分析 |
| T_SDATA_EXCEPTION_LOG | 异常日志 |
| T_SDATA_FUNCTION | 函数 |
| T_SDATA_FUNCTION_PARAM | 函数参数 |
| T_SDATA_LINEAGE_QUERY | 血缘查询 |
| T_SDATA_LINEAGE_RELATION | 血缘关系 |
| T_SDATA_MONGO_TEMPLATE | Mongo模板 |
| T_SDATA_OPERATION_LOG | 操作日志 |
| T_SDATA_ORGANIZATION | 组织架构 |
| T_SDATA_RESOURCE | 资源 |
| T_SDATA_RESOURCE_FILE | 资源文件 |
| T_SDATA_SMART_AGENT | 智能助手 |
| T_SDATA_WORKFLOW | 工作流 |

## DW_ 前缀（数据仓库层）

完整翻译自 SHANGHAI_AREA_BUSINESS sheet（21 张唯一表名）。

### 基础设施 (DW_INFRA_)
| 表名 | 中文含义 |
|------|---------|
| DW_INFRA_CLUSTER | 基础设施集群 |
| DW_INFRA_CLUSTER_NODE | 基础设施集群节点 |
| DW_INFRA_DATABASE | 基础设施数据库 |
| DW_INFRA_GPU | 基础设施GPU资源 |
| DW_INFRA_TOPOLOGY | 基础设施拓扑 |
| DW_INFRA_TOPOLOGY_REL | 基础设施拓扑关系 |

### 算法资源 (DW_ALGO_)
| 表名 | 中文含义 |
|------|---------|
| DW_ALGO_ALLOCATED_RESOURCE | 算法分配资源 |
| DW_ALGO_SERVICE_STATUS | 算法服务状态 |
| DW_ALGO_UTILIZATION_RATE | 算法资源利用率 |
| DW_ALGO_VIDEO_STRUCTURED_TASK | 算法视频结构化任务 |
| DW_ALGO_VIDEO_STRUCTURED_TASK_RESPATH | 算法视频结构化任务结果路径 |

### 视频算法 (DW_VIDEO_ALGO_)
| 表名 | 中文含义 |
|------|---------|
| DW_VIDEO_ALGO_STAT | 视频算法统计分析 |
| DW_VIDEO_ALGO_STAT_TASK_DETAIL | 视频算法统计任务明细 |
| DW_VIDEO_ALGO_TASK_RESOURCE | 视频算法任务资源 |

### API 调用 (DW_API_)
| 表名 | 中文含义 |
|------|---------|
| DW_API_CALL_STAT | API调用统计 |
| DW_API_CALL_STAT_BY_API | API调用统计（按API） |
| DW_API_CALL_STAT_BY_APP | API调用统计（按应用） |
| DW_API_CALL_STAT_BY_DATE | API调用统计（按日期） |
| DW_API_CALL_STAT_BY_USER | API调用统计（按用户） |

### 容器与告警
| 表名 | 中文含义 |
|------|---------|
| DW_CPRT_CONSOLE | 容器控制台 |
| DW_ALARM_INFO | 告警信息 |
| DW_ALARM_INFO_TEMPLATE | 告警信息模板 |

## INFO_ 前缀（算法服务部署信息）

| 表名 | 中文含义 |
|------|---------|
| INFO_ALGORITHM_SERVICE_DEPLOYMENT | 算法服务部署信息 |
