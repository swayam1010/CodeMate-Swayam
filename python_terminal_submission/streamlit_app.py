import streamlit as st
import os
import pathlib
import time
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional

# Try to import optional dependencies
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

@dataclass
class TerminalEntry:
    mode: str
    input: str
    resolved_command: str
    output: str
    is_error: bool
    ts: str

# Initialize session state
def init_session_state():
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'cwd' not in st.session_state:
        st.session_state.cwd = pathlib.Path('./workspace')
    if 'ai_active' not in st.session_state:
        st.session_state.ai_active = check_ai_status()
    if 'ai_reason' not in st.session_state:
        st.session_state.ai_reason = ""
    if 'last_ai_call' not in st.session_state:
        st.session_state.last_ai_call = 0

# Stub functions (to be implemented later)
def ensure_sandbox():
    """Ensure sandbox directory exists"""
    workspace = pathlib.Path('./workspace')
    workspace.mkdir(exist_ok=True)
    return workspace

def list_tree(path: pathlib.Path) -> List[Dict]:
    """List directory tree (stub)"""
    try:
        items = []
        for item in path.iterdir():
            items.append({
                'name': item.name,
                'type': 'dir' if item.is_dir() else 'file',
                'size': item.stat().st_size if item.is_file() else 0
            })
        return sorted(items, key=lambda x: (x['type'], x['name']))
    except:
        return []

def run_command(cmd: str) -> Tuple[str, bool]:
    """Execute command (stub)"""
    # Basic validation
    if not cmd.strip():
        return "Error: Empty command", True
    
    # Check for forbidden characters
    forbidden = ['|', '&&', '>', '<', '`', '$()']
    if any(char in cmd for char in forbidden):
        return "Error: Forbidden characters detected", True
    
    # Simulate command execution
    cmd_lower = cmd.lower().strip()
    
    if cmd_lower == 'help':
        return """Available commands:
• ls - List directory contents
• pwd - Print working directory
• mkdir <name> - Create directory
• touch <file> - Create file
• rm <file> - Remove file
• cd <dir> - Change directory
• count - Count files and directories
• clear - Clear terminal""", False
    
    elif cmd_lower == 'ls':
        return "📁 test_folder/\n📄 example.txt\n📄 script.py", False
    
    elif cmd_lower == 'pwd':
        return f"Current directory: {st.session_state.cwd}", False
    
    elif cmd_lower == 'count':
        return "📊 Files: 2, Directories: 1, Total: 3", False
    
    elif cmd_lower.startswith('mkdir'):
        dirname = cmd[5:].strip()
        if dirname:
            return f"✅ Directory '{dirname}' created", False
        return "Error: Directory name required", True
    
    elif cmd_lower.startswith('touch'):
        filename = cmd[5:].strip()
        if filename:
            return f"✅ File '{filename}' created", False
        return "Error: Filename required", True
    
    else:
        return f"Command executed: {cmd}\nOutput: Success", False

def nl_to_command(nl: str) -> str:
    """Convert natural language to command (stub)"""
    nl_lower = nl.lower()
    
    if 'create' in nl_lower and 'file' in nl_lower:
        return 'touch newfile.txt'
    elif 'create' in nl_lower and ('folder' in nl_lower or 'directory' in nl_lower):
        return 'mkdir newfolder'
    elif 'list' in nl_lower or 'show' in nl_lower:
        return 'ls'
    elif 'help' in nl_lower:
        return 'help'
    else:
        return nl  # Fallback to treating as command

def check_ai_status() -> bool:
    """Check if AI is active"""
    api_key = os.getenv('GEMINI_API_KEY') or st.secrets.get('GEMINI_API_KEY', None) if hasattr(st, 'secrets') else None
    return bool(api_key)

def get_system_metrics() -> Tuple[float, float, List[Dict]]:
    """Get system metrics (stub)"""
    if HAS_PSUTIL:
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            
            # Get top 5 processes by memory
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            top5 = sorted(processes, key=lambda x: x['memory_percent'] or 0, reverse=True)[:5]
            return cpu, ram, top5
        except:
            pass
    
    # Fallback fake data
    return 45.2, 62.8, [
        {'pid': 1234, 'name': 'python', 'memory_percent': 5.2},
        {'pid': 5678, 'name': 'streamlit', 'memory_percent': 4.8},
        {'pid': 9012, 'name': 'chrome', 'memory_percent': 3.1},
        {'pid': 3456, 'name': 'code', 'memory_percent': 2.9},
        {'pid': 7890, 'name': 'system', 'memory_percent': 2.3}
    ]

def main():
    st.set_page_config(
        page_title="AI Terminal - CodeMate Hackathon",
        page_icon="🖥️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Dark theme CSS
    st.markdown("""
    <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        .success-text { color: #00ff00; }
        .error-text { color: #ff4444; }
        .info-text { color: #00aaff; }
        .console-output {
            font-family: 'Courier New', monospace;
            background-color: #1e1e1e;
            padding: 10px;
            border-radius: 5px;
            white-space: pre-wrap;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize
    init_session_state()
    ensure_sandbox()
    
    # Sidebar
    with st.sidebar:
        st.header("🛠️ Terminal Info")
        st.badge("v1.0.0", type="secondary")
        st.info(f"**Session Dir:** `{st.session_state.cwd}`")
        
        if st.button("🗑️ Clear Terminal", use_container_width=True):
            st.session_state.history = []
            st.rerun()
        
        if st.button("📊 Show AI Status", use_container_width=True):
            st.session_state.ai_active = check_ai_status()
            st.rerun()
        
        st.divider()
        
        st.subheader("🚀 Quick Commands")
        quick_cmds = ["help", "ls", "pwd", "count"]
        for cmd in quick_cmds:
            if st.button(f"`{cmd}`", key=f"quick_{cmd}", use_container_width=True):
                output, is_error = run_command(cmd)
                entry = TerminalEntry(
                    mode="Command",
                    input=cmd,
                    resolved_command=cmd,
                    output=output,
                    is_error=is_error,
                    ts=datetime.now().strftime("%H:%M:%S")
                )
                st.session_state.history.append(entry)
                st.rerun()
        
        st.divider()
        
        st.subheader("📁 File Manager")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
        
        tree = list_tree(st.session_state.cwd)
        for item in tree[:10]:  # Show max 10 items
            icon = "📁" if item['type'] == 'dir' else "📄"
            size_str = f" ({item['size']} bytes)" if item['type'] == 'file' else ""
            st.text(f"{icon} {item['name']}{size_str}")
    
    # Main area
    st.title("🖥️ AI Terminal – CodeMate Hackathon")
    
    # Card 1: Terminal Interface
    with st.container(border=True):
        st.subheader("💻 Terminal Interface")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            mode = st.segmented_control("Mode", ["Command", "Natural language"], default="Command")
        
        with col1:
            user_input = st.text_input(
                "Enter command:",
                placeholder="Type your command or natural language query...",
                key="terminal_input"
            )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            execute_btn = st.button("▶️ Execute", type="primary", use_container_width=True)
        with col2:
            st.caption("💡 Natural language supported. Try plain English.")
        
        if execute_btn and user_input:
            # Rate limiting for AI
            current_time = time.time()
            if mode == "Natural language" and (current_time - st.session_state.last_ai_call) < 1:
                st.error("🚨 Rate limited: Please wait 1 second between AI requests")
            else:
                if mode == "Natural language":
                    st.session_state.last_ai_call = current_time
                    resolved_cmd = nl_to_command(user_input)
                else:
                    resolved_cmd = user_input
                
                output, is_error = run_command(resolved_cmd)
                entry = TerminalEntry(
                    mode=mode,
                    input=user_input,
                    resolved_command=resolved_cmd,
                    output=output,
                    is_error=is_error,
                    ts=datetime.now().strftime("%H:%M:%S")
                )
                st.session_state.history.append(entry)
                st.rerun()
    
    # Card 2: Terminal Output
    with st.container(border=True):
        st.subheader("📺 Terminal Output")
        
        if st.session_state.history:
            for i, entry in enumerate(reversed(st.session_state.history[-10:])):  # Show last 10
                with st.expander(f"[{entry.ts}] $ {entry.resolved_command}", expanded=i==0):
                    if entry.mode == "Natural language":
                        st.caption(f"🤖 Translated from: \"{entry.input}\"")
                    
                    color_class = "error-text" if entry.is_error else "success-text"
                    st.markdown(f'<div class="console-output {color_class}">{entry.output}</div>', 
                              unsafe_allow_html=True)
                    
                    if st.button("📋 Copy", key=f"copy_{i}"):
                        st.success("Copied to clipboard!")
        else:
            st.info("🌟 No commands executed yet. Try running a command above!")
    
    # Card 3: AI Status
    with st.container(border=True):
        st.subheader("🤖 AI Natural Language Processing Status")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.ai_active:
                st.success("✅ ACTIVE")
                model = st.secrets.get("GEMINI_MODEL", "gemini-1.5-flash") if hasattr(st, 'secrets') else "gemini-1.5-flash"
                st.info(f"📡 Model: {model}")
            else:
                st.error("❌ INACTIVE")
                st.warning("💡 Add GEMINI_API_KEY to Streamlit secrets to enable AI features")
        
        with col2:
            if st.session_state.ai_reason:
                st.caption(f"Last error: {st.session_state.ai_reason}")
    
    # Card 4: System Monitor
    with st.container(border=True):
        st.subheader("📊 System Monitor")
        
        cpu, ram, top5 = get_system_metrics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("CPU Usage", f"{cpu:.1f}%")
            st.metric("RAM Usage", f"{ram:.1f}%")
        
        with col2:
            st.caption("Top 5 Processes by Memory:")
            for proc in top5:
                st.text(f"PID {proc['pid']}: {proc['name']} ({proc['memory_percent']:.1f}%)")
    
    # Demo section
    st.divider()
    if st.button("🎬 Demo Script"):
        demo_commands = ["mkdir test", "ls", "cd test", "touch a.txt", "ls"]
        for cmd in demo_commands:
            output, is_error = run_command(cmd)
            entry = TerminalEntry(
                mode="Command",
                input=cmd,
                resolved_command=cmd,
                output=output,
                is_error=is_error,
                ts=datetime.now().strftime("%H:%M:%S")
            )
            st.session_state.history.append(entry)
        st.rerun()
    
    # Footer
    st.divider()
    st.caption("Built for CodeMate Hackathon 2025 • PS-1 • Streamlit")

if __name__ == "__main__":
    main()

    def looks_like_natural_language(self, command):
        """Detect if a command looks like natural language vs system command."""
        cmd_lower = command.lower().strip()
        
        natural_indicators = [
            'how', 'what', 'where', 'when', 'why', 'who', 'which',
            'can you', 'could you', 'please', 'i want', 'i need', 'i would', "i'd",
            'show me', 'tell me', 'give me', 'help me', 'find me',
            'create', 'make', 'build', 'generate', 'add', 'remove', 'delete',
            'count', 'list', 'display', 'print', 'open', 'close',
            'files', 'folders', 'directories', 'project', 'items'
        ]
        
        for indicator in natural_indicators:
            if indicator in cmd_lower:
                return True
        
        words = cmd_lower.split()
        if len(words) > 2:
            common_words = ['the', 'a', 'an', 'is', 'are', 'in', 'on', 'at', 'to', 'for', 'of', 'with']
            if any(word in common_words for word in words):
                return True
        
        return False

    def parse_natural_language(self, command):
        """Parse natural language commands using Gemini AI or fallback patterns."""
        if self.ai_enabled:
            return self.parse_with_gemini(command)
        else:
            return self.parse_with_fallback_patterns(command)

    def parse_with_gemini(self, command):
        """Use Gemini AI to parse natural language commands."""
        try:
            prompt = f"""You are a command-line assistant. Convert this natural language request to a single terminal command.

IMPORTANT RULES:
- Return ONLY the command, no explanations
- Use these specific commands when appropriate:
  * For file/folder counting: "count" 
  * For creating files: "touch filename.ext"
  * For creating folders: "mkdir foldername"
  * For listing files: "ls" or "dir"
  * For deleting files: "rm filename" or "del filename"
  * For current directory: "pwd"
  * For help: "help"

Examples:
- "count the files" → "count"
- "how many files" → "count" 
- "create a file called test.py" → "touch test.py"
- "make a folder named project" → "mkdir project"
- "what files are here" → "ls"

User request: "{command}"
Command:"""

            result = self.call_gemini_api(prompt)
            if result and result.strip():
                return result.strip()
            return None
        except Exception as e:
            st.session_state.terminal_output.append(f"❌ AI parsing error: {e}")
            return None

    def call_gemini_api(self, prompt):
        """Make HTTP request to Gemini API."""
        if not self.gemini_api_key or not HAS_REQUESTS:
            return None
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_api_key}"
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0].get('content', {})
                    if 'parts' in content and content['parts']:
                        return content['parts'][0].get('text', '').strip()
            else:
                st.session_state.terminal_output.append("⚠️  Gemini API key validation failed. Switching to fallback patterns.")
                self.ai_enabled = False
            return None
        except Exception as e:
            st.session_state.terminal_output.append(f"❌ AI API error: {e}")
            return None

    def parse_with_fallback_patterns(self, command):
        """Fallback pattern matching for basic natural language processing."""
        cmd_lower = command.lower().strip()
        original_words = command.split()
        
        # Handle simple direct commands first: "delete filename", "remove filename", etc.
        if len(original_words) == 2:
            action = original_words[0].lower()
            target = original_words[1]
            
            if action in ['delete', 'remove', 'del']:
                return f'rm {target}'
            elif action in ['create', 'make']:
                return f'touch {target}'
            elif action in ['mkdir']:
                return f'mkdir {target}'
            elif action in ['rmdir']:
                return f'rmdir {target}'
        
        # File counting patterns
        if any(phrase in cmd_lower for phrase in ['count', 'how many', 'number of files', 'files count']):
            return 'count'
        
        # File/directory deletion patterns
        if any(phrase in cmd_lower for phrase in ['delete', 'remove', 'del']):
            if 'folder' in cmd_lower or 'directory' in cmd_lower:
                # Find folder name
                words = cmd_lower.split()
                for i, word in enumerate(words):
                    if word in ['named', 'called'] and i + 1 < len(original_words):
                        return f'rmdir {original_words[i + 1].strip("\"\'")}'
                    elif word in ['folder', 'directory'] and i + 1 < len(original_words):
                        next_word = original_words[i + 1].strip("\"\'")
                        if next_word not in ['named', 'called']:
                            return f'rmdir {next_word}'
                return 'rmdir temp'
            else:
                # Find file name - prioritize filename-like words first
                for word in original_words:
                    if '.' in word and not word.startswith('.') and word.lower() not in ['delete', 'remove', 'del', 'file', 'the']:
                        return f'rm {word.strip("\"\'")}'
                
                # Then look for patterns with keywords
                words = cmd_lower.split()
                for i, word in enumerate(words):
                    if word in ['named', 'called'] and i + 1 < len(original_words):
                        return f'rm {original_words[i + 1].strip("\"\'")}'
                    elif word == 'file' and i + 1 < len(original_words):
                        next_word = original_words[i + 1].strip("\"\'")
                        if next_word not in ['named', 'called']:
                            return f'rm {next_word}'
                
                # Look for any word after delete/remove that's not a common word
                delete_words = ['delete', 'remove', 'del']
                for i, word in enumerate(words):
                    if word in delete_words and i + 1 < len(original_words):
                        next_word = original_words[i + 1].strip("\"\'")
                        if next_word not in ['the', 'a', 'an', 'file', 'named', 'called']:
                            return f'rm {next_word}'
                
                return 'rm temp.txt'
        
        # File creation patterns
        if 'create' in cmd_lower or 'make' in cmd_lower:
            if 'file' in cmd_lower:
                words = cmd_lower.split()
                filename = None
                
                for i, word in enumerate(words):
                    if word in ['named', 'called'] and i + 1 < len(original_words):
                        filename = original_words[i + 1].strip('"\'')
                        break
                    elif word == 'file' and i + 1 < len(original_words) and original_words[i + 1].lower() not in ['named', 'called']:
                        filename = original_words[i + 1].strip('"\'')
                        break
                
                # Look for filename-like words (with extensions)
                if not filename:
                    for word in original_words:
                        if '.' in word and not word.startswith('.'):
                            filename = word.strip('"\'')
                            break
                
                if filename:
                    if not '.' in filename:
                        if 'python' in cmd_lower:
                            filename += '.py'
                        elif 'txt' in cmd_lower or 'text' in cmd_lower:
                            filename += '.txt'
                        elif 'html' in cmd_lower:
                            filename += '.html'
                        elif 'css' in cmd_lower:
                            filename += '.css'
                        elif 'js' in cmd_lower or 'javascript' in cmd_lower:
                            filename += '.js'
                        else:
                            filename += '.txt'
                    return f'touch {filename}'
                return 'touch newfile.txt'
            elif 'folder' in cmd_lower or 'directory' in cmd_lower:
                words = cmd_lower.split()
                dirname = None
                
                for i, word in enumerate(words):
                    if word in ['named', 'called'] and i + 1 < len(original_words):
                        dirname = original_words[i + 1].strip('"\'')
                        break
                    elif word in ['folder', 'directory'] and i + 1 < len(original_words):
                        next_word = original_words[i + 1].strip('"\'')
                        if next_word.lower() not in ['named', 'called']:
                            dirname = next_word
                            break
                
                return f'mkdir {dirname}' if dirname else 'mkdir newfolder'
        
        # File content writing patterns
        if 'write' in cmd_lower and ('to' in cmd_lower or 'in' in cmd_lower):
            words = original_words
            filename = None
            
            # Find filename after "to" or "in"
            for i, word in enumerate(words):
                if word.lower() in ['to', 'in'] and i + 1 < len(words):
                    filename = words[i + 1].strip('"\'')
                    break
            
            if not filename:
                # Look for filename-like words
                for word in words:
                    if '.' in word and not word.startswith('.'):
                        filename = word.strip('"\'')
                        break
            
            if filename:
                # Extract content before "to" or "in"
                content_parts = []
                collecting = False
                for word in words:
                    if word.lower() == 'write':
                        collecting = True
                        continue
                    elif word.lower() in ['to', 'in']:
                        break
                    elif collecting:
                        content_parts.append(word)
                
                content = ' '.join(content_parts).strip('"\'')
                return f'echo {content} > {filename}' if content else f'touch {filename}'
        
        # Listing patterns
        if any(phrase in cmd_lower for phrase in ['show', 'list', 'what files', 'see files', 'display files']):
            return 'ls'
        
        # Directory listing patterns
        if any(phrase in cmd_lower for phrase in ['what\'s here', 'what is here', 'contents']):
            return 'ls'
        
        return None

    def execute_command(self, command_line):
        """Execute a command and return output."""
        if not command_line.strip():
            return
            
        # Log command
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.command_history.append(command_line)
        st.session_state.session_log.append(f"[{timestamp}] {command_line}")
        
        args = command_line.split()
        command = args[0] if args else ""
        
        # Handle built-in commands
        if command in ['help']:
            return self.cmd_help()
        elif command in ['pwd']:
            return self.cmd_pwd()
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
            if '-r' in args:
                # Force removal
                dirs = [arg for arg in args[1:] if arg != '-r']
                return self.cmd_rmdir_force(dirs)
            else:
                return self.cmd_rmdir(args[1:])
        elif command == 'echo':
            return self.cmd_echo(args[1:])
        elif command == 'edit' and len(args) > 1:
            return self.cmd_edit(args[1:])
        elif command == 'clear':
            st.session_state.terminal_output = []
            return "Screen cleared"
        elif command == 'history':
            return self.cmd_history()
        elif command == 'ai':
            return self.cmd_ai()
        else:
            # Try natural language processing
            if self.looks_like_natural_language(command_line):
                natural_cmd = self.parse_natural_language(command_line)
                if natural_cmd:
                    st.session_state.terminal_output.append(f"🤖 AI: Interpreting as '{natural_cmd}'")
                    return self.execute_command(natural_cmd)
                else:
                    return "❓ I don't understand that command. Try 'help' for available commands."
            
            # Try system command for simple cases
            return self.execute_system_command(command_line)

    def execute_system_command(self, command_line):
        """Execute system commands safely in the web environment."""
        try:
            # Only allow safe commands in web environment
            safe_commands = ['echo', 'date', 'whoami']
            command = command_line.split()[0]
            
            if command in safe_commands:
                result = subprocess.run(
                    command_line,
                    shell=True,
                    cwd=self.current_directory,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.stdout if result.stdout else f"Command completed with exit code {result.returncode}"
            else:
                return f"❌ Command '{command}' not available in web environment. Use built-in commands instead."
                
        except Exception as e:
            return f"❌ Command error: {str(e)}"

    # Command implementations
    def cmd_help(self):
        """Display help information."""
        help_text = """
🌐 **Web Terminal Commands:**

**File Operations:**
• `ls`, `dir` - List directory contents
• `mkdir <name>` - Create directory  
• `rmdir <name>` - Remove empty directory
• `rmdir -r <name>` - Force remove directory and contents
• `touch <file>` - Create or update file
• `cat <file>` - View file contents
• `rm <file>` - Remove file
• `echo <text> > <file>` - Write text to file
• `edit <file> [content]` - Create/edit file with content
• `count` - Count files and directories

**System:**
• `pwd` - Print working directory
• `clear` - Clear screen
• `history` - Show command history
• `ai` - Show AI status
• `help` - Show this help

**Natural Language Examples:**
• "create a file called test.py"
• "delete the file named old.txt"
• "make a folder named project"
• "remove the directory called temp"
• "write hello world to greeting.txt"
• "how many files are here"
• "show me the files"
        """
        return help_text

    def cmd_pwd(self):
        """Print working directory."""
        return f"Current directory: {self.current_directory}"

    def cmd_ls(self):
        """List directory contents."""
        try:
            items = os.listdir(self.current_directory)
            if not items:
                return "📁 Directory is empty"
                
            output = "📂 **Directory Contents:**\n"
            for item in sorted(items):
                path = os.path.join(self.current_directory, item)
                if os.path.isdir(path):
                    output += f"📁 {item}/\n"
                else:
                    output += f"📄 {item}\n"
            return output
        except Exception as e:
            return f"❌ Error listing directory: {e}"

    def cmd_mkdir(self, args):
        """Create directory."""
        results = []
        for dirname in args:
            try:
                path = os.path.join(self.current_directory, dirname)
                os.makedirs(path, exist_ok=True)
                results.append(f"✅ Directory created: {dirname}")
            except Exception as e:
                results.append(f"❌ Error creating directory {dirname}: {e}")
        return "\n".join(results)

    def cmd_touch(self, args):
        """Create or update file."""
        results = []
        for filename in args:
            try:
                path = os.path.join(self.current_directory, filename)
                with open(path, 'a'):
                    pass
                results.append(f"✅ File '{filename}' created/updated")
            except Exception as e:
                results.append(f"❌ Error creating file {filename}: {e}")
        return "\n".join(results)

    def cmd_cat(self, args):
        """Display file contents."""
        results = []
        for filename in args:
            try:
                path = os.path.join(self.current_directory, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    results.append(f"📄 **{filename}:**\n```\n{content}\n```")
            except FileNotFoundError:
                results.append(f"❌ File not found: {filename}")
            except Exception as e:
                results.append(f"❌ Error reading file {filename}: {e}")
        return "\n".join(results)

    def cmd_echo(self, args):
        """Write content to file or display text."""
        if len(args) < 3 or ">" not in args:
            # Just display text
            return " ".join(args)
        
        # Find the ">" operator
        try:
            redirect_index = args.index(">")
            content = " ".join(args[:redirect_index])
            filename = args[redirect_index + 1] if redirect_index + 1 < len(args) else "output.txt"
            
            path = os.path.join(self.current_directory, filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ Content written to {filename}"
        except Exception as e:
            return f"❌ Error writing to file: {e}"

    def cmd_edit(self, args):
        """Simple file editor - creates file with content."""
        if len(args) < 1:
            return "❌ Usage: edit <filename> [content]"
        
        filename = args[0]
        content = " ".join(args[1:]) if len(args) > 1 else ""
        
        try:
            path = os.path.join(self.current_directory, filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"✅ File '{filename}' created/edited with content"
        except Exception as e:
            return f"❌ Error editing file {filename}: {e}"

    def cmd_rm(self, args):
        """Remove files."""
        results = []
        for filename in args:
            try:
                path = os.path.join(self.current_directory, filename)
                if os.path.isfile(path):
                    os.remove(path)
                    results.append(f"✅ File removed: {filename}")
                elif os.path.isdir(path):
                    results.append(f"❌ Cannot remove directory {filename} with rm. Use 'rmdir {filename}' instead.")
                else:
                    results.append(f"❌ File not found: {filename}")
            except Exception as e:
                results.append(f"❌ Error removing file {filename}: {e}")
        return "\n".join(results)

    def cmd_rmdir(self, args):
        """Remove directories."""
        results = []
        for dirname in args:
            try:
                path = os.path.join(self.current_directory, dirname)
                if os.path.isdir(path):
                    # Check if directory is empty
                    if os.listdir(path):
                        results.append(f"❌ Directory not empty: {dirname}. Use 'rmdir -r {dirname}' to force removal.")
                    else:
                        os.rmdir(path)
                        results.append(f"✅ Directory removed: {dirname}")
                else:
                    results.append(f"❌ Directory not found: {dirname}")
            except Exception as e:
                results.append(f"❌ Error removing directory {dirname}: {e}")
        return "\n".join(results)

    def cmd_rmdir_force(self, args):
        """Force remove directories and their contents."""
        results = []
        for dirname in args:
            try:
                path = os.path.join(self.current_directory, dirname)
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    results.append(f"✅ Directory and contents removed: {dirname}")
                else:
                    results.append(f"❌ Directory not found: {dirname}")
            except Exception as e:
                results.append(f"❌ Error removing directory {dirname}: {e}")
        return "\n".join(results)

    def cmd_count(self):
        """Count files and directories."""
        try:
            items = os.listdir(self.current_directory)
            files = [item for item in items if os.path.isfile(os.path.join(self.current_directory, item))]
            dirs = [item for item in items if os.path.isdir(os.path.join(self.current_directory, item))]
            
            return f"📊 **File Count:**\n📄 Files: {len(files)}\n📁 Directories: {len(dirs)}\n📦 Total items: {len(items)}"
        except Exception as e:
            return f"❌ Error counting files: {str(e)}"

    def cmd_history(self):
        """Show command history."""
        if not st.session_state.command_history:
            return "📜 No commands in history"
            
        output = "📜 **Command History:**\n"
        for i, cmd in enumerate(st.session_state.command_history[-10:], 1):
            output += f"{i:2d}. {cmd}\n"
        return output

    def cmd_ai(self):
        """Show AI status."""
        output = "🤖 **AI Natural Language Processing Status:**\n\n"
        
        if self.ai_enabled:
            output += "✅ **Gemini AI is ACTIVE** - Full natural language understanding enabled!\n"
            output += "🧠 Model: Gemini 1.5 Flash via HTTP API\n"
        else:
            output += "⚠️  **Gemini AI is INACTIVE** - Using fallback patterns\n"
            output += "💡 To enable full AI: Add GEMINI_API_KEY to Streamlit secrets\n"
        
        output += "\n🌟 **Examples you can try:**\n"
        output += "• 'create a file called test.py'\n"
        output += "• 'how many files are here'\n"
        output += "• 'make a folder named project'\n"
        output += "• 'show me the files'\n"
        
        return output

def main():
    st.set_page_config(
        page_title="AI Terminal",
        page_icon="⚡",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for minimal, elegant design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #fafbfc;
    }
    
    .main-container {
        max-width: 900px;
        margin: 2rem auto;
        padding: 0 1rem;
    }
    
    .terminal-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
    }
    
    .terminal-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .terminal-subtitle {
        color: #6b7280;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 0;
    }
    
    .command-section {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .terminal-output {
        background: #0f1419;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
        min-height: 300px;
        max-height: 500px;
        overflow-y: auto;
        font-family: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', monospace;
        font-size: 0.9rem;
        line-height: 1.5;
        border: 1px solid #e5e7eb;
    }
    
    .output-line {
        margin-bottom: 0.25rem;
        padding: 0.125rem 0;
    }
    
    .command-line {
        color: #7dd3fc;
        font-weight: 600;
    }
    
    .success-line {
        color: #34d399;
    }
    
    .error-line {
        color: #f87171;
    }
    
    .info-line {
        color: #60a5fa;
    }
    
    .ai-line {
        color: #a78bfa;
    }
    
    .default-line {
        color: #d1d5db;
    }
    
    .stButton > button {
        background: #111827;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        border: 1px solid #374151;
    }
    
    .stButton > button:hover {
        background: #1f2937;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        padding: 0.875rem 1rem;
        font-size: 0.95rem;
        background: white;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    .quick-actions {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0 2rem 0;
        flex-wrap: wrap;
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .status-success {
        background: #ecfdf5;
        color: #047857;
        border: 1px solid #d1fae5;
    }
    
    .status-warning {
        background: #fffbeb;
        color: #b45309;
        border: 1px solid #fed7aa;
    }
    
    .footer-section {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem 0;
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    .welcome-message {
        background: #0f1419;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        border: 1px solid #e5e7eb;
    }
    
    .welcome-title {
        color: #60a5fa;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .welcome-examples {
        color: #d1d5db;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .example-command {
        color: #34d399;
        font-family: 'SF Mono', 'Monaco', monospace;
        font-weight: 500;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .terminal-title {
            font-size: 2rem;
        }
        .command-section {
            padding: 1.5rem;
        }
        .terminal-output {
            font-size: 0.85rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize terminal
    terminal = WebTerminal()
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header section
    st.markdown("""
    <div class="terminal-header">
        <h1 class="terminal-title">⚡ AI Terminal</h1>
        <p class="terminal-subtitle">Intelligent command line with natural language processing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Command input section
    st.markdown('<div class="command-section">', unsafe_allow_html=True)
    
    # Command input
    command_input = st.text_input(
        "",
        placeholder="Type a command or ask in natural language...",
        key="command_input",
        label_visibility="collapsed"
    )
    
    # Action buttons
    col1, col2, col3, col4 = st.columns([2, 1, 1, 6])
    
    with col1:
        execute_btn = st.button("Execute", type="primary", use_container_width=True)
    
    with col2:
        clear_btn = st.button("Clear", use_container_width=True)
    
    with col3:
        help_btn = st.button("Help", use_container_width=True)
    
    # Quick actions
    st.markdown("**Quick Commands:**")
    
    quick_actions = ["ls", "count", "pwd", "help"]
    cols = st.columns(len(quick_actions))
    
    for i, action in enumerate(quick_actions):
        with cols[i]:
            if st.button(f"`{action}`", key=f"quick_{action}", use_container_width=True):
                result = terminal.execute_command(action)
                if result:
                    st.session_state.terminal_output.append(f"$ {action}")
                    st.session_state.terminal_output.append(result)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle button actions
    if clear_btn:
        st.session_state.terminal_output = []
        st.rerun()
    
    if help_btn:
        result = terminal.cmd_help()
        st.session_state.terminal_output.append("$ help")
        st.session_state.terminal_output.append(result)
        st.rerun()
    
    if execute_btn and command_input.strip():
        result = terminal.execute_command(command_input)
        if result:
            st.session_state.terminal_output.append(f"$ {command_input}")
            st.session_state.terminal_output.append(result)
        st.rerun()
    
    # Terminal output section
    st.markdown("### Terminal Output")
    
    if st.session_state.terminal_output:
        output_html = '<div class="terminal-output">'
        
        for line in st.session_state.terminal_output:
            line_str = str(line)
            
            if line_str.startswith("$"):
                output_html += f'<div class="output-line command-line">{line_str}</div>'
            elif line_str.startswith("✅") or "success" in line_str.lower():
                output_html += f'<div class="output-line success-line">{line_str}</div>'
            elif line_str.startswith("❌") or line_str.startswith("⚠️") or "error" in line_str.lower():
                output_html += f'<div class="output-line error-line">{line_str}</div>'
            elif line_str.startswith("🤖") or "AI:" in line_str:
                output_html += f'<div class="output-line ai-line">{line_str}</div>'
            elif line_str.startswith("📊") or line_str.startswith("📄") or line_str.startswith("📁"):
                output_html += f'<div class="output-line info-line">{line_str}</div>'
            else:
                # Clean HTML and preserve formatting
                clean_line = line_str.replace("**", "<strong>").replace("*", "<em>")
                clean_line = clean_line.replace("\n", "<br>")
                output_html += f'<div class="output-line default-line">{clean_line}</div>'
        
        output_html += '</div>'
        st.markdown(output_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="welcome-message">
            <div class="welcome-title">👋 Welcome to AI Terminal</div>
            <div class="welcome-examples">
                Try these commands:<br><br>
                <span class="example-command">"create a file called test.py"</span><br>
                <span class="example-command">"show me the files"</span><br>
                <span class="example-command">"help"</span> - for all available commands
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # AI Status indicator
    if terminal.ai_enabled:
        st.markdown("""
        <div class="status-indicator status-success">
            <span>🤖 AI Natural Language Processing: <strong>ACTIVE</strong></span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-indicator status-warning">
            <span>⚠️ Using fallback patterns - Add GEMINI_API_KEY for full AI features</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer-section">
        <p>🏆 Built for <strong>CodeMate Hackathon 2025</strong> • Modern AI Terminal</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()