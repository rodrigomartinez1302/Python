**File Copy Module**
This module is designed to copy files from a source path to a destination path based on a specified file pattern. The module requires certain files and libraries to function properly.

**Files**
file_params.xlsx: an Excel file with parameters for the file copying process. This file should contain the following fields:

file_pattern: the file pattern to search for in the source path. This can include wildcard characters such as * and ?.
src_path: the path where the source files are located.
dst_path: the path where the copied files will be placed.
config.json: a JSON file with the database configuration. This file should contain the database credentials and other relevant configuration settings.

**Libraries**
The module relies on the following Python libraries:

threading: for running multiple file copying processes simultaneously
glob: for finding files that match the specified file pattern
os: for working with file paths and directory structures
shutil: for copying files from the source path to the destination path
sys: for accessing system-specific parameters and functions
datetime: for working with dates and times
pandas: for reading and writing Excel files
apscheduler: for scheduling file copying tasks
pyodbc: for connecting to a SQL Server database
json: for reading and writing JSON files

**Usage**
To use the module, you will need to provide the required files (file_params.xlsx and config.json) in the same directory as the Python file. You will also need to install the required Python libraries (using pip or another package manager).

Once the dependencies are installed, you can run the module by executing the Python file. The module will search for files in the source path that match the specified file pattern, and will copy them to the destination path. The module can be scheduled to run at regular intervals using the apscheduler library.
