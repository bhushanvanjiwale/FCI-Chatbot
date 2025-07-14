import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class Visualizer:
    def __init__(self):
        pass

    def create_visualization(self, data):
        """Create basic visualizations for the data"""
        if data is None or data.empty:
            st.error("No data available for visualization")
            return
        
        st.subheader("Data Visualizations")
        
        # Show basic info
        st.write("**Data Info:**")
        st.write(f"Shape: {data.shape}")
        st.dataframe(data.head())
        
        # Get numeric columns
        numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_columns:
            # Create histogram for first numeric column
            if len(numeric_columns) > 0:
                st.write("**Histogram:**")
                fig, ax = plt.subplots()
                ax.hist(data[numeric_columns[0]].dropna(), bins=30, alpha=0.7, color='blue')
                ax.set_title(f'Histogram of {numeric_columns[0]}')
                ax.set_xlabel(numeric_columns[0])
                ax.set_ylabel('Frequency')
                st.pyplot(fig)
            
            # Create correlation heatmap if multiple numeric columns
            if len(numeric_columns) > 1:
                st.write("**Correlation Heatmap:**")
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(data[numeric_columns].corr(), annot=True, cmap='coolwarm', ax=ax)
                st.pyplot(fig)
        else:
            st.info("No numeric columns found for visualization")

    def plot_histogram(self, data, column):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(data[column].dropna(), bins=30, alpha=0.7, color='blue')
        ax.set_title(f'Histogram of {column}')
        ax.set_xlabel(column)
        ax.set_ylabel('Frequency')
        ax.grid(axis='y', alpha=0.75)
        st.pyplot(fig)

    def plot_scatter(self, data, x_column, y_column):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(data[x_column], data[y_column], alpha=0.7, color='green')
        ax.set_title(f'Scatter Plot of {x_column} vs {y_column}')
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        ax.grid()
        st.pyplot(fig)

    def plot_box(self, data, column):
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(x=data[column], ax=ax)
        ax.set_title(f'Box Plot of {column}')
        ax.set_xlabel(column)
        st.pyplot(fig)