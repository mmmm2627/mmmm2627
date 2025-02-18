## Predicting Surface Protein Levels from Gene Expression Using Neural Networks  
This project aims to predict surface protein levels based on gene expression data using neural networks. The dataset consists of over 110k samples, where continuous gene expression inputs are used to generate continuous protein level outputs. Two neural network architectures, Multi-Layer Perceptron (MLP) and Convolutional Neural Network (CNN), were implemented to evaluate their predictive performance, with the CNN model achieving the best accuracy (0.936).  

### Project Features  
- **Data Processing**: Handled large-scale gene expression data for training and evaluation.  
- **Neural Network Models**: Implemented both MLP and CNN architectures to predict protein levels.  
- **Performance Optimization**: Applied techniques such as early stopping, learning rate scheduling, and cross-validation to enhance model efficiency and reduce training time by 15%.  
- **Model Evaluation**: Identified CNN as the best-fit model for robust predictions.  

### Dataset  
The dataset consists of gene expression data and corresponding surface protein levels for training and testing, 
generated from `data_subset.ipynb`.
- `subset/` – A subset of the dataset for testing and validation.  
  - `test_cite_inputs_id.feather` – Metadata of test data for the CITEseq dataset.  
  - `test_cite_X.npy` – Test set gene expression data.  
  - `train_cite_inputs_id.feather` – Metadata of training data for the CITEseq dataset.  
  - `train_cite_targets.npy` – Target surface protein levels for training data.  
  - `train_cite_X.npy` – Gene expression input data for training.  

### Model Implementation  
- **Multi-Layer Perceptron (MLP)**: A fully connected feedforward neural network for regression.  
- **Convolutional Neural Network (CNN)**: Adapted for structured feature extraction and prediction.  
