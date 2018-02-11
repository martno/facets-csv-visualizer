# facets-csv-visualizer
Simple wrapper around Facets (https://pair-code.github.io/facets/) to visualize csv files


# Installation
```
pip3 install -r requirements.txt
```


# Usage
```
python3 facets_csv_visualizer.py --help

Usage: facets_csv_visualizer.py [OPTIONS]

Options:
  --csv TEXT                      Path to CSV file  [required]
  --port INTEGER RANGE            Port  [default: 8080]
  --title TEXT                    Website title  [default: Facets csv
                                  visualizer]
  --announcement TEXT             Announcement printed next to the 'Dive' and
                                  'Overview' tabs
  --filter TEXT                   Pandas query applied to the csv file. See
                                  https://pandas.pydata.org/pandas-docs/stable
                                  /generated/pandas.DataFrame.query.html
  --overview_groupby TEXT         Category to group-by in Overview
  --row_facet TEXT                Row-based faceting
  --column_facet TEXT             Column-based faceting
  --vertical_position TEXT        Vertical position in scatter mode
  --horizontal_position TEXT      Horizontal position in scatter mode
  --color_by TEXT                 Field used to color datapoints
  --field_name TEXT               Datapoint name
  --image_column TEXT             Column with paths to images to load as
                                  sprites in facets dive. All images must have
                                  the same width and height
  --open_browser / --dont_open_browser
                                  Open website when loaded  [default: True]
  --help                          Show this message and exit.  ```
```

## Examples

`python3 facets_csv_explorer.py --csv=iris.csv`

`python3 facets_csv_explorer.py --csv=iris.csv --title=Iris --overview_groupby=species --color_by=species`

