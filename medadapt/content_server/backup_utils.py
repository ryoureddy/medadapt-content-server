import os
import sqlite3
import shutil
import datetime
import logging
import json
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("medadapt_backup")

def create_backup(db_path='medadapt_content.db', backup_dir='backups'):
    """
    Create a backup of the SQLite database
    
    Args:
        db_path: Path to the database file
        backup_dir: Directory to store backups
        
    Returns:
        Path to the created backup or None if failed
    """
    try:
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create timestamp for backup filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"medadapt_backup_{timestamp}.db")
        
        logger.info(f"Creating backup of {db_path} to {backup_path}")
        
        # Check if source database exists
        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            return None
        
        # Create backup
        shutil.copy2(db_path, backup_path)
        
        # Verify backup was created successfully
        if os.path.exists(backup_path):
            logger.info(f"Backup created successfully: {backup_path}")
            
            # Create metadata file
            metadata = {
                "original_db": db_path,
                "backup_time": timestamp,
                "backup_size": os.path.getsize(backup_path)
            }
            
            metadata_path = os.path.join(backup_dir, f"medadapt_backup_{timestamp}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=4)
            
            return backup_path
        else:
            logger.error("Backup creation failed")
            return None
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        return None

def restore_backup(backup_path, target_path='medadapt_content.db'):
    """
    Restore database from backup
    
    Args:
        backup_path: Path to the backup file
        target_path: Path where to restore the database
        
    Returns:
        Boolean indicating success or failure
    """
    try:
        logger.info(f"Restoring backup from {backup_path} to {target_path}")
        
        # Check if backup file exists
        if not os.path.exists(backup_path):
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Create temporary copy of current database if it exists
        if os.path.exists(target_path):
            temp_path = f"{target_path}.temp"
            shutil.copy2(target_path, temp_path)
            logger.info(f"Created temporary backup of current database: {temp_path}")
        
        try:
            # Copy backup to target location
            shutil.copy2(backup_path, target_path)
            
            # Verify database integrity
            conn = sqlite3.connect(target_path)
            cursor = conn.cursor()
            
            # Check if essential tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['resources', 'topic_mappings', 'user_documents']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"Restored database missing tables: {', '.join(missing_tables)}")
                # Rollback to original if tables are missing
                if os.path.exists(temp_path):
                    shutil.copy2(temp_path, target_path)
                    logger.info("Rolled back to original database due to validation failure")
                return False
            
            conn.close()
            
            # Remove temporary backup if restoration was successful
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            logger.info("Database restoration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during restoration: {str(e)}")
            
            # Rollback to original
            if os.path.exists(temp_path):
                shutil.copy2(temp_path, target_path)
                logger.info("Rolled back to original database due to error")
                
            return False
            
    except Exception as e:
        logger.error(f"Error restoring backup: {str(e)}")
        return False

def list_backups(backup_dir='backups'):
    """
    List available database backups
    
    Args:
        backup_dir: Directory containing backups
        
    Returns:
        List of dictionaries with backup information
    """
    try:
        if not os.path.exists(backup_dir):
            logger.warning(f"Backup directory not found: {backup_dir}")
            return []
            
        backups = []
        
        # Get all .db files in backup directory
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        
        for file in backup_files:
            file_path = os.path.join(backup_dir, file)
            
            # Get file metadata
            creation_time = os.path.getctime(file_path)
            size = os.path.getsize(file_path)
            
            # Get timestamp from filename
            timestamp = file.replace('medadapt_backup_', '').replace('.db', '')
            
            # Check for metadata file
            metadata_path = os.path.join(backup_dir, file.replace('.db', '.json'))
            metadata = {}
            
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            backups.append({
                'filename': file,
                'path': file_path,
                'timestamp': timestamp,
                'creation_time': creation_time,
                'size': size,
                'metadata': metadata
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['creation_time'], reverse=True)
        
        return backups
        
    except Exception as e:
        logger.error(f"Error listing backups: {str(e)}")
        return []

def schedule_backup(interval_hours=24, db_path='medadapt_content.db', backup_dir='backups', max_backups=10):
    """
    Schedule regular backups at specified intervals
    
    Args:
        interval_hours: Hours between backups
        db_path: Path to the database file
        backup_dir: Directory to store backups
        max_backups: Maximum number of backups to keep
        
    Note: This function blocks and runs indefinitely until interrupted
    """
    logger.info(f"Starting scheduled backups every {interval_hours} hours")
    
    try:
        while True:
            # Create backup
            create_backup(db_path, backup_dir)
            
            # Prune old backups if needed
            backups = list_backups(backup_dir)
            if len(backups) > max_backups:
                # Remove oldest backups
                for backup in backups[max_backups:]:
                    try:
                        os.remove(backup['path'])
                        # Also remove metadata file if it exists
                        metadata_path = backup['path'].replace('.db', '.json')
                        if os.path.exists(metadata_path):
                            os.remove(metadata_path)
                        logger.info(f"Removed old backup: {backup['filename']}")
                    except Exception as e:
                        logger.error(f"Error removing old backup {backup['filename']}: {str(e)}")
            
            # Sleep until next backup
            logger.info(f"Next backup scheduled in {interval_hours} hours")
            time.sleep(interval_hours * 3600)
            
    except KeyboardInterrupt:
        logger.info("Backup scheduling stopped by user")
    except Exception as e:
        logger.error(f"Error in backup scheduling: {str(e)}")

if __name__ == "__main__":
    # When run directly, create a backup
    backup_path = create_backup()
    if backup_path:
        print(f"Backup created: {backup_path}")
    else:
        print("Backup creation failed") 