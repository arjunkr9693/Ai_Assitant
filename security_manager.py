"""
Security manager for Jarvis AI Assistant
Handles all security checks and safe file operations
"""

import os
from config import ALLOWED_DRIVES, BLOCKED_OPERATIONS, SAFE_APPS, BLOCKED_APPS


class SecurityManager:
    @staticmethod
    def is_safe_operation(command):
        """Check if the command contains any blocked operations"""
        command_lower = command.lower()
        for blocked_op in BLOCKED_OPERATIONS:
            if blocked_op in command_lower:
                return False, f"Operation '{blocked_op}' is not allowed for security reasons."
        return True, ""

    @staticmethod
    def is_allowed_path(file_path):
        """Check if the file path is in allowed directories (D: or E: drives only)"""
        if not file_path:
            return False

        # Convert to absolute path and normalize
        try:
            abs_path = os.path.abspath(file_path)
            drive = abs_path[:2].upper()
            return drive in ALLOWED_DRIVES
        except:
            return False

    @staticmethod
    def is_safe_app(app_name):
        """Check if the application is safe to open"""
        normalized_app_name = app_name.lower().strip()

        if normalized_app_name in BLOCKED_APPS:
            return False, f"I cannot open {app_name} for security reasons."

        if normalized_app_name in SAFE_APPS:
            return True, SAFE_APPS[normalized_app_name]

        return False, f"I cannot open '{app_name}'. For security, I can only open approved applications like notepad, calculator, chrome, firefox, and media players."


class FileManager:
    """Handles secure file operations"""

    @staticmethod
    def safe_file_operation(operation_type, *args):
        """Safely perform file operations with security checks"""
        try:
            if operation_type == "rename":
                old_path, new_path = args

                # Check if both paths are in allowed directories
                if not SecurityManager.is_allowed_path(old_path):
                    return False, f"Access denied: '{old_path}' is not in allowed directories (D: or E: drives only)."

                if not SecurityManager.is_allowed_path(new_path):
                    return False, f"Access denied: '{new_path}' is not in allowed directories (D: or E: drives only)."

                # Check if source file exists
                if not os.path.exists(old_path):
                    return False, f"File '{old_path}' not found."

                # Check if destination already exists
                if os.path.exists(new_path):
                    return False, f"File '{new_path}' already exists. Cannot rename."

                # Perform rename operation
                os.rename(old_path, new_path)
                return True, f"Successfully renamed '{old_path}' to '{new_path}'."

            elif operation_type == "create":
                file_path, content = args

                # Check if path is in allowed directories
                if not SecurityManager.is_allowed_path(file_path):
                    return False, f"Access denied: '{file_path}' is not in allowed directories (D: or E: drives only)."

                # Check if file already exists
                if os.path.exists(file_path):
                    return False, f"File '{file_path}' already exists. Cannot overwrite existing files."

                # Create new file with content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, f"Successfully created file '{file_path}'."

            elif operation_type == "list":
                directory_path = args[0] if args else "D:\\"

                # Check if directory is in allowed drives
                if not SecurityManager.is_allowed_path(directory_path):
                    return False, f"Access denied: '{directory_path}' is not in allowed directories (D: or E: drives only)."

                # List files in directory
                if os.path.exists(directory_path) and os.path.isdir(directory_path):
                    files = os.listdir(directory_path)
                    return True, f"Files in '{directory_path}': {', '.join(files)}"
                else:
                    return False, f"Directory '{directory_path}' not found or is not a directory."

        except Exception as e:
            return False, f"Error performing {operation_type} operation: {str(e)}"

        return False, "Unknown file operation."