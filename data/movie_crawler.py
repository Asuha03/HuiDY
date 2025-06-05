import requests
import json
import time
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 加载环境变量
load_dotenv()

# TMDB API配置
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def get_movie_details(movie_id):
    """获取电影详细信息"""
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'zh-CN',
        'append_to_response': 'credits'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取电影 {movie_id} 详情时出错: {e}")
        return None

def get_popular_movies(page=1):
    """获取热门电影列表"""
    url = f"{TMDB_BASE_URL}/movie/popular"
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'zh-CN',
        'page': page
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取热门电影列表时出错: {e}")
        return None

def save_movie_data(movie_data, filename):
    """保存电影数据到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(movie_data, f, ensure_ascii=False, indent=2)

def main():
    # 创建数据目录
    data_dir = os.path.join(project_root, 'data', 'raw')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # 获取热门电影列表
    movies_data = []
    for page in range(1, 26):  # 获取25页数据，每页20部电影
        print(f"正在获取第 {page} 页电影...")
        popular_movies = get_popular_movies(page)
        
        if not popular_movies:
            continue
        
        for movie in popular_movies['results']:
            movie_id = movie['id']
            print(f"正在获取电影 {movie_id} 的详细信息...")
            
            movie_details = get_movie_details(movie_id)
            if movie_details:
                movies_data.append(movie_details)
                # 每获取一部电影后立即保存数据
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = os.path.join(data_dir, f'movies_{timestamp}.json')
                save_movie_data(movies_data, filename)
                print(f"数据已保存到 {filename}")
            
            # 避免API请求过于频繁
            time.sleep(0.25)
    
    print("数据采集完成")

if __name__ == '__main__':
    main() 