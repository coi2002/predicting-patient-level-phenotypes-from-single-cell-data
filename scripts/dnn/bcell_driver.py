# System arguments
import argparse
# data management
import numpy as np
import pandas as pd
# visualization
import matplotlib.pyplot as plt
import seaborn as sns
# flow cytometry libraries
import cytoflow as flow
# user defined functions
import bcell_preprocess as bpreprocess
import bcell_plot as bplot
import bcell_nn as bnn


# read command line flags
parser = argparse.ArgumentParser(description='Run a DNN on cytometry data.')
parser.add_argument('-v', '--verbose', 
                    help='Print information and status to console.',
                    action='store_true')
parser.add_argument('-p', '--plot', 
                    help='Display plots.',
                    action='store_true')
args = parser.parse_args()

# specify data files
marrow_basal_file = 'data/B_cell_data/Marrow1_01_Basal1.fcs'
marrow_bcr_file   = 'data/B_cell_data/Marrow1_06_BCR.fcs'

# using the cytoflow package
basal_tube = flow.Tube(file = marrow_basal_file,
                  conditions = {'bcr' : 0.0})
bcr_tube   = flow.Tube(file=marrow_bcr_file,
                  conditions = {'bcr' : 1.0})

import_op = flow.ImportOp(conditions = {'bcr' : 'float'},
                          tubes = [basal_tube, bcr_tube])


ex = import_op.apply()

# Check channels in the experiment
if args.verbose:
    # print information about the channels in the experiment
    print('\n')
    print('Number of channels: ', len(ex.channels))
    print("Channels in this experiment: \n", ex.channels)
    print('\n')

# Extract cytometry data in pandas database format
cells_df   = bpreprocess.tube_to_df(ex)
if args.verbose:
    # print information about the dataframes with cytometry data
    print('\n')
    print('Information on the cytometry measurement dataframe:')
    print(cells_df.head)
    print(cells_df.dtypes)
    print('\n')

# EDA plots
if args.plot:
    # display a plot showing the count per category
    bplot.value_count_plot(cells_df).plot(kind = 'bar')
    plt.title("Cell Count by Category")
    plt.xlabel("BCR Stimulated/Unstimulated")
    plt.ylabel("Number of Cells")
    plt.show(block=True)

# Format data as tensorslicedataset
cyto_dataset = bpreprocess.df_to_train_tensor(cells_df)
if args.verbose:
    # print information on the cell data tensors
    print('\n')
    print('Tensor Dataset:\t', cyto_dataset)
    for feat, targ in cyto_dataset.take(5):
        print('Information on the cytometry measurement tensors:')
        print('Tensor shape:\t', feat.shape)
        print('Features: {}, Target: {}'.format(feat, targ))
        print('\n')

# Initialize DNN model with tensors
bcell_nn = bnn.define_model()
bcell_nn.fit(cyto_dataset, epochs=15)