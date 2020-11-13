import argparse
import os
import pickle
import pandas as pd
import numpy as np
from IPython.core.display import display
import matplotlib.pyplot as plt

import missingno as msno

import data_handling_support_functions as sup
import data_visualization_functions as vis


def adapt_features_for_model(features_cleaned1, outcomes_cleaned1, result_dir, conf):


    ## Prepare the Feature Columns

    # === Replace signs for missing values or other values with ===#
    features = features_cleaned1.copy()

    # Custom replacements, replace only if there is something to replace, else it makes NAN of it
    # value_replacements = {
    #    'n': 0,
    #    'y': 1,
    #    'unknown': np.NAN
    # }

    # === Replace all custom values and missing values with content from the value_replacement
    for col in features.columns:
        # df_dig[col] = df[col].map(value_replacements)
        # df_dig[col] = df[col].replace('?', np.nan)

        # Everything to numeric
        features[col] = pd.to_numeric(features[col])
        # df_dig[col] = np.int64(df_dig[col])

    display(features.head(5))

    # Create one-hot-encoding for certain classes and replace the original class
    # onehotlabels = pd.get_dummies(df_dig.iloc[:,1])

    # Add one-hot-encondig columns to the dataset
    # for i, name in enumerate(onehotlabels.columns):
    #    df_dig.insert(i+1, column='Cylinder' + str(name), value=onehotlabels.loc[:,name])

    # Remove the original columns
    # df_dig.drop(columns=['cylinders'], inplace=True)

    ## Prepare the Outcomes

    # Replace classes with digital values
    outcomes = outcomes_cleaned1.copy()
    outcomes = outcomes.astype(int)
    print("Outcome types")
    print(outcomes.dtypes)

    ### Binarize Multiclass Dataset

    # If the binarize setting is used, then binarize the class of the outcome.
    if conf['binarize_labels'] == True:
        binarized_outcome = (outcomes[conf['class_name']] == conf['class_number']).astype(np.int_)
        y = binarized_outcome.values.flatten()
        print("y was binarized. Classes before: {}. Classes after: {}".format(np.unique(outcomes[conf['class_name']]),
                                                                              np.unique(y)))

        # Redefine class labels
        class_labels = {
            0: conf['binary_0_label'],
            1: conf['binary_1_label']
        }

        print("Class labels redefined to: {}".format(class_labels))
    else:
        y = outcomes[conf['class_name']].values.flatten()
        print("No binarization was made. Classes: {}".format(np.unique(y)))

    # y = outcomes[class_name].values.flatten()
    # y_labels = class_labels
    # class_labels_inverse = sup.inverse_dict(class_labels)

    print("y shape: {}".format(y.shape))
    print("y labels: {}".format(class_labels))
    print("y unique classes: {}".format(np.unique(y, axis=0)))

    ## Determine Missing Data
    #Missing data is only visualized here as it is handled in the training algorithm in S40.

    # Check if there are any nulls in the data
    print("Missing data in the features: ", features.isnull().values.sum())
    features[features.isna().any(axis=1)]

    # Missing data part
    print("Number of missing values per feature")
    missingValueShare = []
    for col in features.columns:
        # if is_string_dtype(df_dig[col]):
        missingValueShare.append(sum(features[col].isna()) / features.shape[0])

    # Print missing value graph
    vis.paintBarChartForMissingValues(features.columns, missingValueShare)

    # Visualize missing data with missingno
    #fig = plt.figure(num=None, figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')
    msno.matrix(features)
    plt.gcf()
    plt.savefig(os.path.join(result_dir,'_missing_numbers_matrix'))
    plt.show()

    if features.isnull().values.sum() > 0:
        plt.gcf()
        msno.heatmap(features)
        plt.savefig(os.path.join(result_dir, '_missing_numbers_heatmap'))
        plt.show()

    #### View Prepared Binary Features
    # We need some more plots for the binary data types.

    # vis.plotBinaryValues(df_dig, df_dig.columns) #0:-1
    # plt.savefig(image_save_directory + "/BinaryFeatures.png", dpi=70)

    return features, y, class_labels

def main():
    conf = sup.load_config(args.config_path)

    data_preparation_dump_file_path = os.path.join("tmp", "step31out.pickle")
    (features_cleaned1, outcomes_cleaned1, class_labels,
     data_source_raw, data_directory, result_directory) = pickle.load(open(data_preparation_dump_file_path, "rb" ))

    dataset_name = conf['dataset_name']
    class_name = conf['class_name']

    model_features_filename = data_directory + "/" + dataset_name + "_" + class_name + "_features_for_model" + ".csv"
    model_outcomes_filename = data_directory + "/" + dataset_name + "_" + class_name + "_outcomes_for_model" + ".csv"
    model_labels_filename = data_directory + "/" + dataset_name + "_" + class_name + "_labels_for_model" + ".csv"

    features, y, class_labels = adapt_features_for_model(features_cleaned1, outcomes_cleaned1, result_directory, conf)

    # === Save features to a csv file ===#
    print("Features shape {}".format(features.shape))
    features.to_csv(model_features_filename, sep=';', index=True)
    # np.savetxt(filenameprefix + "_X.csv", X, delimiter=";", fmt='%s')
    print("Saved features to " + model_features_filename)

    # === Save the selected outcome to a csv file ===#
    print("outcome shape {}".format(y.shape))
    y_true = pd.DataFrame(y, columns=[conf['class_name']], index=outcomes_cleaned1.index)
    y_true.to_csv(model_outcomes_filename, sep=';', index=True, header=True)
    print("Saved features to " + model_outcomes_filename)

    # === Save new y labels to a csv file ===#
    print("Class labels length {}".format(len(class_labels)))
    with open(model_labels_filename, 'w') as f:
        for key in class_labels.keys():
            f.write("%s;%s\n" % (class_labels[key],
                                 key))  # Classes are saved inverse to the labelling in the file, i.e. first value, then key
    print("Saved class names and id to " + model_labels_filename)

    #annotations_directory = conf['annotations_directory']

    #if not args.on_inference_data:
    #    data_directory = conf['training_data_directory']
    #    result_directory = conf['result_directory'] + "/analysis_training"
    #else:
    #    data_directory = conf['inference_data_directory']
    #    result_directory = conf['result_directory'] + "/analysis_inference"

    #if not os.path.isdir(result_directory):
    #    os.makedirs(result_directory)
    #    print("Created directory: ", result_directory)

    #data_preparation_dump_file_path = os.path.join("tmp", "step31out.pickle")
    #if not os.path.isdir("tmp"):
    #    os.makedirs("tmp")
    #    print("Created directory: ", "tmp")

    #features_raw, outcomes_cleaned1, data_source_raw, class_labels = load_files(data_directory, conf['dataset_name'], conf['class_name'])
    ## Data Cleanup of Features and Outcomes before Features are Modified
    #features_cleaned1 = clean_features_first_pass(features_raw, class_labels)

    #analyze_raw_data(features_cleaned1, outcomes_cleaned1, result_directory, conf['dataset_name'], conf['class_name'])

    #Save structures for further processing
    # Dump path data
    #dump((features_cleaned1, outcomes_cleaned1, class_labels, data_directory, result_directory), open(data_preparation_dump_file_path, 'wb'))
    #print("Stored paths to: ", data_preparation_dump_file_path)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Step 3.1 - Analyze Data')
    #parser.add_argument("-r", '--retrain_all_data', action='store_true',
    #                    help='Set flag if retraining with all available data shall be performed after ev')
    parser.add_argument("-conf", '--config_path', default="config/debug_timedata_omxS30.json",
                        help='Configuration file path', required=False)
    #parser.add_argument("-i", "--on_inference_data", action='store_true',
    #                    help="Set inference if only inference and no training")

    args = parser.parse_args()

    #if not args.pb and not args.xml:
    #    sys.exit("Please pass either a frozen pb or IR xml/bin model")

    main()


    print("=== Program end ===")