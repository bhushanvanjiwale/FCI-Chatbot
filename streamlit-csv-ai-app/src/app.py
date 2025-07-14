import streamlit as st
import pandas as pd
from components.csv_handler import load_csv, summarize_data
from components.mysql_handler import MySQLHandler
from components.ai_processor import AIProcessor
from components.visualizer import Visualizer
from utils.error_handler import handle_error
from utils.logger import app_logger

def main():
    st.title("🤖 AI-Powered Data Chat Assistant")
    
    # Sidebar for settings
    with st.sidebar:
        st.subheader("⚙️ Settings")
        
        # Check OpenAI availability
        try:
            from utils.security import load_api_key, test_api_key
            api_key = load_api_key()
            
            # Test the API key
            test_result = test_api_key(api_key)
            if test_result == True:
                st.success("✅ OpenAI Connected & Working")
                openai_available = True
            else:
                st.error("❌ OpenAI API Key Invalid")
                openai_available = False
        except Exception as e:
            st.error("❌ OpenAI Configuration Error")
            openai_available = False
        
        if not openai_available:
            st.markdown("### 🔧 Fix API Key Issue:")
            st.markdown("""
            1. **Get a valid API key:**
               - Go to: https://platform.openai.com/api-keys
            2. **Update your config.json**
            3. **Restart the application**
            """)
            st.stop()

        # Advanced settings
        with st.expander("Advanced Settings"):
            show_code = st.checkbox("Show Generated Code", value=False)
            show_debug = st.checkbox("Show Debug Info", value=False)
    
    # Data source selection
    st.subheader("📊 Choose Your Data Source")
    data_source = st.radio(
        "Select data source:",
        ["Upload CSV File", "Connect to MySQL Database"],
        horizontal=True
    )
    
    data = None
    
    if data_source == "Upload CSV File":
        # CSV file upload section
        uploaded_file = st.file_uploader("📂 Upload your CSV file", type=["csv"])
        
        if uploaded_file is not None:
            try:
                with st.spinner("🔄 Loading your data..."):
                    data = load_csv(uploaded_file)
                
                if data is not None:
                    st.success(f"✅ CSV loaded successfully!")
                    display_data_info(data, uploaded_file.size)
            except Exception as e:
                st.error("❌ Something went wrong while processing your file.")
                if show_debug:
                    st.exception(e)
    
    elif data_source == "Connect to MySQL Database":
        # MySQL connection section
        st.subheader("🗄️ MySQL Database Connection")
        
        # Initialize session state for MySQL connection
        if "mysql_connected" not in st.session_state:
            st.session_state.mysql_connected = False
        if "mysql_data" not in st.session_state:
            st.session_state.mysql_data = None
        if "selected_table_name" not in st.session_state:
            st.session_state.selected_table_name = None
        
        # Initialize MySQL handler only once
        if "mysql_handler" not in st.session_state:
            st.session_state.mysql_handler = MySQLHandler()
        
        mysql_handler = st.session_state.mysql_handler
        
        # Show connection status
        if st.session_state.mysql_connected:
            st.success("🟢 Connected to MySQL Database")
            
            # If we have data loaded, use it
            if st.session_state.mysql_data is not None:
                data = st.session_state.mysql_data
                st.success(f"✅ Using data from table: {st.session_state.selected_table_name}")
                display_data_info(data)
            else:
                # Show table selection
                tables = mysql_handler.get_tables()
                
                if tables:
                    st.subheader("📋 Available Tables")
                    selected_table = st.selectbox("Choose a table to analyze:", tables, key="table_selector")
                    
                    if selected_table:
                        # Show table info
                        table_info = mysql_handler.get_table_info(selected_table)
                        if table_info:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("📊 Total Rows", f"{table_info['row_count']:,}")
                            with col2:
                                st.metric("📋 Columns", len(table_info['columns']))
                            
                            # Show columns
                            with st.expander("👀 Table Structure"):
                                st.write("**Columns:**")
                                for col in table_info['columns']:
                                    st.write(f"• **{col[0]}** ({col[1]})")
                        
                        # Load data button
                        col1, col2 = st.columns(2)
                        with col1:
                            load_limit = st.number_input("Rows to load (max 10000):", min_value=100, max_value=10000, value=1000, key="load_limit")
                        
                        with col2:
                            if st.button("📥 Load Table Data", type="primary", key="load_data_btn"):
                                with st.spinner(f"Loading data from {selected_table}..."):
                                    loaded_data = mysql_handler.load_table_data(selected_table, load_limit)
                                    
                                    if loaded_data is not None:
                                        # Store data in session state
                                        st.session_state.mysql_data = loaded_data
                                        st.session_state.selected_table_name = selected_table
                                        data = loaded_data
                                        st.success(f"✅ Loaded {len(data)} rows from {selected_table}")
                                        st.rerun()  # Rerun to show the data interface
                                    else:
                                        st.error("❌ Failed to load table data")
                else:
                    st.warning("No tables found in the database")
        else:
            # Connection form
            with st.form("mysql_connection"):
                col1, col2 = st.columns(2)
                
                with col1:
                    host = st.text_input("Host", value="sql12.freesqldatabase.com", placeholder="sql12.freesqldatabase.com")
                    username = st.text_input("Username", value="sql12790028", placeholder="sql12790028")
                    database = st.text_input("Database Name", value="sql12790028", placeholder="sql12790028")
                
                with col2:
                    port = st.number_input("Port", value=3306, min_value=1, max_value=65535)
                    password = st.text_input("Password", value="P9nfXfxVWk", type="password", placeholder="P9nfXfxVWk")
                
                connect_button = st.form_submit_button("🔗 Connect to Database")
            
            # Handle connection
            if connect_button and all([host, username, password, database]):
                with st.spinner("Connecting to database..."):
                    success, message = mysql_handler.connect_to_mysql(host, username, password, database, port)
                    
                    if success:
                        st.success(message)
                        st.session_state.mysql_connected = True
                        st.rerun()  # Rerun to show table selection
                    else:
                        st.error(message)
                        st.session_state.mysql_connected = False
        
        # Add disconnect button if connected
        if st.session_state.mysql_connected:
            if st.button("🔌 Disconnect from Database", key="disconnect_btn"):
                mysql_handler.close_connection()
                st.session_state.mysql_connected = False
                st.session_state.mysql_data = None
                st.session_state.selected_table_name = None
                st.success("Disconnected from database")
                st.rerun()
    
    # Chat interface (only show if data is loaded)
    if data is not None:
        # Reset messages when switching data sources
        if "current_data_source" not in st.session_state:
            st.session_state.current_data_source = data_source
        elif st.session_state.current_data_source != data_source:
            st.session_state.messages = []  # Clear chat when switching data sources
            st.session_state.current_data_source = data_source
        
        # Chat interface
        st.subheader("💬 Chat with your data")
        st.caption("Ask me anything about your data - I can answer questions, create visualizations, and provide insights!")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your data..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analyzing..."):
                    try:
                        # Initialize AI processor
                        ai_processor = AIProcessor()
                        
                        # Process the prompt
                        result = ai_processor.process_prompt(prompt, data)
                        
                        if result["type"] == "conversation":
                            # Display conversational response
                            st.write(result["content"])
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": result["content"]
                            })
                        
                        elif result["type"] == "code":
                            # Show code if requested
                            if show_code:
                                with st.expander("🔍 Generated Code"):
                                    st.code(result["content"], language="python")
                            
                            # Execute code and show results
                            execution_result = ai_processor.execute_code(result["content"], data)
                            
                            if execution_result["success"]:
                                response_msg = "✅ Analysis completed!"
                                st.success(response_msg)
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": response_msg
                                })
                            else:
                                error_msg = f"❌ Execution error: {execution_result['error']}"
                                st.error(error_msg)
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": error_msg
                                })
                        
                        elif result["type"] == "error":
                            st.error(result["content"])
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": result["content"]
                            })
                    
                    except Exception as e:
                        error_msg = f"❌ System error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                        
                        if show_debug:
                            st.exception(e)
        
        # Quick action buttons
        st.subheader("🚀 Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Data Summary", key="summary"):
                summary_prompt = "Give me a comprehensive summary of this dataset including key statistics and insights"
                st.session_state.messages.append({"role": "user", "content": summary_prompt})
                st.rerun()
        
        with col2:
            if st.button("📈 Create Charts", key="charts"):
                chart_prompt = "Create interesting visualizations that best represent this data"
                st.session_state.messages.append({"role": "user", "content": chart_prompt})
                st.rerun()
        
        with col3:
            if st.button("🔍 Find Patterns", key="patterns"):
                pattern_prompt = "What interesting patterns or correlations can you find in this data?"
                st.session_state.messages.append({"role": "user", "content": pattern_prompt})
                st.rerun()
        
        with col4:
            if st.button("🔄 Clear Chat", key="clear"):
                st.session_state.messages = []
                st.rerun()
    
    else:
        st.info("👆 Please upload a CSV file or connect to MySQL database to start analyzing your data!")
        
        # Show example questions
        st.subheader("💡 Example Questions")
        examples = [
            "How many records are in this dataset?",
            "What are the main columns and their types?",
            "Show me the distribution of [column name]",
            "Create a pie chart for [categorical column]",
            "What correlations exist between numeric columns?",
            "Find any missing values in the data",
            "Show me summary statistics",
            "Create a scatter plot of [column1] vs [column2]"
        ]
        
        for example in examples:
            st.write(f"• {example}")

def display_data_info(data, file_size=None):
    """Display data information"""
    # Show basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Rows", f"{data.shape[0]:,}")
    with col2:
        st.metric("📋 Columns", data.shape[1])
    with col3:
        if file_size:
            st.metric("💾 Size", f"{file_size//1024} KB")
        else:
            st.metric("🗄️ Source", "MySQL")
    
    # Show data preview
    with st.expander("👀 Data Preview", expanded=False):
        st.dataframe(data.head(10))
        
        # Quick data insights
        st.subheader("📈 Quick Insights")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Numeric Columns:**")
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                st.write(", ".join(numeric_cols))
            else:
                st.write("None")
        
        with col2:
            st.write("**Categorical Columns:**")
            cat_cols = data.select_dtypes(include=['object']).columns.tolist()
            if cat_cols:
                st.write(", ".join(cat_cols))
            else:
                st.write("None")

if __name__ == "__main__":
    main()