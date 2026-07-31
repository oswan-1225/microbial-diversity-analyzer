import argparse
from pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Analyze microbial diversity data across experimental groups.")
    
    parser.add_argument("--input", required=True, help="Path to the input CSV file")
    parser.add_argument("--control", required=True, help="Label of the control group")
    parser.add_argument("--output", default="results", help="Directory to save output files")
    parser.add_argument("--group_col", default="group", help="Name of the column containing the experimental groups")
    parser.add_argument("--index_col", type=int, default=0, help="Index of the column to use as the DataFrame index")
    parser.add_argument("--metrics", nargs="+", default=None, help="List of metrics to calculate (default: species_richness and shannon_diversity)")
    parser.add_argument("--on_missing", choices=["error", "fill_zero", "drop_rows"], default="error", help="How to handle missing data")
    parser.add_argument("--exclude_cols", nargs="+", default=None, help="Additional metadata columns to exclude (not taxa data)")
    parser.add_argument("--no_index_col", action="store_true", help="Pass this if your CSV has no sample-ID index column (all columns are data)")

    args = parser.parse_args()
    

    run_pipeline(
        input_path=args.input,
        control_label=args.control,
        output_dir=args.output,
        group_col=args.group_col,
        metrics=args.metrics,
        on_missing=args.on_missing,
        exclude_cols=args.exclude_cols,
        index_col=None if args.no_index_col else args.index_col,
    )

if __name__ == "__main__":
    main()