# 全球电影数据分析大屏可视化系统

## 项目简介

本项目是一个基于 Python 的全球电影数据分析大屏可视化系统，通过数据可视化技术展示全球电影市场的发展趋势、票房分布、类型偏好等信息。

## 技术栈

- 后端：Django + Python
- 数据可视化：Pyecharts
- 数据库：MySQL
- 前端：HTML + CSS + JavaScript

## 功能特点

1. 全球电影票房分布地图展示
2. 电影类型占比分析
3. 年度票房趋势分析
4. 导演/演员影响力分析
5. 电影评分分布分析
6. 电影制作成本与票房关系分析
7. 电影关键词词云展示

## 安装说明

1. 克隆项目到本地
2. 安装依赖：`pip install -r requirements.txt`
3. 配置数据库连接
4. 运行数据库迁移：`python manage.py migrate`
5. 启动开发服务器：`python manage.py runserver`

## 项目结构

```
project_final/
├── movie_analysis/          # Django项目主目录
├── static/                  # 静态文件
├── templates/              # HTML模板
├── data/                   # 数据文件
├── requirements.txt        # 项目依赖
└── README.md              # 项目说明
```

## 数据来源

- IMDB 电影数据库
- The Movie Database (TMDB) API
- Box Office Mojo 票房数据

## 贡献者

[待添加]

## 许可证

MIT License
