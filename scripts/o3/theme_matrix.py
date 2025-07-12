"""Theme matrix generator for o3 methodology.

Creates prevalence matrix with conditional formatting as specified by ChatGPT-o3.
"""

import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
from openpyxl import Workbook
from openpyxl.styles import PatternFill
from openpyxl.formatting.rule import ColorScaleRule

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(os.getenv("OUTPUTS_DIR", ROOT / "outputs"))


def create_theme_matrix(merged_csv_path: Path) -> pd.DataFrame:
    """Create theme prevalence matrix from merged tags."""
    if not merged_csv_path.exists():
        print(f"Warning: {merged_csv_path} not found")
        return pd.DataFrame()
    
    # Read merged tags
    df = pd.read_csv(merged_csv_path)
    
    if df.empty:
        return df
    
    # Calculate prevalence for each code (excluding uid column)
    code_columns = [col for col in df.columns if col != 'uid']
    prevalence = {}
    
    for code in code_columns:
        if code in df.columns:
            # Prevalence = percentage of units coded with this code
            prevalence[code] = (df[code].sum() / len(df)) * 100
        else:
            prevalence[code] = 0.0
    
    # Create theme matrix
    theme_matrix = pd.DataFrame([prevalence])
    theme_matrix = theme_matrix.T  # Transpose to get themes as rows
    theme_matrix.columns = ['Prevalence_%']
    theme_matrix = theme_matrix.sort_values('Prevalence_%', ascending=False)
    
    return theme_matrix


def apply_conditional_formatting(workbook: Workbook, sheet_name: str = "Theme_Matrix"):
    """Apply 3-color scale conditional formatting per o3 spec."""
    ws = workbook[sheet_name]
    
    # Find the data range (excluding header)
    data_range = f"B2:B{ws.max_row}"  # Assuming prevalence is in column B
    
    # Create 3-color scale rule
    # Min (white) = 0%, Mid (light orange) = 50%, Max (dark red) = 100%
    color_scale = ColorScaleRule(
        start_type='num', start_value=0, start_color='FFFFFF',  # White
        mid_type='num', mid_value=50, mid_color='FFB366',       # Light orange
        end_type='num', end_value=100, end_color='CC0000'       # Dark red
    )
    
    # Apply the rule
    ws.conditional_formatting.add(data_range, color_scale)


def save_theme_matrix(theme_matrix: pd.DataFrame, transcript_id: str) -> None:
    """Save theme matrix to Excel with conditional formatting."""
    if theme_matrix.empty:
        print(f"No theme matrix to save for {transcript_id}")
        return
    
    # Create Excel file
    output_path = OUTPUT_DIR / f"{transcript_id}_theme_matrix.xlsx"
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        theme_matrix.to_excel(writer, sheet_name='Theme_Matrix', index=True)
        
        # Get the workbook and apply formatting
        workbook = writer.book
        apply_conditional_formatting(workbook)
    
    print(f"Saved theme matrix to {output_path}")
    print(f"Top themes by prevalence:")
    for theme, prevalence in theme_matrix.head(5).iterrows():
        print(f"  {theme}: {prevalence['Prevalence_%']:.1f}%")


def main():
    """Generate theme matrices for all merged tag files."""
    merged_files = list(OUTPUT_DIR.glob("*_tags_merged.csv"))
    
    if not merged_files:
        print(f"No merged tag files found in {OUTPUT_DIR}")
        return
    
    print(f"Found {len(merged_files)} merged tag file(s)")
    
    for merged_file in merged_files:
        transcript_id = merged_file.stem.replace("_tags_merged", "")
        print(f"\nProcessing {transcript_id}...")
        
        theme_matrix = create_theme_matrix(merged_file)
        if not theme_matrix.empty:
            save_theme_matrix(theme_matrix, transcript_id)
    
    print(f"\nAll theme matrices complete. Results in {OUTPUT_DIR}")


if __name__ == "__main__":
    main() 