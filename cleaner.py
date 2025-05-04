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


