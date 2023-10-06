# SHU24hSpaceInfo
看看是谁又在24小时自习空间卷哦

## Feature

- 查看座位上的人什么时候开始卷，卷到什么时候
- 查看座位上是谁在卷
- 查看谁接下来预订了座位
- 查看某一时间段哪些座位空着
- 查看座位预定历史
- 预约座位

## Quick Start

### Requirements

```bash
python -m pip install -r requirements.txt
```

### Run the Script

```bash
python main.py
```

### Example task script (for crontab)

```
python exampletask.py
```

## Notice

- 本脚本仅供学习使用，请勿用于任何非法行为

- 使用该脚本的一切后果自负，使用该脚本代表你承诺遵守《图书馆24H学习空间管理办法》，自觉维护公共学习空间秩序

- 运行该脚本时会尝试读取`session.db`以避免重复登录的开销，若session无效会提示重新登录
