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

         