import os
import sys
import argparse
from cleaner import DirectoryCleaner, DownloadsCleaner

def main():
    
    parser = argparse.ArgumentParser(description='Directory cleaner')
    
    parser.add_argument('--dir', type=str, help='Directory to clean (default: ~/Downloads)')
    parser.add_argument('--archive-dir', type=str, help='Directory to archive (default: DIR/Archived)')
    parser.add_argument('--days', type=int, help='Only process older than ')
    parser.add_argument('--mode', choices=['stats', 'clean'], default='stats', 
                        help='Mode: stats (show stats) or clean')
    parser.add_argument('--downloads', action='store_true', 
                        help='Use default settings for downloads folder')
    
    args = parser.parse_args()
    
    try:
        if args.downloads:
            cleaner = DownloadsCleaner()
            print(f"Using default downloads folder cleaner: {cleaner.target_directory}")
        else:
            cleaner = DirectoryCleaner(
                target_directory=args.dir,
                archive_base_dir=args.archive_dir
            )
            print(f"Cleaning directory: {cleaner.target_directory}")
            print(f"Archiving in: {cleaner.archive_base_dir}")
        
        # Mostrar estadísticas
        stats = cleaner.get_directory_stats()
        print("\n=== Directory stats ===")
        print(f"Total files: {stats['total_files']}")
        print(f"Total size: {stats['total_size_mb']:.2f} MB")
        
        print("\nExtension distribution:")
        for ext, data in stats['by_extension'].items():
            print(f"  {ext}: {data['count']} archivos, {data['size_mb']:.2f} MB")
        
        # Limpiar si se solicita
        if args.mode == 'clean':
            print("\n=== Cleaning initializing ===")
            result = cleaner.clean_directory(older_than_days=args.days)
            
            print("\n=== Cleaning results ===")
            print(f"Processed files: {result['total']}")
            print(f"Archived: {result['archived']}")
            print(f"Deleted: {result['deleted']}")
            print(f"Moved: {result['moved']}")
            print(f"Ignored: {result['ignored']}")
            print(f"Errors: {result['errors']}")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())