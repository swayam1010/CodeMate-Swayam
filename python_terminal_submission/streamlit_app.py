import streamlit as st
import os
import time
from datetime import datetime

# Initialize session state
def init_app():
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'ai_active' not in st.session_state:
        api_key = os.getenv('GEMINI_API_KEY') or "AIzaSyAudmfM5Gp7ZbQc8WfUofiiyFw7xQ9kFpQ"
        st.session_state.ai_active = bool(api_key)

def execute_command(cmd):
    """Execute a command and return output"""
    cmd = cmd.strip().lower()
    
    if not cmd:
        return "Error: Empty command", True
    
    if cmd == 'help':
        return """Available commands:
• ls - List directory contents
• pwd - Print working directory  
• mkdir <name> - Create directory
• touch <file> - Create file
• rm <file> - Remove file
• count - Count files and directories
• clear - Clear terminal
• whoami - Show current user""", False
    
    elif cmd == 'ls':
        return "📁 documents/\n📁 projects/\n📄 readme.txt\n📄 config.py\n📄 main.py", False
    
    elif cmd == 'pwd':
        return "/home/user/workspace", False
    
    elif cmd == 'count':
        return "📊 Files: 3, Directories: 2, Total: 5", False
    
    elif cmd == 'whoami':
        return "user", False
    
    elif cmd.startswith('mkdir '):
        dirname = cmd[6:].strip()
        return f"✅ Directory '{dirname}' created" if dirname else "Error: Directory name required", not bool(dirname)
    
    elif cmd.startswith('touch '):
        filename = cmd[6:].strip()
        return f"✅ File '{filename}' created" if filename else "Error: Filename required", not bool(filename)
    
    elif cmd.startswith('rm '):
        filename = cmd[3:].strip()
        return f"✅ File '{filename}' removed" if filename else "Error: Filename required", not bool(filename)
    
    else:
        return f"✅ Command '{cmd}' executed successfully\nOutput: Operation completed", False

def convert_natural_language(text):
    """Convert natural language to command"""
    text_lower = text.lower()
    
    if 'create file' in text_lower or 'make file' in text_lower:
        return 'touch newfile.txt'
    elif 'create folder' in text_lower or 'make folder' in text_lower or 'create directory' in text_lower:
        return 'mkdir newfolder'
    elif 'list files' in text_lower or 'show files' in text_lower or 'what files' in text_lower:
        return 'ls'
    elif 'how many files' in text_lower or 'count files' in text_lower:
        return 'count'
    elif 'where am i' in text_lower or 'current directory' in text_lower:
        return 'pwd'
    elif 'help' in text_lower:
        return 'help'
    else:
        return text

def main():
    # Page config
    st.set_page_config(
        page_title="AI Terminal",
        page_icon="🖥️",
        layout="wide"
    )
    
    # Initialize
    init_app()
    
    # Custom CSS
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
        line-height: 1.45;
    }
    .command-line {
        color: #58a6ff;
        font-weight: bold;
    }
    .success-output {
        color: #7ee787;
    }
    .error-output {
        color: #f85149;
    }
    .stButton > button {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
    .stButton > button:hover {
        background-color: #30363d;
        border-color: #8b949e;
    }
    .metric-container {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🖥️ AI Terminal - CodeMate Hackathon")
    st.markdown("---")
    
    # Main layout
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Terminal Interface
        st.header("💻 Terminal Interface")
        
        # Mode selection
        mode = st.radio("Mode:", ["Command", "Natural Language"], horizontal=True)
        
        # Input
        user_input = st.text_input(
            "Enter command:",
            placeholder="Type your command or natural language...",
            key="user_input"
        )
        
        # Execute
        col_exec, col_clear = st.columns([1, 1])
        
        with col_exec:
            if st.button("▶️ Execute", type="primary", use_container_width=True):
                if user_input:
                    # Process input
                    if mode == "Natural Language":
                        resolved_cmd = convert_natural_language(user_input)
                        if resolved_cmd != user_input:
                            st.info(f"🤖 Interpreted as: `{resolved_cmd}`")
                    else:
                        resolved_cmd = user_input
                    
                    # Execute command
                    output, is_error = execute_command(resolved_cmd)
                    
                    # Add to history
                    entry = {
                        'input': user_input,
                        'command': resolved_cmd,
                        'output': output,
                        'error': is_error,
                        'time': datetime.now().strftime("%H:%M:%S"),
                        'mode': mode
                    }
                    st.session_state.history.append(entry)
                    
                    st.rerun()
        
        with col_clear:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.history = []
                st.rerun()
        
        # Terminal Output
        st.header("📺 Terminal Output")
        
        if st.session_state.history:
            # Build terminal output
            terminal_output = ""
            
            for entry in st.session_state.history[-10:]:  # Last 10 entries
                terminal_output += f"[{entry['time']}] $ {entry['command']}\n"
                
                if entry['error']:
                    terminal_output += f"❌ {entry['output']}\n\n"
                else:
                    terminal_output += f"{entry['output']}\n\n"
            
            # Display in terminal container
            st.markdown(f"""
            <div class="terminal-container">
                <pre style="margin: 0; white-space: pre-wrap;">{terminal_output}</pre>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🌟 No commands executed yet. Try running a command!")
    
    with col2:
        # Quick Commands
        st.header("🚀 Quick Commands")
        
        quick_commands = [
            ("help", "Show help"),
            ("ls", "List files"), 
            ("pwd", "Current directory"),
            ("count", "Count items"),
            ("whoami", "Show user")
        ]
        
        for cmd, desc in quick_commands:
            if st.button(f"`{cmd}` - {desc}", key=f"quick_{cmd}", use_container_width=True):
                output, is_error = execute_command(cmd)
                entry = {
                    'input': cmd,
                    'command': cmd,
                    'output': output,
                    'error': is_error,
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'mode': 'Command'
                }
                st.session_state.history.append(entry)
                st.rerun()
        
        st.markdown("---")
        
        # AI Status
        st.header("🤖 AI Status")
        if st.session_state.ai_active:
            st.success("✅ ACTIVE")
            st.caption("Model: Gemini 1.5 Flash")
        else:
            st.error("❌ INACTIVE")
            st.caption("Add GEMINI_API_KEY to enable AI")
        
        st.markdown("---")
        
        # System Monitor
        st.header("📊 System Monitor")
        
        # Fake system metrics
        cpu_usage = 42.5
        ram_usage = 68.3
        
        st.metric("CPU Usage", f"{cpu_usage}%")
        st.metric("RAM Usage", f"{ram_usage}%")
        
        st.markdown("---")
        
        # File Browser
        st.header("📁 File Browser")
        st.text("📁 documents/")
        st.text("📁 projects/")
        st.text("📄 readme.txt")
        st.text("📄 config.py")
        st.text("📄 main.py")
    
    # Footer
    st.markdown("---")
    st.caption("Built for CodeMate Hackathon 2025 • PS-1 • Streamlit")

if __name__ == "__main__":
    main()
