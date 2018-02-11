import os
import click
import pandas as pd
import http.server
import socketserver
import webbrowser
import base64
import math
from tqdm import tqdm
from PIL import Image
import json

from generic_feature_statistics_generator import GenericFeatureStatisticsGenerator


TEMPLATE_HMTL = 'index_template.html'
INDEX_HTML = 'index.html'
ATLAS_IMAGE_FILENAME = 'atlas.png'


@click.command()
@click.option('--csv', required=True, help='Path to CSV file')
@click.option('--port', default='8080', show_default=True, type=click.IntRange(min=0, max=65535), help='Port')
@click.option('--title', default='Facets csv visualizer', show_default=True, help='Website title')
@click.option('--announcement', default='', help="Announcement printed next to the 'Dive' and 'Overview' tabs")
@click.option('--filter', default='', help='Pandas query applied to the csv file. See https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.query.html')
@click.option('--overview_groupby', default='', help="Category to group-by in Overview")
@click.option('--row_facet', default='', help='Row-based faceting')
@click.option('--column_facet', default='', help='Column-based faceting')
@click.option('--vertical_position', default='', help='Vertical position in scatter mode')
@click.option('--horizontal_position', default='', help='Horizontal position in scatter mode')
@click.option('--color_by', default='', help='Field used to color datapoints')
@click.option('--field_name', default='', help='Datapoint name')
@click.option('--image_column', default='', help='Column with paths to images to load as sprites in facets dive. All images must have the same width and height')
@click.option('--open_browser/--dont_open_browser', default=True, show_default=True, help='Open website when loaded')
def main(**kwargs):
    p = Params(kwargs)
    print('Params:')
    p.pretty_print()
    print()

    df = pd.read_csv(p.csv)

    if len(p.filter) > 0:
        df = df.query(p.filter)

    for field in (p.overview_groupby, p.row_facet, p.column_facet, p.vertical_position, p.horizontal_position, p.color_by, p.field_name, p.image_column):
        if len(field) > 0:
            assert field in df.columns, "Field '{}' not in header of csv file.".format(field)

    use_atlas = False
    if len(p.image_column) > 0:
        use_atlas = True
        atlas, (img_width, img_height) = create_atlas(list(df[p.image_column]))
        df = df.drop(p.image_column, axis='columns')

    print('Summary:')
    print(df.describe())
    print()
    print('First rows:')
    print(df.head())
    print()

    jsonstr = df.to_json(orient='records')

    protostr = create_overview_protostr(df, p.overview_groupby)

    position_mode = 'scatter' if len(p.vertical_position) > 0 or len(p.horizontal_position) > 0 else 'stacked'

    dive_settings = {
        "verticalFacet": p.row_facet,
        "horizontalFacet": p.column_facet,
        "colorBy": p.color_by,
        "imageFieldName": p.field_name,
        "positionMode": position_mode,
        "verticalPosition": p.vertical_position,
        "horizontalPosition": p.horizontal_position,
        "atlasUrl": ATLAS_IMAGE_FILENAME if use_atlas else '',
        "spriteImageWidth": img_width if use_atlas else '',
        "spriteImageHeight": img_height if use_atlas else '',
    }

    with open(TEMPLATE_HMTL) as f:
        html = f.read().format(
            title=p.title, 
            announcement=p.announcement, 
            jsonstr=jsonstr, 
            protostr=protostr,
            dive_settings=dive_settings,
        )
    
    try:
        with open(INDEX_HTML, 'w') as f:
            f.write(html)
        if use_atlas:
            atlas.save(ATLAS_IMAGE_FILENAME)

        url = 'http://localhost:{}/'.format(p.port)

        if p.open_browser:
            webbrowser.open_new_tab(url)

        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", p.port), Handler) as httpd:
            print("Serving at {}".format(url))
            httpd.serve_forever()
    finally:
        os.remove(INDEX_HTML)
        if use_atlas:
            os.remove(ATLAS_IMAGE_FILENAME)


def create_atlas(image_filenames):
    num_images = len(image_filenames)
    size = int(math.ceil(math.sqrt(num_images)))

    first_image = Image.open(image_filenames[0])
    img_width = first_image.width
    img_height = first_image.height

    atlas = Image.new(mode='RGB', size=(size*img_width, size*img_height))

    for i, image_filepath in tqdm(enumerate(image_filenames), desc='Loading images'):
        img = Image.open(image_filepath)

        assert img.width == img_width and img.height == img_height, \
            "All images must have the same width and height. First image dimensions: {}. Image dimensions of '{}': {}" \
            .format((img.width, img.height), image_filepath, (img.width, img.height))

        x = i % size
        y = i // size
        atlas.paste(img, box=(x*img_width, y*img_height))

    return atlas, (img_width, img_height)


def create_overview_protostr(df, groupby):
    gfsg = GenericFeatureStatisticsGenerator()

    if len(groupby) > 0:
        frames_list = [{'name': name, 'table': group} for name, group in df.groupby(groupby)]
    else:
        frames_list = [{'name': 'data', 'table': df}]
    proto = gfsg.ProtoFromDataFrames(frames_list)
    protostr = base64.b64encode(proto.SerializeToString()).decode("utf-8")

    return protostr


class Params:
    """
    Simple wrapper class for dictionaries to make each key accessible as an attribute.

    >>> p = Params({'a': 1, 'b': 2})
    >>> print(p.a, p.b)
    ... 1 2
    """

    def __init__(self, params_dict):
            self.__dict__ = params_dict

    def __repr__(self):
        classname = self.__class__.__name__
        return '{}[{}]'.format(classname, self.__dict__)

    def pretty_print(self):
        extra_space = 2

        keys = self.__dict__.keys()
        max_length = max(len(str(key)) for key in keys)

        for key in sorted(keys):
            row = ''
            row += str(key)
            row += ' ' * ((max_length - len(key)) + extra_space)

            value = self.__dict__[key]
            if len(str(value)) > 0:
                row += '{} [{}]'.format(value, type(value).__name__)
            else:
                row += '[{}]'.format(type(value).__name__)

            print(row)


if __name__ == '__main__':
    main()
