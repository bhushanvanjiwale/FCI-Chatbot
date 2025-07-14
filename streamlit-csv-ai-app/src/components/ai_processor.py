from openai import OpenAI
from utils.security import load_api_key
from utils.logger import app_logger

class AIProcessor:
    def __init__(self):
        try:
            api_key = load_api_key()
            self.client = OpenAI(api_key=api_key)
            app_logger.info("AI Processor initialized with OpenAI", show_in_ui=False)
        except Exception as e:
            app_logger.error(f"Failed to initialize OpenAI client: {str(e)}", show_in_ui=False)
            raise Exception("OpenAI initialization failed")
    
    def process_prompt(self, prompt, dataframe, chat_history=None):
        """Main method to process user prompts"""
        try:
            # Build context from the actual data
            context = self._build_data_context(dataframe)
            
            # Determine if we need code generation or conversation
            if self._needs_code_generation(prompt):
                return self._generate_and_execute_code(prompt, dataframe, context)
            else:
                return self._generate_conversational_response(prompt, dataframe, context)
        except Exception as e:
            app_logger.error(f"Error processing prompt: {str(e)}", show_in_ui=False)
            return {"type": "error", "content": f"I encountered an error: {str(e)}. Please try rephrasing your question."}
    
    def _build_data_context(self, dataframe):
        """Build comprehensive context about the data with actual values"""
        # Get actual data insights
        numeric_cols = dataframe.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = dataframe.select_dtypes(include=['object']).columns.tolist()
        
        # Build context with FULL dataset statistics, not just samples
        context = f"""
        DATASET INFORMATION:
        - Total rows: {dataframe.shape[0]:,}
        - Total columns: {dataframe.shape[1]}
        - Column names: {list(dataframe.columns)}
        - Numeric columns: {numeric_cols}
        - Categorical columns: {categorical_cols}
        
        IMPORTANT: This dataset contains {dataframe.shape[0]:,} rows of data. When calculating totals, sums, or counts, use ALL rows, not just the sample below.
        
        SAMPLE DATA (first 3 rows for reference only):
        {dataframe.head(3).to_string(index=False)}
        
        FULL DATASET STATISTICS:
        """
        
        # Add comprehensive numeric statistics for the FULL dataset
        if numeric_cols:
            context += f"\nNumeric column statistics (ALL {dataframe.shape[0]:,} rows):\n"
            full_stats = dataframe[numeric_cols].describe()
            context += full_stats.to_string()
            
            # Add totals for important columns
            context += f"\n\nCOLUMN TOTALS (sum of all {dataframe.shape[0]:,} rows):\n"
            for col in numeric_cols:
                total = dataframe[col].sum()
                context += f"{col}: {total:,}\n"
        
        # Add categorical value counts for context
        if categorical_cols:
            context += f"\nCategorical column information (ALL {dataframe.shape[0]:,} rows):\n"
            for col in categorical_cols[:3]:  # First 3 categorical columns
                unique_count = dataframe[col].nunique()
                most_common = dataframe[col].mode().iloc[0] if len(dataframe[col].mode()) > 0 else "N/A"
                context += f"{col}: {unique_count} unique values, most common: {most_common}\n"
        
        # Add data quality information
        context += f"\nDATA QUALITY (ALL {dataframe.shape[0]:,} rows):\n"
        missing_info = dataframe.isnull().sum()
        if missing_info.sum() > 0:
            context += "Missing values:\n"
            for col, missing in missing_info.items():
                if missing > 0:
                    context += f"  {col}: {missing} missing ({missing/len(dataframe)*100:.1f}%)\n"
        else:
            context += "No missing values found.\n"
        
        return context
    
    def _needs_code_generation(self, prompt):
        """Determine if prompt needs code generation"""
        code_keywords = [
            'plot', 'chart', 'graph', 'visualize', 'visualization', 'histogram', 
            'pie', 'bar', 'scatter', 'line chart', 'box plot', 'heatmap', 
            'correlation', 'show distribution', 'create', 'make', 'generate', 
            'display chart', 'draw'
        ]
        
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in code_keywords)
    
    def _generate_conversational_response(self, prompt, dataframe, context):
        """Generate intelligent conversational responses about data"""
        
        full_prompt = f"""
        You are an expert data analyst. Answer the user's question about their dataset accurately using the COMPLETE dataset information provided.
        
        {context}
        
        User question: {prompt}
        
        CRITICAL INSTRUCTIONS:
        - The dataset contains {dataframe.shape[0]:,} rows - USE THIS FULL DATASET for calculations
        - The sample data shown above is only for reference - DO NOT calculate totals from just the sample
        - When asked for totals, sums, counts, or statistics, use the FULL DATASET STATISTICS provided above
        - For questions about totals like "total email delivered", refer to the COLUMN TOTALS section
        - Provide accurate numbers based on the complete dataset, not just the 3-row sample
        
        Answer the question accurately using the FULL dataset information:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1000,
                temperature=0.1  # Lower temperature for more accurate responses
            )
            
            content = response.choices[0].message.content.strip()
            return {"type": "conversation", "content": content}
            
        except Exception as e:
            app_logger.error(f"OpenAI API error: {str(e)}", show_in_ui=False)
            return {"type": "error", "content": f"OpenAI API error: {str(e)}. Please check your API key and try again."}
    
    def _generate_and_execute_code(self, prompt, dataframe, context):
        """Generate code for visualizations and data analysis"""
        
        # Add data type information to help AI make better decisions
        dtype_info = {}
        for col in dataframe.columns:
            dtype_info[col] = {
                'type': str(dataframe[col].dtype),
                'sample_values': dataframe[col].dropna().head(3).tolist(),
                'unique_count': dataframe[col].nunique()
            }
        
        code_prompt = f"""
        Generate Python code for data analysis/visualization using the provided dataset.
        
        {context}
        
        DETAILED COLUMN INFORMATION:
        {dtype_info}
        
        User request: {prompt}
        
        CRITICAL REQUIREMENTS:
        - The DataFrame is already loaded and named 'data' - DO NOT read any CSV files
        - ALWAYS use fig, ax = plt.subplots(figsize=(10, 8)) for creating plots
        - ALWAYS end with st.pyplot(fig) - NEVER use plt.show()
        - For pie charts: ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        - For bar charts: ax.bar(x_values, y_values)
        - Include proper titles with ax.set_title()
        - For pie charts of email data, sum the columns first: email_totals = data[['email_sent', 'email_delivered', 'email_read', 'email_undelivered']].sum()
        - Generate ONLY executable Python code, no explanations
        
        EXAMPLE PATTERN:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 8))
        # your analysis code here
        ax.set_title('Your Title')
        st.pyplot(fig)
        
        Generate the code now:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate clean Python code for data visualization. ALWAYS use st.pyplot(fig) instead of plt.show(). Use proper matplotlib syntax with fig, ax = plt.subplots()."},
                    {"role": "user", "content": code_prompt}
                ],
                max_tokens=800,
                temperature=0.1
            )
            
            code = response.choices[0].message.content.strip()
            cleaned_code = self._clean_generated_code(code)
            cleaned_code = self._validate_and_fix_code(cleaned_code)
            
            return {"type": "code", "content": cleaned_code}
            
        except Exception as e:
            app_logger.error(f"Code generation error: {str(e)}", show_in_ui=False)
            return {"type": "error", "content": f"Code generation failed: {str(e)}"}
    
    def _clean_generated_code(self, code):
        """Clean and prepare generated code"""
        # Remove markdown code blocks
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
        
        return code.strip()
    
    def _validate_and_fix_code(self, code):
        """Validate and fix common issues in generated code"""
        lines = code.split('\n')
        fixed_lines = []
        needs_matplotlib_setup = False
        
        # Check if code uses matplotlib but doesn't have proper setup
        code_str = '\n'.join(lines)
        if ('ax.' in code_str or 'plt.' in code_str) and 'fig, ax = plt.subplots' not in code_str:
            needs_matplotlib_setup = True
        
        # Add matplotlib setup if needed
        if needs_matplotlib_setup:
            fixed_lines.append('import matplotlib.pyplot as plt')
            fixed_lines.append('fig, ax = plt.subplots(figsize=(10, 8))')
        
        for line in lines:
            # Skip lines that try to read CSV files
            if any(forbidden in line.lower() for forbidden in ['pd.read_csv', 'read_csv', '.csv']):
                continue
            
            # Skip data assignment lines that don't use the existing data
            if line.strip().startswith('data =') and 'pd.read' in line:
                continue
                
            # Replace any DataFrame creation with reference to existing data
            if 'pd.DataFrame' in line and '=' in line:
                continue
            
            # Fix common variable name issues - replace df with data
            if 'df[' in line or 'df.' in line:
                line = line.replace('df[', 'data[').replace('df.', 'data.')
            
            # Fix matplotlib display issues - replace plt.show() with st.pyplot(fig)
            if 'plt.show()' in line:
                line = line.replace('plt.show()', 'st.pyplot(fig)')
            
            # Skip duplicate matplotlib imports and setups
            if line.strip() == 'import matplotlib.pyplot as plt' and needs_matplotlib_setup:
                continue
            if 'fig, ax = plt.subplots' in line and needs_matplotlib_setup:
                continue
            
            fixed_lines.append(line)
        
        # Ensure st.pyplot(fig) is present if we have matplotlib code
        final_code = '\n'.join(fixed_lines)
        if ('fig, ax = plt.subplots' in final_code or 'ax.' in final_code) and 'st.pyplot' not in final_code:
            fixed_lines.append('st.pyplot(fig)')
        
        return '\n'.join(fixed_lines)

    def execute_code(self, code, dataframe):
        """Execute the generated code safely with better error handling"""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            import numpy as np
            import streamlit as st
            
            # Clear any previous plots
            plt.clf()
            
            local_vars = {
                'data': dataframe, 
                'df': dataframe,  # Add df as alias
                'st': st, 
                'pd': __import__('pandas'),
                'plt': plt, 
                'sns': sns, 
                'np': np
            }
            
            # Execute the code
            exec(code, {'__builtins__': __builtins__}, local_vars)
            return {"success": True, "message": "Analysis completed successfully"}
            
        except Exception as e:
            error_msg = str(e)
            app_logger.error(f"Code execution error: {error_msg}", show_in_ui=False)
            
            # Provide more helpful error messages
            if "could not convert string to float" in error_msg:
                error_msg = "❌ Cannot perform numeric operations on text data. Please specify a numeric column or ask for categorical analysis instead."
            elif "KeyError" in error_msg:
                error_msg = "❌ Column not found. Please check the column name and try again."
            elif "labels' must be of length" in error_msg:
                error_msg = "❌ Chart labeling error. Please try a different visualization approach."
            
            return {"success": False, "error": error_msg}