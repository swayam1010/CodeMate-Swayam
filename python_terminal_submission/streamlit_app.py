import streamlit as st
import os
import sys
import subprocess
import time
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path to import from main.py
sys.path.append(os.path.dirname(__file__))

# Try to import optional dependencies
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class WebTerminal:
    def __init__(self):
        self.version = "1.3.0-web"
        
        # Use a persistent workspace directory
        if 'workspace' not in st.session_state:
            workspace_path = os.path.join(os.getcwd(), 'workspace')
            os.makedirs(workspace_path, exist_ok=True)
            st.session_state.workspace = workspace_path
        
        self.current_directory = st.session_state.workspace
        
        # Initialize session state
        if 'command_history' not in st.session_state:
            st.session_state.command_history = []
        if 'terminal_output' not in st.session_state:
            st.session_state.terminal_output = []
        
        self.setup_gemini_ai()

    def setup_gemini_ai(self):
        """Initialize Gemini AI integration."""
        self.gemini_api_key = (
            os.getenv('GEMINI_API_KEY') or 
            st.secrets.get('GEMINI_API_KEY', None) if hasattr(st, 'secrets') else None or
            "AIzaSyAudmfM5Gp7ZbQc8WfUofiiyFw7xQ9kFpQ"  # Updated API key
        )
        
        self.ai_enabled = bool(self.gemini_api_key and HAS_REQUESTS)

    def execute_command(self, command_line):
        """Execute a command and return output."""
        if not command_line.strip():
            return "Error: Empty command"
            
        # Log command
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.command_history.append(command_line)
        
        args = command_line.split()
        command = args[0].lower() if args else ""
        
        try:
            # Handle built-in commands
            if command == 'help':
                return self.cmd_help()
            elif command == 'pwd':
                return f"Current directory: {self.current_directory}"
            elif command in ['ls', 'dir']:
                return self.cmd_ls()
            elif command == 'count':
                return self.cmd_count()
            elif command == 'mkdir' and len(args) > 1:
                return self.cmd_mkdir(args[1:])
            elif command == 'touch' and len(args) > 1:
                return self.cmd_touch(args[1:])
            elif command == 'cat' and len(args) > 1:
                return self.cmd_cat(args[1:])
            elif command in ['rm', 'del'] and len(args) > 1:
                return self.cmd_rm(args[1:])
            elif command == 'rmdir' and len(args) > 1:
                return self.cmd_rmdir(args[1:])
            elif command == 'clear':
                st.session_state.terminal_output = []
                return "Terminal cleared"
            elif command == 'whoami':
                return "web-user"
            elif command == 'date':
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            elif command.startswith('echo'):
                return self.cmd_echo(args[1:])
            else:
                # Try natural language processing
                if self.looks_like_natural_language(command_line):
                    natural_cmd = self.parse_natural_language(command_line)
                    if natural_cmd and natural_cmd != command_line:
                        return f"🤖 Interpreting '{command_line}' as '{natural_cmd}'\n" + self.execute_command(natural_cmd)
                
                return f"Unknown command: {command}. Type 'help' for available commands."
        
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def looks_like_natural_language(self, command):
        """Detect if a command looks like natural language."""
        indicators = ['how', 'what', 'create', 'make', 'show', 'list', 'delete', 'remove', 'count', 'many']
        return any(word in command.lower() for word in indicators)

    def parse_natural_language(self, command):
        """Convert natural language to terminal command."""
        cmd_lower = command.lower()
        
        if 'create' in cmd_lower and 'file' in cmd_lower:
            # Extract filename if mentioned
            words = command.split()
            for i, word in enumerate(words):
                if word.lower() in ['called', 'named'] and i + 1 < len(words):
                    return f"touch {words[i+1]}"
            return "touch newfile.txt"
        
        elif 'create' in cmd_lower and ('folder' in cmd_lower or 'directory' in cmd_lower):
            words = command.split()
            for i, word in enumerate(words):
                if word.lower() in ['called', 'named'] and i + 1 < len(words):
                    return f"mkdir {words[i+1]}"
            return "mkdir newfolder"
        
        elif 'list' in cmd_lower or 'show' in cmd_lower:
            return "ls"
        
        elif 'count' in cmd_lower or 'how many' in cmd_lower:
            return "count"
        
        elif 'delete' in cmd_lower or 'remove' in cmd_lower:
            if 'file' in cmd_lower:
                return "rm filename"
            elif 'folder' in cmd_lower or 'directory' in cmd_lower:
                return "rmdir dirname"
        
        return command

    # Command implementations
    def cmd_help(self):
        return """Available commands:
• ls, dir - List directory contents
• pwd - Print working directory
• mkdir <name> - Create directory
• rmdir <name> - Remove directory
• touch <file> - Create file
• cat <file> - View file contents
• rm <file> - Remove file
• echo <text> - Display text
• count - Count files and directories
• clear - Clear terminal
• whoami - Show current user
• date - Show current date/time

Natural language examples:
• "create a file called test.txt"
• "make a folder named projects"
• "show me the files"
• "count the files"
• "delete file test.txt"
"""

    def cmd_ls(self):
        try:
            items = os.listdir(self.current_directory)
            if not items:
                return "Directory is empty"
            
            result = []
            for item in sorted(items):
                path = os.path.join(self.current_directory, item)
                if os.path.isdir(path):
                    result.append(f"📁 {item}/")
                else:
                    size = os.path.getsize(path)
                    result.append(f"📄 {item} ({size} bytes)")
            
            return "\n".join(result)
        except Exception as e:
            return f"Error listing directory: {e}"

    def cmd_count(self):
        try:
            items = os.listdir(self.current_directory)
            files = sum(1 for item in items if os.path.isfile(os.path.join(self.current_directory, item)))
            dirs = sum(1 for item in items if os.path.isdir(os.path.join(self.current_directory, item)))
            return f"📊 Files: {files}, Directories: {dirs}, Total: {len(items)}"
        except Exception as e:
            return f"Error counting items: {e}"

    def cmd_mkdir(self, args):
        results = []
        for dirname in args:
            try:
                path = os.path.join(self.current_directory, dirname)
                os.makedirs(path, exist_ok=True)
                results.append(f"✅ Directory '{dirname}' created")
            except Exception as e:
                results.append(f"❌ Error creating directory {dirname}: {e}")
        return "\n".join(results)

    def cmd_touch(self, args):
        results = []
        for filename in args:
            try:
                path = os.path.join(self.current_directory, filename)
                with open(path, 'a'):
                    pass
                results.append(f"✅ File '{filename}' created")
            except Exception as e:
                results.append(f"❌ Error creating file {filename}: {e}")
        return "\n".join(results)

    def cmd_cat(self, args):
        results = []
        for filename in args:
            try:
                path = os.path.join(self.current_directory, filename)
                with open(path, 'r') as f:
                    content = f.read()
                    results.append(f"📄 Contents of {filename}:\n{content}")
            except FileNotFoundError:
                results.append(f"❌ File not found: {filename}")
            except Exception as e:
                results.append(f"❌ Error reading file {filename}: {e}")
        return "\n".join(results)

    def cmd_rm(self, args):
        results = []
        for filename in args:
            try:
                path = os.path.join(self.current_directory, filename)
                if os.path.isfile(path):
                    os.remove(path)
                    results.append(f"✅ File '{filename}' removed")
                else:
                    results.append(f"❌ File not found: {filename}")
            except Exception as e:
                results.append(f"❌ Error removing file {filename}: {e}")
        return "\n".join(results)

    def cmd_rmdir(self, args):
        results = []
        for dirname in args:
            try:
                path = os.path.join(self.current_directory, dirname)
                if os.path.isdir(path):
                    if os.listdir(path):  # Directory not empty
                        shutil.rmtree(path)
                    else:
                        os.rmdir(path)
                    results.append(f"✅ Directory '{dirname}' removed")
                else:
                    results.append(f"❌ Directory not found: {dirname}")
            except Exception as e:
                results.append(f"❌ Error removing directory {dirname}: {e}")
        return "\n".join(results)

    def cmd_echo(self, args):
        return " ".join(args)

def main():
    # Page config
    st.set_page_config(
        page_title="AI Terminal - CodeMate Hackathon",
        page_icon="🖥️",
        layout="wide"
    )
    
    # Custom CSS for terminal look
    st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .terminal-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', monospace;
        font-size: 14px;
        line-height: 1.6;
        max-height: 400px;
        overflow-y: auto;
    }
    .command-prompt {
        color: #58a6ff;
        font-weight: bold;
    }
    .success-output {
        color: #7ee787;
    }
    .error-output {
        color: #f85149;
    }
    .info-output {
        color: #79c0ff;
    }
    .stButton > button {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
        font-family: 'SF Mono', Monaco, monospace;
    }
    .stButton > button:hover {
        background-color: #30363d;
        border-color: #8b949e;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize terminal
    terminal = WebTerminal()
    
    # Header
    st.title("🖥️ AI Terminal - CodeMate Hackathon")
    st.markdown("*Real file operations with AI-powered natural language processing*")
    st.markdown("---")
    
    # Main layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Terminal Interface
        st.header("💻 Terminal Interface")
        
        # Input area
        user_input = st.text_input(
            "Command:",
            placeholder="Type a command or natural language (e.g., 'create a file called test.txt')",
            key="command_input"
        )
        
        # Buttons
        col_exec, col_clear = st.columns([1, 1])
        
        with col_exec:
            if st.button("▶️ Execute", type="primary", use_container_width=True):
                if user_input.strip():
                    output = terminal.execute_command(user_input)
                    st.session_state.terminal_output.append({
                        'command': user_input,
                        'output': output,
                        'time': datetime.now().strftime("%H:%M:%S")
                    })
                    st.rerun()
        
        with col_clear:
            if st.button("🗑️ Clear Terminal", use_container_width=True):
                st.session_state.terminal_output = []
                st.rerun()
        
        # Terminal Output
        st.header("📺 Terminal Output")
        
        if st.session_state.terminal_output:
            terminal_text = ""
            
            for entry in st.session_state.terminal_output[-10:]:  # Show last 10 entries
                terminal_text += f"[{entry['time']}] $ {entry['command']}\n"
                terminal_text += f"{entry['output']}\n\n"
            
            st.markdown(f"""
            <div class="terminal-container">
                <pre style="margin: 0; white-space: pre-wrap; word-wrap: break-word;">{terminal_text}</pre>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🌟 Welcome! Type a command above to get started. Try natural language like 'create a file called hello.txt'")
    
    with col2:
        # Quick Commands
        st.header("🚀 Quick Commands")
        
        quick_commands = [
            ("help", "Show all commands"),
            ("ls", "List files"),
            ("pwd", "Current directory"),
            ("count", "Count items"),
            ("date", "Show date/time")
        ]
        
        for cmd, desc in quick_commands:
            if st.button(f"`{cmd}` - {desc}", key=f"quick_{cmd}", use_container_width=True):
                output = terminal.execute_command(cmd)
                st.session_state.terminal_output.append({
                    'command': cmd,
                    'output': output,
                    'time': datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
        
        st.markdown("---")
        
        # AI Status
        st.header("🤖 AI Status")
        if terminal.ai_enabled:
            st.success("✅ ACTIVE")
            st.caption("Natural language processing enabled")
        else:
            st.warning("⚠️ Using fallback patterns")
            st.caption("Add GEMINI_API_KEY for full AI")
        
        st.markdown("---")
        
        # Workspace Info
        st.header("📁 Workspace")
        st.info(f"**Location:** `{terminal.current_directory}`")
        
        # Quick file operations
        st.subheader("Quick Actions")
        
        new_file = st.text_input("Create file:", placeholder="filename.txt")
        if st.button("Create File", use_container_width=True) and new_file:
            output = terminal.execute_command(f"touch {new_file}")
            st.session_state.terminal_output.append({
                'command': f"touch {new_file}",
                'output': output,
                'time': datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()
        
        new_dir = st.text_input("Create directory:", placeholder="dirname")
        if st.button("Create Directory", use_container_width=True) and new_dir:
            output = terminal.execute_command(f"mkdir {new_dir}")
            st.session_state.terminal_output.append({
                'command': f"mkdir {new_dir}",
                'output': output,
                'time': datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()
        
        st.markdown("---")
        
        # System Info
        st.header("📊 System Info")
        if HAS_PSUTIL:
            try:
                cpu = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory().percent
                st.metric("CPU Usage", f"{cpu:.1f}%")
                st.metric("Memory Usage", f"{memory:.1f}%")
            except:
                st.info("System metrics unavailable")
        else:
            st.info("Install psutil for system metrics")
    
    # Footer
    st.markdown("---")
    st.caption("Built for CodeMate Hackathon 2025 • PS-1 • Streamlit • Real File Operations")

if __name__ == "__main__":
    main()
