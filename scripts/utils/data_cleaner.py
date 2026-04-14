import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, List, Any
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCleaner:
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def clean_tags(self, tags_str: str) -> List[str]:
        #Czyszczenie i parsowanie tagów
        if pd.isna(tags_str) or not tags_str:
            return []
        
        # Rozdzielenie tagów po przecinku i usunięcie białych znaków
        tags = [tag.strip() for tag in str(tags_str).split(',')]
        # Filtrowanie pustych tagów
        tags = [tag for tag in tags if tag]
        return tags
    
    def clean_text(self, text: str) -> str:
        """Czyszczenie tekstu"""
        if pd.isna(text):
            return ""
        
        text = str(text).strip()
        # Usunięcie zbędnych białych znaków
        text = ' '.join(text.split())
        return text
    
    def extract_genre_from_tags(self, tags: List[str]) -> List[str]:
        """Ekstrakcja gatunków z tagów"""
        # Lista znanych gatunków
        known_genres = {
            'action', 'adventure', 'animation', 'biography', 'comedy', 'crime',
            'documentary', 'drama', 'family', 'fantasy', 'film-noir', 'history',
            'horror', 'music', 'musical', 'mystery', 'romance', 'sci-fi',
            'short', 'sport', 'thriller', 'war', 'western', 'gothic', 'cult'
        }
        
        genres = [tag for tag in tags if tag.lower() in known_genres]
        return genres if genres else ['unknown']
    
    def process_movie(self, imdb_id: str, row: pd.Series) -> Dict[str, Any]:
        """Przetwarzanie pojedynczego wiersza do formatu JSON"""
        
        # Czyszczenie danych
        imdb_id = str(imdb_id).strip()
        title = self.clean_text(row['title'])
        plot_synopsis = self.clean_text(row['plot_synopsis'])
        tags = self.clean_tags(row['tags'])
        genres = self.extract_genre_from_tags(tags)
        
        # Walidacja
        if not imdb_id or not title or not plot_synopsis:
            logger.warning(f"Pominięcie wiersza z brakującymi danymi: {imdb_id}")
            return None
        
        movie_data = {
            'imdb_id': imdb_id,
            'title': title,
            'plot_synopsis': plot_synopsis,
            'tags': tags,
            'genres': genres,
            'synopsis_source': str(row.get('synopsis_source', 'unknown')).strip(),
            'review': self.clean_text(row.get('review', '')) if 'review' in row else '',
            'split': str(row.get('split', 'train')).strip()
        }
        
        return movie_data
    
    def process_csv(self, csv_file: str, output_file: str) -> int:
        """Przetwarzanie pliku CSV do JSON"""
        
        logger.info(f"Czytanie pliku: {csv_file}")
        df = pd.read_csv(csv_file, index_col=0)
        
        logger.info(f"Liczba rekordów: {len(df)}")
        
        movies = []
        skipped = 0
        
        for imdb_id, row in df.iterrows():
            movie_data = self.process_movie(imdb_id, row)
            if movie_data:
                movies.append(movie_data)
            else:
                skipped += 1
        
        logger.info(f"Przetworzono: {len(movies)}, pominięto: {skipped}")
        
        # Zapis do JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Zapisano do: {output_file}")
        return len(movies)
    
    def process_all(self):
        """Przetwarzanie wszystkich plików CSV"""
        
        csv_files = [
            ('mpst_train.csv', 'movies_train.json'),
            ('mpst_validation.csv', 'movies_validation.json'),
            ('mpst_test.csv', 'movies_test.json')
        ]
        
        total_movies = 0
        
        for csv_file, output_file in csv_files:
            input_path = self.input_dir / csv_file
            output_path = self.output_dir / output_file
            
            if input_path.exists():
                count = self.process_csv(str(input_path), str(output_path))
                total_movies += count
            else:
                logger.warning(f"Plik nie znaleziony: {input_path}")
        
        # Połączenie wszystkich filmów w jeden plik
        all_movies = []
        for _, output_file in csv_files:
            output_path = self.output_dir / output_file
            if output_path.exists():
                with open(output_path, 'r', encoding='utf-8') as f:
                    all_movies.extend(json.load(f))
        
        combined_file = self.output_dir / 'movies_all.json'
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(all_movies, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Razem przetworzono filmów: {total_movies}")
        logger.info(f"Połączony plik: {combined_file}")
        
        # Statystyki
        self.print_statistics(all_movies)
    
    def print_statistics(self, movies: List[Dict]):
        """Wydrukowanie statystyk"""
        
        logger.info("\n=== STATYSTYKI ===")
        logger.info(f"Liczba filmów: {len(movies)}")
        
        # Gatunki
        all_genres = {}
        all_tags = {}
        
        for movie in movies:
            for genre in movie.get('genres', []):
                all_genres[genre] = all_genres.get(genre, 0) + 1
            for tag in movie.get('tags', []):
                all_tags[tag] = all_tags.get(tag, 0) + 1
        
        logger.info(f"\nGatunki ({len(all_genres)}):")
        for genre, count in sorted(all_genres.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {genre}: {count}")
        
        logger.info(f"\nTop tagi ({len(all_tags)}):")
        for tag, count in sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {tag}: {count}")


def download_dataset_from_huggingface(output_dir: Path):
    """Pobieranie datasetu MPST z HuggingFace i zapis do CSV"""
    
    try:
        from datasets import load_dataset
    except ImportError:
        logger.error("Pakiet 'datasets' nie jest zainstalowany!")
        logger.error("Zainstaluj: pip install datasets")
        return False
    
    try:
        logger.info("Pobieranie datasetu z HuggingFace...")
        logger.info("Dataset: cryptexcode/MPST")
        
        # Pobranie datasetu
        ds = load_dataset("cryptexcode/MPST")
        
        # Zapis każdego split'a do CSV
        for split_name in ds.keys():
            logger.info(f"\nPrzetwarzanie split: {split_name}")
            
            split_data = ds[split_name]
            logger.info(f"Liczba rekordów: {len(split_data)}")
            
            # Konwersja do DataFrame
            df = split_data.to_pandas()
            
            # Zapis do CSV
            csv_filename = f"mpst_{split_name}.csv"
            csv_path = output_dir / csv_filename
            
            df.to_csv(csv_path)
            logger.info(f"✅ Zapisano: {csv_path}")
        
        logger.info("\n✅ Dataset został pomyślnie pobrany!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Błąd podczas pobierania datasetu: {e}")
        return False


if __name__ == '__main__':
    # Ścieżki względne - względem bieżącego katalogu
    # Jeśli skrypt jest w scripts/utils/, to parent.parent da nam główny folder projektu
    script_dir = Path(__file__).resolve().parent  # scripts/utils/
    project_root = script_dir.parent.parent  # Główny folder projektu
    
    input_dir = project_root / 'data' / 'raw'
    output_dir = project_root / 'data' / 'processed'
    
    # Tworzenie folderów jeśli nie istnieją
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Folder wejściowy: {input_dir}")
    logger.info(f"Folder wyjściowy: {output_dir}")
    
    # Sprawdzenie czy pliki CSV już istnieją
    csv_files = ['mpst_train.csv', 'mpst_validation.csv', 'mpst_test.csv']
    csv_exists = all((input_dir / f).exists() for f in csv_files)
    
    if not csv_exists:
        logger.info("\n⏳ Pliki CSV nie znalezione. Pobieranie z HuggingFace...")
        success = download_dataset_from_huggingface(input_dir)
        if not success:
            logger.error("Nie udało się pobrać datasetu. Zakończenie.")
            exit(1)
    else:
        logger.info("✅ Pliki CSV już istnieją. Pomijanie pobierania.")
    
    # Przetwarzanie
    logger.info("\n⏳ Czyszczenie i transformacja danych...")
    cleaner = DataCleaner(str(input_dir), str(output_dir))
    cleaner.process_all()
    
    logger.info("\n✅ Gotowe!")
