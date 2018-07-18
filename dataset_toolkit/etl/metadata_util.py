#
# Uber, Inc. (c) 2018
#
""" Script display parquet dataset metadata """

import argparse
from pyarrow import parquet as pq

from dataset_toolkit.etl import dataset_metadata, rowgroup_indexing
from dataset_toolkit.fs_utils import FilesystemResolver

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='metadata utility',
                                     description='Show and manipulate parquet dataset metadata',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dataset-url', type=str,
                        help='the url to the dataset base directory', required=True)
    parser.add_argument('--schema', action='store_true',
                        help='Display schema from metadata')
    parser.add_argument('--index', action='store_true',
                        help='Display list of row group indexes')
    parser.add_argument('--print-values', action='store_true',
                        help='Print index values (dataset piece indexes)')
    parser.add_argument('--skip-index', nargs='+', type=str,
                        help='Donot display indexed values for given fields')

    args = parser.parse_args()

    if args.dataset_url and args.dataset_url[-1] == '/':
        args.dataset_url = args.dataset_url[:-1]

    # Create pyarrow file system
    resolver = FilesystemResolver(args.dataset_url)
    dataset = pq.ParquetDataset(resolver.parsed_dataset_url().path, filesystem=resolver.filesystem(),
                                validate_schema=False)

    all = not args.schema and not args.index
    if args.schema or all:
        print '*** Schema from dataset metadata ***'
        print dataset_metadata.get_schema(dataset)

    if args.index or all:
        index_dict = rowgroup_indexing.get_row_group_indexes(dataset)
        print '*** Row group indexes from dataset metadata ***'
        for index_name in index_dict:
            print 'Index: {}'.format(index_name)
            if args.skip_index is None or index_name not in args.skip_index:
                for field_value in index_dict[index_name].indexed_values:
                    print '  -- {}({})'.format(field_value,
                                               len(index_dict[index_name].get_row_group_indexes(field_value)))
                    if args.print_values:
                        print index_dict[index_name].get_row_group_indexes(field_value)
            else:
                print '  (skipped)'
