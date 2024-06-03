import json
import mysql.connector
from colored import fg, attr

def connect_to_db():
    try:
        dbconfig = {
            'host': 'localhost',
            'user': 'root',
            'password': 'password',
            'database': 'movies'
        }
        connection = mysql.connector.connect(**dbconfig)
        cursor = connection.cursor(dictionary=True)
        return connection, cursor
    except mysql.connector.Error as err:
        print(f"{fg(1)}Error connecting to MySQL: {err}{attr(0)}")
        return None, None

def create_queries_table(cursor):
    query = """CREATE TABLE IF NOT EXISTS queries (
                query_id INT AUTO_INCREMENT PRIMARY KEY,
                query_text VARCHAR(255) NOT NULL
            );"""
    cursor.execute(query)

    
def record_query(connection, cursor, query):
    try:
        cursor.execute("INSERT INTO queries (query_text) VALUES (%s) ON DUPLICATE KEY UPDATE query_text = %s", (query, query))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"{fg(1)}Error recording query: {err}{attr(0)}")

def get_popular_queries(connection, cursor, limit= 5):
    try:
        cursor.execute("SELECT query_text, COUNT(*) as count FROM queries GROUP BY query_text ORDER BY count DESC LIMIT 5") #групировкой и каунтом подсчитываем уникальные значения
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"{fg(1)}Error fetching popular queries: {err}{attr(0)}")
        return []

def search_by_keyword(connection, cursor, keyword, limit=10, offset=0):
    try:
        query = f"SELECT * FROM movies WHERE title LIKE '%{keyword}%' LIMIT {limit} OFFSET {offset}"
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"{fg(1)}Error searching movies by keyword: {err}{attr(0)}")
        return []
        print(f"{fg(1)}No more movies found!{attr(0)}")
        interrupted = True


def search_by_year(connection, cursor, year, limit=10, offset=0):
    try:
        query = f"SELECT * FROM movies WHERE year = {year} LIMIT {limit} OFFSET {offset}"
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"{fg(1)}Error searching movies by year: {err}{attr(0)}")
        return []
        print(f"{fg(1)}No more movies found!{attr(0)}")
        interrupted = True

def search_by_genre(connection, cursor, genres, limit=10, offset=0):
    try:
        query = f"SELECT * FROM movies WHERE genres LIKE '%{genres}%' LIMIT {limit} OFFSET {offset}"
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"{fg(1)}Error searching movies by genres: {err}{attr(0)}")
        return []
        print(f"{fg(1)}No more movies found!{attr(0)}")
        interrupted = True

def search_by_year_and_genre(connection, cursor, year, genres, limit=10, offset=0):
    try:
        query = f"SELECT * FROM movies WHERE year = {year} AND genres LIKE '%{genres}%' LIMIT {limit} OFFSET {offset}"
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"{fg(1)}Error searching movies by year and genre: {err}{attr(0)}")
        return []
        print(f"{fg(1)}No more movies found!{attr(0)}")
        interrupted = True

def search_by_cast(connection, cursor, cast, limit=10, offset=0):
    try:
        query = "SELECT * FROM movies WHERE cast LIKE %s LIMIT %s OFFSET %s"     # %s заменится на число указывающее смещение
        cursor.execute(query, ('%' + cast + '%', limit, offset))
        result = cursor.fetchall()
        return result
    except mysql.connector.Error as err:
        print(f"{fg(1)}Error searching movies by actor: {err}{attr(0)}")
        return []
        print(f"{fg(1)}No more movies found!{attr(0)}")
        interrupted = True

def search_by_rating(connection, cursor, rating, limit=10, offset=0):
    try:
        query = f"SELECT * FROM movies WHERE rating >= {rating} LIMIT {limit} OFFSET {offset}"
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except ValueError:
        print(f"{fg(1)}Please enter a valid floating point number for rating!{attr(0)}")
        return []
    except mysql.connector.Error as err:
        print(f"{fg(1)}Error searching movies by rating: {err}{attr(0)}")
        return []
        print(f"{fg(1)}No more movies found!{attr(0)}")
        interrupted = True

def main():
    print(f"{fg(3)}Welcome to Movie Search Console App!{attr(0)}")
    connection, cursor = connect_to_db()
    if not connection or not cursor:
        return
    try:
        while True:
            interrupted = False
            print("\n")
            print(f"{fg(4)}Choose search option:{attr(0)}")
            print("1. Search by keyword")
            print("2. Search by year")
            print("3. Search by genres")
            print("4. Search by year and genre")
            print("5. Search by actor")
            print("6. Search by rating")
            print("7. Bring out the most popular queries")
            print("8. Exit")
            choice = input("Enter your choice: ").strip()
            offset = 0   #определения смещения при выполнении поиска. Смещение указывает, с какой строки начинать выборку результатов
            
            if choice == '1':
                keyword = input(f"Enter keyword to search movies:")
                record_query(connection, cursor, f"Search by keyword: {keyword}")  
                while True:
                    movies = search_by_keyword(connection, cursor, keyword, offset=offset)
                    if not movies:
                        print(f"{fg(1)}No more movies found!{attr(0)}")
                        break
                    print("\n")
                    print(f"{fg(2)}Found {len(movies)} movies:{attr(0)}")
                    for movie in movies:
                        print(f"{fg(6)}Title:{attr(0)} {movie['title']}")
                        print(f"{fg(6)}Year:{attr(0)} {movie['year']}")
                        genres = ', '.join(movie['genres'])
                        print(f"{fg(6)}Genre:{attr(0)} {genres}")
                        print(f"{fg(6)}Plot:{attr(0)} {movie['plot']}")
                        print(f"{fg(6)}IMDB rating:{attr(0)} {movie['rating']}")
                        poster_url = movie['poster']
                        if poster_url:
                            print(f"{fg(6)}Poster:{attr(0)} {poster_url}") 
                        else:
                            print(f"{fg(3)}No poster available{attr(0)}") 
                        names_list = json.loads(movie['cast'])  
                        names_string = ", ".join(names_list)   
                        cast_output = f"{fg(6)}Cast:{attr(0)} {names_string}"        
                        print(cast_output)
                        print("\n")
                    offset += 10
                    choice_next = input("Do you want to see more movies? (yes/no): ").strip().lower()
                    interrupted = True   #проверка, было ли выполнено действие пользователя, которое прерывает этот цикл
                    if choice_next != 'yes':
                        break
                        
            elif choice == '2':
                year = input(f"Enter year to search movies:")
                record_query(connection, cursor, f"Search by year: {year}")
                while True:
                    movies = search_by_year(connection, cursor, year, offset=offset)
                    if not movies:
                        print(f"{fg(1)}No more movies found!{attr(0)}")
                        break
                    print("\n")
                    print(f"{fg(2)}Found {len(movies)} movies:{attr(0)}")
                    for movie in movies:
                        print(f"{fg(6)}Title:{attr(0)} {movie['title']}")
                        print(f"{fg(6)}Year:{attr(0)} {movie['year']}")
                        genres = ', '.join(movie['genres'])
                        print(f"{fg(6)}Genre:{attr(0)} {genres}")
                        print(f"{fg(6)}Plot:{attr(0)} {movie['plot']}")
                        print(f"{fg(6)}IMDB rating:{attr(0)} {movie ['rating']}")
                        poster_url = movie['poster']
                        if poster_url:
                            print(f"{fg(6)}Poster:{attr(0)} {poster_url}")  
                        else:
                            print(f"{fg(3)}No poster available{attr(0)}") 
                        names_list = json.loads(movie['cast'])   
                        names_string = ", ".join(names_list)  
                        cast_output = f"{fg(6)}Cast:{attr(0)} {names_string}"       
                        print(cast_output)
                        print("\n")
                    offset += 10
                    choice_next = input("Do you want to see more movies? (yes/no): ").strip().lower()
                    if choice_next != 'yes':
                        interrupted = True
                        break
                        
            elif choice == '3':
                genres = input(f"Enter genre to search movies:")
                record_query(connection, cursor, f"Search by genres: {genres}")
                while True:
                    movies = search_by_genre(connection, cursor, genres, offset=offset)
                    if not movies:
                        print(f"{fg(1)}No more movies found!{attr(0)}")
                        break
                    print("\n")
                    print(f"{fg(2)}Found {len(movies)} movies:{attr(0)}")
                    for movie in movies:
                        print(f"{fg(6)}Title:{attr(0)} {movie['title']}")
                        print(f"{fg(6)}Year:{attr(0)} {movie['year']}")
                        genres = ', '.join(movie['genres'])
                        print(f"{fg(6)}Genre:{attr(0)} {genres}")
                        print(f"{fg(6)}Plot:{attr(0)} {movie['plot']}")
                        print(f"{fg(6)}IMDB rating:{attr(0)} {movie ['rating']}")
                        poster_url = movie['poster']
                        if poster_url:
                            print(f"{fg(6)}Poster:{attr(0)} {poster_url}") 
                        else:
                            print(f"{fg(3)}No poster available{attr(0)}") 
                        names_list = json.loads(movie['cast'])  
                        names_string = ", ".join(names_list)  
                        cast_output = f"{fg(6)}Cast:{attr(0)} {names_string}"         
                        print(cast_output)
                        print("\n")
                    offset += 10
                    choice_next = input("Do you want to see more movies? (yes/no): ").strip().lower()
                    if choice_next != 'yes':
                        interrupted = True
                        break
                        
            elif choice == '4':
                year = input(f"Enter year to search movies:")
                genres = input(f"Enter genre to search movies:")
                record_query(connection, cursor, f"Search by year and genres: {year}, {genres}")
                while True:
                    movies = search_by_year_and_genre(connection, cursor, year, genres, offset=offset)
                    if not movies:
                        print(f"{fg(1)}No more movies found!{attr(0)}")
                        break
                    print("\n")
                    print(f"{fg(2)}Found {len(movies)} movies:{attr(0)}")
                    for movie in movies:
                        print("\n")
                        print(f"{fg(6)}Title:{attr(0)} {movie['title']}")
                        print(f"{fg(6)}Year:{attr(0)} {movie['year']}")
                        genres = ', '.join(movie['genres'])
                        print(f"{fg(6)}Genre:{attr(0)} {genres}")
                        print(f"{fg(6)}Plot:{attr(0)} {movie['plot']}")
                        print(f"{fg(6)}IMDB rating:{attr(0)} {movie ['rating']}")
                        poster_url = movie['poster']
                        if poster_url:
                            print(f"{fg(6)}Poster:{attr(0)} {poster_url}")  
                        else:
                            print(f"{fg(3)}No poster available{attr(0)}") 
                        names_list = json.loads(movie['cast'])   
                        names_string = ", ".join(names_list)   
                        cast_output = f"{fg(6)}Cast:{attr(0)} {names_string}"          
                        print(cast_output)
                        print("\n")
                        offset += 10
                    choice_next = input("Do you want to see more movies? (yes/no): ").strip().lower()
                    if choice_next != 'yes':
                        interrupted = True
                        break

            elif choice == '5':
                actor = input(f"Enter actor name to search movies:")
                record_query(connection, cursor, f"Search by actor: {actor}") 
                while True:
                    movies = search_by_cast(connection, cursor, actor, offset=offset)
                    if not movies:
                        print(f"{fg(1)}No more movies found!{attr(0)}")
                        break
                    print("\n")
                    print(f"{fg(2)}Found {len(movies)}  movies:{attr(0)}")
                    for movie in movies:
                        print(f"{fg(6)}Title:{attr(0)} {movie['title']}")
                        print(f"{fg(6)}Year:{attr(0)} {movie['year']}")
                        genres = ', '.join(movie['genres'])
                        print(f"{fg(6)}Genre:{attr(0)} {genres}")
                        print(f"{fg(6)}Plot:{attr(0)} {movie['plot']}")
                        print(f"{fg(6)}IMDB rating:{attr(0)} {movie ['rating']}")
                        poster_url = movie['poster']
                        if poster_url:
                            print(f"{fg(6)}Poster:{attr(0)} {poster_url}") 
                        else:
                            print(f"{fg(3)}No poster available{attr(0)}") 
                        names_list = json.loads(movie['cast'])   
                        names_string = ", ".join(names_list)   
                        cast_output = f"{fg(6)}Cast:{attr(0)} {names_string}"          
                        print(cast_output)
                        print("\n")
                    offset += 10
                    choice_next = input("Do you want to see more movies? (yes/no): ").strip().lower()
                    interrupted = True
                    if choice_next != 'yes':
                        break

            elif choice == '6':
                rating = input(f"Enter minimum rating to search movies: ")
                record_query(connection, cursor, f"Search by rating: {rating}") 
                while True:
                    movies = search_by_rating(connection, cursor, rating, offset=offset)
                    if not movies:
                        print(f"{fg(1)}No more movies found!{attr(0)}")
                        break
                    print("\n")
                    print(f"{fg(2)}Found {len(movies)} movies:{attr(0)}")
                    for movie in movies:
                        print(f"{fg(6)}Title:{attr(0)} {movie['title']}")
                        print(f"{fg(6)}Year:{attr(0)} {movie['year']}")
                        genres = ', '.join(movie['genres'])
                        print(f"{fg(6)}Genre:{attr(0)} {genres}")
                        print(f"{fg(6)}Plot:{attr(0)} {movie['plot']}")
                        print(f"{fg(6)}IMDB rating:{attr(0)} {movie ['rating']}")
                        poster_url = movie['poster']
                        if poster_url:
                            print(f"{fg(6)}Poster:{attr(0)} {poster_url}")  
                        else:
                            print(f"{fg(3)}No poster available{attr(0)}") 
                        names_list = json.loads(movie['cast'])    
                        names_string = ", ".join(names_list)   
                        cast_output = f"{fg(6)}Cast:{attr(0)} {names_string}"  
                        print(cast_output)
                        print("\n")
                    offset += 10
                    choice_next = input("Do you want to see more movies? (yes/no): ").strip().lower()
                    interrupted = True
                    if choice_next != 'yes':
                        break
            elif choice == '7':
                popular_queries = get_popular_queries(connection, cursor)
                print("\n")
                print("TOP-5 Most frequent queries:")
                for i, query in enumerate(popular_queries, 1):
                    print(f"{i}. {query['query_text']}")
            elif choice == '8':
                print(f"{fg(3)}I hope I was helpful. Enjoy your movies!{attr(0)}")
                break
                
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()