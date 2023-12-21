CREATE TABLE `ct_dljg_list` (
  `@key` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'id',
  `agencyname` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '机构名称',
  `agencycode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '机构代码',
  `postcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '邮编',
  `email` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '邮箱',
  `principal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '负责人',
  `phone` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '联系电话',
  `createdate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '设立日期',
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '地址',
  `zynum` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '执业代理师人数',
  `status` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '状态'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE `ct_dljg_fz` (
  `agencyname` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '机构名称',
  `@key` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'id',
  `@rowid` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '列id',
  `branchname` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '分支机构名称',
  `branchcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '分支机构代码',
  `principal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '负责人',
  `agent` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '代理师',
  `phone` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '联系电话',
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '分支机构地址',
  `id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'id'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='分支机构设置情况';

CREATE TABLE `ct_dljg` (
  `agencyname` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '机构名称',
  `agencycode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '机构代码',
  `principal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '负责人',
  `parter` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '合伙人/股东/设立人',
  `doublecert` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '双证人员',
  `phone` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '联系电话',
  `fax` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '传真',
  `agencyurl` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '网址',
  `email` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '邮箱',
  `postcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '邮编',
  `status` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '机构状态',
  `agent` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '代理师',
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '地址',
  `isgzcn` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '申请机构执业许可的办理方式',
  `tyshxycode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '统一社会信用代码'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='专利代理机构基本信息';

CREATE TABLE `ct_dls_list` (
  `@key` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'id',
  `name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '姓名',
  `sex` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '性别',
  `birthdate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '出生日期',
  `certificate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '执业备案号',
  `qualificationcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '资格证号',
  `agencycode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '机构代码',
  `cmajor` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '专业',
  `id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'id',
  `localoffice` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '办事处',
  `cnkeyword` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '中文关键词"',
  `status` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci

CREATE TABLE `ct_dls_detail` (
  `name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '姓名',
  `sex` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '性别',
  `birthdate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '出生年月',
  `nationality` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '民族',
  `cardtype` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '证件类型',
  `no` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '证件号码',
  `education` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '学历',
  `cmajor` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '专业',
  `ispartner` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '是否合伙人/股东',
  `certificate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '执业备案号',
  `qualificationcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '资格证号',
  `foreignlanuage` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '外语语种',
  `qualificationtype` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '资格证类型',
  `otherqualification` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '其他资格',
  `qualifydate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '领取资格证时间',
  `firstbusinessdate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '首次执业时间',
  `phone` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '电话',
  `postcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '邮编',
  `houseraddress` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '家庭地址',
  `filesplace` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '档案存放地',
  `filesunit` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '档案存放单位',
  `filesunitlinkman` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '档案存放单位联系人',
  `filesunitphone` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '档案存放单位联系电话',
  `isretire` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '是否退休',
  `retiredate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '退休时间',
  `retireunit` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '退休单位',
  `agencyname` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '所在专利代理机构名称',
  `agencycode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '所在专利代理机构代码',
  `agencypostcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '所在专利代理机构邮编',
  `agencyaddress` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '所在专利代理机构地址',
  `agencyphone` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '所在专利代理机构电话',
  `agenttime` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '代理师累计执业年限',
  `isdlrcy` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '是否可以执业'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE `ct_dls_work` (
  `person_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '代理师id',
  `@key` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '编号id',
  `workstartdate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '工作开始时间',
  `workenddate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '工作结束时间',
  `workunit` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '工作单位',
  `workduty` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '职务',
  `workid` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '工作id',
  `id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '代理师id'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ct_dls_zybalist` (
  `person_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '代理师id',
  `@key` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'id',
  `workstartdate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '执业开始时间',
  `workenddate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '执业结束时间',
  `workunit` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '执业机构',
  `workduty` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '职务',
  `zybaid` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '编号顺序'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci

CREATE TABLE `ct_dls_education` (
  `person_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '代理师id',
  `@key` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'id',
  `studystartdate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '学习开始时间',
  `studyenddate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '学习结束时间',
  `studyunit` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '学习单位',
  `degree` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '学位',
  `eduid` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '学位id',
  `id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '代理师id'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `ct_fzjg_list` (
  `@key` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'id',
  `agencycode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '主机构代码',
  `branchname` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '分支机构名称',
  `branchcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '分支机构代码',
  `principal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '负责人',
  `localoffice` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '所属地方局',
  `createdate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '设立日期',
  `postcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '邮编',
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '地址',
  `phone` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '电话',
  `agent` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '代理师',
  `status` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '状态',
  `id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT 'id'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='分支机构信息列表';