from django.shortcuts import render
from django.http import JsonResponse
from .models import Movie, Genre, Director, Actor, ProductionCompany
from pyecharts.charts import Bar, Pie, Line, Map, WordCloud, Scatter, HeatMap
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import json
import re

def index(request):
    # 生成所有图表
    genre_pie = create_genre_pie()
    year_revenue_line_option = create_year_revenue_line()
    director_bar = create_director_bar()
    vote_distribution = create_vote_distribution()
    company_wordcloud = create_company_wordcloud()
    budget_revenue_scatter = create_budget_revenue_scatter()
    
    # 将图表转换为JSON字符串
    context = {
        'genre_pie': genre_pie.dump_options(),
        'year_revenue_line': json.dumps(year_revenue_line_option),
        'director_bar': director_bar.dump_options(),
        'vote_distribution': vote_distribution.dump_options(),
        'company_wordcloud': company_wordcloud.dump_options(),
        'budget_revenue_scatter': budget_revenue_scatter.dump_options(),
    }
    
    return render(request, 'index.html', context)

def create_genre_pie():
    genres = Genre.objects.all()
    pie = (
        Pie(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add(
            "电影数量",
            [list(z) for z in zip([g.name for g in genres], [g.movies.count() for g in genres])],
            radius=["40%", "75%"],
            label_opts=opts.LabelOpts(is_show=False)
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="电影类型分布"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_right="10%"),
            tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)")
        )
    )
    return pie

def create_year_revenue_line():
    movies = Movie.objects.all().order_by('release_date')
    
    # 新增：按年份汇总票房
    year_revenue_map = {}
    for movie in movies:
        if movie.release_date and movie.revenue is not None:
            year = movie.release_date.year
            # 确保revenue是数字类型再进行累加
            try:
                revenue = int(movie.revenue)
                if year in year_revenue_map:
                    year_revenue_map[year] += revenue
                else:
                    year_revenue_map[year] = revenue
            except (ValueError, TypeError):
                # 如果revenue不是有效的数字，跳过此条数据
                continue

    # 将汇总数据转换为按年份排序的列表
    sorted_years = sorted(year_revenue_map.keys())
    sorted_revenues = [year_revenue_map[year] for year in sorted_years]

    print("Year Revenue Data (Aggregated):", list(zip(sorted_years, sorted_revenues))) # 更新打印输出

    years = sorted_years # 使用汇总后的唯一年份作为X轴数据
    revenues = sorted_revenues # 使用汇总后的总票房作为Y轴数据

    # 1. 使用柱状图先生成 Option，因为柱状图能正常显示数据
    bar_chart = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(years)
        .add_yaxis("年度票房", revenues,
                   label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="年度票房趋势"),
            xaxis_opts=opts.AxisOpts(name="年份", type_="category", axislabel_opts=opts.LabelOpts(rotate=45)),
            yaxis_opts=opts.AxisOpts(name="票房（美元）", type_="value"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow")
        )
    )

    # 2. 获取生成的 Option 字典
    line_option = json.loads(bar_chart.dump_options())

    # 3. 修改 Option 字典，将其系列类型改为 'line' 并调整相关配置
    if line_option and line_option.get("series"):
        # 假设只有一个系列需要修改
        series_opts = line_option["series"][0]

        # 将系列类型改为 line
        series_opts["type"] = "line"

        # 将 Python 的 True 转换为 JSON 的 true
        series_opts["smooth"] = True

        # 在category轴下，Line的series数据应该是纯Y值，而不是[[x,y]]
        # 然而PyechartsBar生成的是纯Y值，这里我们不需要额外处理data格式

        # 调整tooltip的axisPointer type，Line图通常用'line'
        if line_option.get("tooltip") and line_option["tooltip"].get("axisPointer"):
             line_option["tooltip"]["axisPointer"]["type"] = "line"

    # 4. 返回修改后的 Option 字典
    return line_option

def create_director_bar():
    directors = Director.objects.all()
    director_revenue = []
    for director in directors:
        total_revenue = sum(movie.revenue for movie in director.movies.all())
        director_revenue.append((director.name, total_revenue))
    director_revenue.sort(key=lambda x: x[1], reverse=True)
    director_revenue = director_revenue[:10]
    
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis([x[0] for x in director_revenue])
        .add_yaxis("票房", [x[1] for x in director_revenue],
                   label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="导演票房排行"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            yaxis_opts=opts.AxisOpts(name="票房（美元）"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow")
        )
    )
    return bar

def create_vote_distribution():
    movies = Movie.objects.all()
    vote_ranges = {
        '0-2': 0,
        '2-4': 0,
        '4-6': 0,
        '6-8': 0,
        '8-10': 0
    }
    for movie in movies:
        vote = movie.vote_average
        if vote < 2:
            vote_ranges['0-2'] += 1
        elif vote < 4:
            vote_ranges['2-4'] += 1
        elif vote < 6:
            vote_ranges['4-6'] += 1
        elif vote < 8:
            vote_ranges['6-8'] += 1
        else:
            vote_ranges['8-10'] += 1
    
    bar = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis(list(vote_ranges.keys()))
        .add_yaxis("电影数量", list(vote_ranges.values()),
                   label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="评分分布"),
            xaxis_opts=opts.AxisOpts(name="评分区间"),
            yaxis_opts=opts.AxisOpts(name="电影数量"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow")
        )
    )
    return bar

def create_company_wordcloud():
    companies = ProductionCompany.objects.all()
    company_data = []
    for company in companies:
        count = company.movies.count()
        if count > 0 and company.name:
            company_data.append({
                'name': company.name[:20],  # 限制名称长度
                'value': count  # 直接使用电影数量
            })
    
    # 只取前30个公司
    company_data.sort(key=lambda x: x['value'], reverse=True)
    company_data = company_data[:30]
    
    # 如果没有数据，使用默认值
    if not company_data:
        company_data = [{'name': '无数据', 'value': 1}]
    
    # 使用词云图
    wordcloud = (
        WordCloud(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add(
            series_name="",
            data_pair=[(x['name'], x['value']) for x in company_data]
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="制作公司分布"),
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                formatter="{b}: {c} 部电影"
            )
        )
        .set_series_opts(
            word_size_range=[15, 70], # 调整大小范围
            rotation_range=[0, 0], # 不旋转
            grid_size=10, # 调整网格大小
            textstyle_opts=opts.TextStyleOpts(font_family="Microsoft YaHei"),
            shape="circle"
        )
    )
    return wordcloud

def create_budget_revenue_scatter():
    movies = Movie.objects.all()
    data = []
    for movie in movies:
        if movie.budget > 0 and movie.revenue > 0:  # 只处理有效的预算和票房数据
            data.append([movie.budget, movie.revenue])
    
    scatter = (
        Scatter(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis([x[0] for x in data])
        .add_yaxis("预算-票房关系", [x[1] for x in data],
                   label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="预算与票房关系"),
            xaxis_opts=opts.AxisOpts(
                name="预算（美元）",
                type_="log"  # 使用对数坐标轴
            ),
            yaxis_opts=opts.AxisOpts(
                name="票房（美元）",
                type_="log"  # 使用对数坐标轴
            ),
            tooltip_opts=opts.TooltipOpts(trigger="item", formatter="预算: ${a}<br/>票房: ${c}")
        )
    )
    return scatter
