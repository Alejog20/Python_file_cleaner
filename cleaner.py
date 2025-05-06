import os
import shutil
import time
import datetime
import logging
from pathlib import Path
import re


class DirectoryCleaner: 

    """
    
    Identify files based on ext, age and size.
    Move files, renames and compresses files
    Define cleaning rules
    Logging
    
    """

    def __init__(self, target_directory=None, archive_base_dir=None):
        """
        Intializes DirectoryCleaner

        Args:
            target_directory (str): Directory to be cleaned up, By default is Downloads directory.
            archive_base_dire (str): Based directory where files will be stored, if None
                                    it will create a new Directory 'Archived' in target_directory.
        
        """
        if target_directory is None:
            self.target_directory = os.path.expanduser("~/Downloads")
        else:
            self.target_directory = target_directory


        if archive_base_dir is None:
            self.archive_base_dir = os.path.join(self.target_directory, "Archived")
        else:    
            self.archive_base_dir = archive_base_dir


        #Ensure archive file exists
        os.makedirs(self.archive_base_dir, exist_ok=True)

        #Logging
        self._setup_logging()


        """ Processing Rules"""

        self.rules = [{
            '.csv':'archive',
            '.txt':'archive',
            '.xml':'archive',
            '.pdf':'delete',
            '.xls':'delete',
            '.xlsx':'delete',
        }]

        
        self.name_rules= [{
            'pattern': re.compile(r'EPAY', re.IGNORECASE),
            'action': 'move',
            'destination': os.path.join(self.archive_base_dir, 'EPAY')
        }]

        for rule in self.name_rules:
                if rule['action'] == 'move':
                     os.makedirs(rule['destination'], exist_ok=True)
                     

    def _setup_logging(self):
         """Configures the Class logging system"""
         self.logger = logging.getLogger('DirectoryCleaner')
         self.logger-setLevel(logging.INFO)

         # Logging file handler
         log_dir = os.path.join(self.archive_base_dir, 'logs')
         os.makedirs(log_dir, exist_ok=True)

         log_file = os.path.join(log_dir, f'cleaner_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log')
         file_handler = logging.StreamHandler() 

         console_handler = logging.StreamHandler()

         formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
         file_handler.setFormatter(formatter)
         console_handler.setFormatter(formatter)

         self.logger.addHandler(file_handler)
         self.logger.addHandler(console_handler)


    def add_rule(self, pattern, action, destination=None):
         """
         
         Adds a rule to handle files based on name patterns

         Args:
            pattern (str) : Name pattern on filenames that need to be handled differently
            action(str) : Action to be done ('move','ignore','delete')
            destination (str) : Folder destination (only for action = 'move' )
         
         """

         rule = {
              'pattern': re.compile(pattern, re.IGNORECASE),
              'action' : action
         }

         if action == 'move' and destination:
              rule['destination'] = destination
              os.makedirs(destination, exist_ok=True)
              
         self.name_rules.append(rule)
         self.logger.info(f'Name rule added: {pattern} -> {action}')


    def _get_file_info(self, file_path):
         """
         Gets relevant info on a file

         Args: 
            file_path (str) : File path

        Returns: 
            dict: File info        
         
         """
         try:
              stat_info = os.stat(file_path)

              #Get extension
              _, ext = os.path.splitext(file_path)

              return {
                   'path': file_path,
                   'name': os.path.basename(file_path),
                   'extension': ext.lower(),
                   'size': stat_info.st_size,
                   'modified': datetime.datetime.fromtimestamp(stat_info.st_mtime),
                   'created' : datetime.datetime.fromtimestamp(stat_info.st_ctime)
              }
         
         except Exception as e:
              self.logger.error(f'Error while getting file info {file_path}:{e}')
              return None
              

    def _process_file(self, file_info):
         
         """
         
        Process a file based on the configured rules
         
        Args:
        file_info (dict) : Info on the file

        Returns: 
        str: Action done ('archived','deleted','moved', 'ignored')

        
        """
         for rule in self.name_rules:
            if rule['pattern'].search(file_info['name']):
                if rule['action'] == 'move':
                    self.move_file(file_info, rule['destination'])
                    return 'moved'
                elif rule['action'] === 'delete':
                    self._delete_file(file_info)
                    return 'deleted'
                else:
                    return 'ignored'

        # Verify ext rules

         if file_info['extension'] in self.rules:
            action = self.rules[file_info['extension']]

            if action == 'archive':
                self._archive_file()  
                return 'archived'
            elif action == 'delete':
                self._delete_file(file_info)
                return 'deleted'
            else:  
                return 'ignored'
         else:
            return 'ignored'
            

    def _archive_file(self, file_info):
        """
        Archives a file based on its extension

        Args:
            file_info (dict): File info
        
        """

        ext_dir = os.path.join(self.archive_base_dir, file_info['extension'][1:].upper())
        os.makedirs(ext_dir, exist_ok = True)

        # File destiny
        destination = os.path.join(ext_dir, file_info['name'])

        if os.path.exists(destination):
             bas_name, ext = os.path.splitext(file_info['name'])
             timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
             new_name = f'{base_name}_{timestamp}{ext}'
             destination = os.path.join(ext_dir, new_name)


        try:
            shutil.move(file_info['path'], destination)
            self.logger.info(f'Archived file {file_info['path']} -> {destination}')
        except Exception as e:
            self.logger.error(f'Error while archiving {file_info['path']}: {e}')


    def _move_file(self, file_info, destination):

        """
        Moves a file to a specific destination

        Args:
            file_info (dict) : File information
            destination (str) : Destination directory
        
        """

        dest_path = os.path.join(destination, file_info['name'])

        if os.path.exists(dest_path):
            base_name, ext = os.path.splitext(file_info['name'])
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{base_name}_{timestamp}{ext}"
            dest_path = os.path.join(destination, new_name)
        
        # Mover el archivo
        try:
            shutil.move(file_info["path"], dest_path)
            self.logger.info(f"Archivo movido: {file_info['path']} -> {dest_path}")
        except Exception as e:
            self.logger.error(f"Error al mover {file_info['path']}: {e}")
    
    def _delete_file(self, file_info):
        """
        Elimina un archivo.
        
        Args:
            file_info (dict): Información del archivo
        """
        try:
            os.remove(file_info["path"])
            self.logger.info(f"Archivo eliminado: {file_info['path']}")
        except Exception as e:
            self.logger.error(f"Error al eliminar {file_info['path']}: {e}")
    
    def clean_directory(self, older_than_days=None):
        """
        Limpia el directorio objetivo según las reglas configuradas.
        
        Args:
            older_than_days (int, optional): Solo procesar archivos más antiguos 
                                            que este número de días
        
        Returns:
            dict: Estadísticas de la operación
        """
        self.logger.info(f"Iniciando limpieza de {self.target_directory}")
        
        stats = {
            "total": 0,
            "archived": 0,
            "deleted": 0,
            "moved": 0,
            "ignored": 0,
            "errors": 0
        }
        
        cutoff_date = None
        if older_than_days is not None:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=older_than_days)
            self.logger.info(f"Procesando solo archivos anteriores a {cutoff_date}")
        
        # Procesar cada archivo en el directorio
        for filename in os.listdir(self.target_directory):
            try:
                file_path = os.path.join(self.target_directory, filename)
                
                # Ignorar directorios
                if os.path.isdir(file_path):
                    continue
                
                # Obtener información del archivo
                file_info = self._get_file_info(file_path)
                if file_info is None:
                    stats["errors"] += 1
                    continue
                
                stats["total"] += 1
                
                # Verificar antigüedad si corresponde
                if cutoff_date and file_info["modified"] > cutoff_date:
                    stats["ignored"] += 1
                    continue
                
                # Procesar archivo
                result = self._process_file(file_info)
                stats[result] += 1
                
            except Exception as e:
                self.logger.error(f"Error procesando {filename}: {e}")
                stats["errors"] += 1
        
        # Registrar estadísticas
        self.logger.info(f"Limpieza completada. Estadísticas: {stats}")
        return stats
    
    def get_directory_stats(self, directory=None):
        """
        Obtiene estadísticas del directorio.
        
        Args:
            directory (str, optional): Directorio a analizar. 
                                      Si es None, se usa target_directory.
                                      
        Returns:
            dict: Estadísticas del directorio
        """
        if directory is None:
            directory = self.target_directory
            
        stats = {
            "total_files": 0,
            "total_size": 0,
            "by_extension": {}
        }
        
        # Procesar cada archivo en el directorio
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            # Ignorar directorios
            if os.path.isdir(file_path):
                continue
                
            # Obtener información del archivo
            file_info = self._get_file_info(file_path)
            if file_info is None:
                continue
                
            stats["total_files"] += 1
            stats["total_size"] += file_info["size"]
            
            # Contar por extensión
            ext = file_info["extension"]
            if ext not in stats["by_extension"]:
                stats["by_extension"][ext] = {
                    "count": 0,
                    "size": 0
                }
            
            stats["by_extension"][ext]["count"] += 1
            stats["by_extension"][ext]["size"] += file_info["size"]
        
        # Convertir tamaño a MB
        stats["total_size_mb"] = stats["total_size"] / (1024 * 1024)
        
        for ext in stats["by_extension"]:
            stats["by_extension"][ext]["size_mb"] = stats["by_extension"][ext]["size"] / (1024 * 1024)
            
        return stats

# Clase más específica para la carpeta de descargas
class DownloadsCleaner(DirectoryCleaner):
    """
    Clase especializada para limpiar la carpeta de descargas con configuraciones predefinidas.
    """
    
    def __init__(self):
        """Inicializa el limpiador de descargas con configuraciones predefinidas."""
        super().__init__(target_directory=os.path.expanduser("~/Downloads"))
        
        # Configurar reglas específicas para descargas
        self.rules = {
            ".csv": "archive",
            ".txt": "archive",
            ".xml": "archive",
            ".pdf": "delete",
            ".xls": "delete",
            ".xlsx": "delete",
            ".jpg": "archive",
            ".png": "archive",
            ".exe": "delete",
            ".msi": "delete",
            ".zip": "archive",
            ".rar": "archive"
        }
        
        # Crear carpeta EPAY
        epay_dir = os.path.join(self.archive_base_dir, "EPAY")
        os.makedirs(epay_dir, exist_ok=True)
        
        # Regla para archivos EPAY
        self.add_name_rule(r"EPAY", "move", epay_dir)