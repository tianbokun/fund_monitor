# 基金限购监控APP

一款用于监控中国大陆投资基金每日限购额的Android应用。

## 功能特性

- ✅ 监控基金日限购额
- ✅ 实时查看申购状态
- ✅ 基金代码搜索
- ✅ 数据自动刷新
- ✅ 本地数据持久化

## 安装使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行调试

```bash
python main.py
```

### 3. 构建Android APK

```bash
flet build apk --platform android
```

## 项目结构

```
fund_monitor_app/
├── main.py              # 应用入口
├── lib/
│   ├── fund_service.py    # 基金数据服务
│   └── components.py    # UI组件
├── requirements.txt    # 依赖
└── README.md
```

## 技术栈

- **UI框架**: Flet (Flutter for Python)
- **数据源**: AkShare (东方财富/天天基金)
- **目标平台**: Android/iOS/Web

## 数据API说明

数据来源于东方财富天天基金网:
- 接口: fund_purchase_em()
- 字段: 日累计限定金额, 申购状态, 赎回状态等

> 注意: 限额数据仅为参考，实际以基金公司公告为准。