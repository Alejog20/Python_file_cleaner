import os


class DirectoryCleaner: 

    """
    
    Identify files based on ext, age and size.
    Move files, renames and compresses files
    Define cleaning rules
    Logging
    
    """

    def __init__(self, target_directory=None, archive_base_dir=None):
        """
        Intializes Directory cleaner

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

