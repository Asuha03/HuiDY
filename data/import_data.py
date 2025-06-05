import os
import json
import django
import sys
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_analysis.settings')
django.setup()

from movie_dashboard.models import Movie, Genre, Director, Actor, ProductionCompany

def import_movie_data(json_file):
    """从JSON文件导入电影数据"""
    with open(json_file, 'r', encoding='utf-8') as f:
        movies_data = json.load(f)
    
    for movie_data in movies_data:
        # 创建或更新电影
        movie, created = Movie.objects.update_or_create(
            title=movie_data['title'],
            defaults={
                'release_date': datetime.strptime(movie_data['release_date'], '%Y-%m-%d').date(),
                'budget': movie_data['budget'],
                'revenue': movie_data['revenue'],
                'runtime': movie_data['runtime'],
                'vote_average': movie_data['vote_average'],
                'vote_count': movie_data['vote_count'],
                'overview': movie_data['overview'],
                'poster_path': movie_data['poster_path']
            }
        )
        
        # 处理电影类型
        for genre_data in movie_data['genres']:
            genre, _ = Genre.objects.get_or_create(name=genre_data['name'])
            movie.genres.add(genre)
        
        # 处理导演
        if 'credits' in movie_data and 'crew' in movie_data['credits']:
            for crew_member in movie_data['credits']['crew']:
                if crew_member['job'] == 'Director':
                    director, _ = Director.objects.get_or_create(name=crew_member['name'])
                    movie.directors.add(director)
        
        # 处理演员（只取前5个主要演员）
        if 'credits' in movie_data and 'cast' in movie_data['credits']:
            for cast_member in movie_data['credits']['cast'][:5]:
                actor, _ = Actor.objects.get_or_create(name=cast_member['name'])
                movie.actors.add(actor)
        
        # 处理制作公司
        for company_data in movie_data['production_companies']:
            company, _ = ProductionCompany.objects.get_or_create(
                name=company_data['name'],
                defaults={'country': company_data.get('origin_country', '')}
            )
            movie.production_companies.add(company)
        
        print(f"已导入电影: {movie.title}")

def main():
    # 获取最新的数据文件
    data_dir = os.path.join(project_root, 'data', 'raw')
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    if not json_files:
        print("未找到数据文件")
        return
    
    latest_file = max(json_files, key=lambda x: os.path.getctime(os.path.join(data_dir, x)))
    json_file = os.path.join(data_dir, latest_file)
    
    print(f"正在从 {json_file} 导入数据...")
    import_movie_data(json_file)
    print("数据导入完成")

if __name__ == '__main__':
    main() 